# @Author: Zeta Syanthis <zetasyanthis>
# @Date:   2017/07/21
# @Email:  zeta@zetasyanthis.org
# @Project: MyArchive
# @Last modified by:   zetasyanthis
# @Last modified time: 2017/07/21
# @License MIT

#
# Load favorites for a Twitter user and output them to a file.
#

import csv
import logging
import os
import sys
import time

from collections import namedtuple
from sqlalchemy.orm.exc import NoResultFound
from time import sleep

from myarchive.db.tag_db.tables import Memory, Service, Tag, User
from myarchive.libs import twitter
from myarchive.libs.twitter import TwitterError

LOGGER = logging.getLogger(__name__)


USER = "USER"
FAVORITES = "FAVORITES"

KEYS = [
    u'user',
    u'text',
    u'in_reply_to_screen_name',
    u'media',

    # Not that interesting, but saved.
    u'hashtags',
    u'id',
    u'in_reply_to_status_id',
    # Seems to be empty a lot. Put it at the end.
    u'urls',

    # Don't really care about these.
    # u'user_mentions',
    # u'source',
    # u'created_at',
    # u'id_str',
    # u'place',
    # u'in_reply_to_user_id',
    # u'lang',
    # u'possibly_sensitive',
    # u'favorited',
    # u'favorite_count',
    # u'retweeted',
    # u'retweet_count',
]


CSVTweet = namedtuple(
    'CSVTweet',
    ["id",
     "username",
     "in_reply_to_status_id",
     "in_reply_to_user_id",
     "timestamp",
     "text",
     "retweeted_status_id",
     "retweeted_status_user_id",
     "retweeted_status_timestamp",
     "expanded_urls"]
)


class TwitterAPI(twitter.Api):
    """API with an extra call."""

    def __init__(self, **kwargs):
        super(TwitterAPI, self).__init__(sleep_on_rate_limit=True, **kwargs)

    def LookupStatuses(self, status_ids, trim_user=False,
                       include_entities=True):
        """
        Returns up to 100 status messages, specified by a list passed to
        status_ids.

        Args:
          status_ids:
            A list of numeric IDs of the statuses you are trying to retrieve.
          trim_user:
            When set to True, each tweet returned in a timeline will include
            a user object including only the status authors numerical ID.
            Omit this parameter to receive the complete user object. [Optional]
          include_entities:
            If False, the entities node will be disincluded.
            This node offers a variety of metadata about the tweet in a
            discreet structure, including: user_mentions, urls, and
            hashtags. [Optional]
        Returns:
          A twitter.Status instance representing that status message
        """
        url = '%s/statuses/lookup.json' % self.base_url

        parameters = dict()

        if not status_ids or len(status_ids) > 100:
            raise TwitterError(
                "status_ids must be between 1 and 100 in length.")
        # This takes a comma-separated list of up to 100 IDs.
        parameters['id'] = ",".join(status_ids)

        if trim_user:
            parameters['trim_user'] = True
        if include_entities:
            parameters['include_entities'] = True

        resp = self._RequestUrl(url, 'GET', data=parameters)
        data = self._ParseAndCheckTwitter(resp.content.decode('utf-8'))

        # return [twitter.Status.NewFromJsonDict(x) for x in data]
        return data

    def import_tweets(
            self, database, service, username, tweet_storage_path,
            media_storage_path, tweet_type):
        """
        Archives several types of new tweets along with their associated
        content.
        """
        api_user_dict = self.GetUser(screen_name=username).AsDict()
        twitter_user, unused_existing = User.find_or_create(
            db_session=database.session,
            service_id=service.id,
            user_id=api_user_dict["id"],
            username=api_user_dict["screen_name"],
            user_dict=api_user_dict,
        )
        database.session.add(twitter_user)
        database.session.commit()

        # Always start with None to pick up max number of new tweets.
        since_id = None
        start_time = -1
        sleep_time = 0
        max_id = None
        early_termination = False
        request_index = 0
        requests_before_sleeps = 1
        while not early_termination:
            # Twitter rate-limits us. Space this out a bit to avoid a
            # super-long sleep at the end doesn't kill the connection.
            if request_index >= requests_before_sleeps:
                # If we hit the rate limit, download media while we wait.
                duration = time.time() - start_time
                if duration < sleep_time:
                    sleep_duration = sleep_time - duration
                    LOGGER.info(
                        "Sleeping for %s seconds to ease up on rate "
                        "limit...", sleep_duration)
                    sleep(sleep_duration)
            start_time = time.time()
            request_index += 1

            LOGGER.info(
                "Pulling 200 tweets from API starting with ID %s and "
                "ending with ID %s...", since_id, max_id)
            try:
                if tweet_type == FAVORITES:
                    loop_statuses = self.GetFavorites(
                        screen_name=username,
                        count=200,
                        since_id=since_id,
                        max_id=max_id,
                        include_entities=True)
                    # 15 requests per 15 minutes.
                    requests_before_sleeps = 15 - 1
                    sleep_time = 60
                elif tweet_type == USER:
                    loop_statuses = self.GetUserTimeline(
                        screen_name=username,
                        count=200,
                        since_id=since_id,
                        max_id=max_id)
                    # 300 requests per 15 minutes.
                    sleep_time = 3
                    requests_before_sleeps = 300 - 1
            except twitter.error.TwitterError as e:
                # If we overran the rate limit, try again.
                if e.message[0][u'code'] == 88:
                    LOGGER.warning(
                        "Overran rate limit. Sleeping %s seconds in an "
                        "attempt to recover...", sleep_time)
                    request_index = requests_before_sleeps
                    sleep(sleep_time)
                    continue
                raise
            LOGGER.debug(
                "Found %s tweets this iteration...", len(loop_statuses))
            # Check for "We ran out of tweets via this API" termination
            # condition.
            if not loop_statuses:
                break
            # Update our max ID counter.
            max_id = min(
                [int(loop_status.AsDict()["id"])
                 for loop_status in loop_statuses]
            )

            # Format things the way we want and handle max_id changes.
            LOGGER.info("Adding %s tweets to DB...", len(loop_statuses))
            author = None
            for status in loop_statuses:
                status_dict = status.AsDict()
                status_id = int(status_dict["id"])
                # Only really query if we absolutely have to.
                user_dict = status_dict["user"]
                user_id = int(user_dict["id"])
                if author and author.id == user_id:
                    pass
                else:
                    author, unused_existing = User.find_or_create(
                        db_session=database.session,
                        service_id=service.id,
                        user_id=user_id,
                        username=None,
                        user_dict=user_dict,
                    )
                    database.session.add(author)

                # Add the tweet to the DB.
                media_urls_list = list()
                if status_dict.get("media"):
                    media_urls_list = [
                        media_dict["media_url_https"]
                        for media_dict in status_dict["media"]
                    ]
                memory, existing = Memory.find_or_create(
                    db_session=database.session,
                    service_id=service.id,
                    service_uuid=status_id,
                    memory_dict=status_dict,
                )
                if existing is False:
                    if tweet_type == FAVORITES:
                        twitter_user.favorites.append(memory)
                        author.posts.append(memory)
                    elif tweet_type == USER:
                        twitter_user.posts.append(memory)
                    apply_tags_to_tweet(
                        db_session=database.session,
                        tweet=memory,
                        status_dict=status_dict)
            database.session.commit()

    def import_from_csv(self, database, service, tweet_storage_path,
                        csv_filepath, username, media_storage_path):

        api_user_dict = self.GetUser(screen_name=username).AsDict()

        twitter_user, unused_existing = User.find_or_create(
            db_session=database.session,
            service_id=service.id,
            user_id=api_user_dict["id"],
            username=api_user_dict["screen_name"],
            user_dict=api_user_dict,
        )
        database.session.add(twitter_user)
        database.session.commit()

        csv_tweets_by_id = dict()
        LOGGER.debug("Scanning CSV for new tweets...")
        with open(csv_filepath) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                tweet_id = int(row['tweet_id'])
                csv_tweet = CSVTweet(
                    id=tweet_id,
                    username=username,
                    in_reply_to_status_id=row["in_reply_to_status_id"],
                    in_reply_to_user_id=row["in_reply_to_user_id"],
                    timestamp=row["timestamp"],
                    text=row["text"],
                    retweeted_status_id=row["retweeted_status_id"],
                    retweeted_status_user_id=
                    row["retweeted_status_user_id"],
                    retweeted_status_timestamp=
                    row["retweeted_status_timestamp"],
                    expanded_urls=row["expanded_urls"]
                )
                csv_tweets_by_id[tweet_id] = csv_tweet

        csv_ids = list(csv_tweets_by_id.keys())
        num_imports = len(csv_ids)
        LOGGER.info(
            "Attempting API import of %s tweets from on CSV file...",
            num_imports)

        # API allows 60 requests per 15 minutes.
        sleep_time = 15
        requests_before_sleeps = 60 - 1

        api_calls = num_imports / 100
        subsequent_api_calls = api_calls - requests_before_sleeps
        if subsequent_api_calls <= 0:
            # Rough estimate, but we basically won't hit the API limit.
            time_to_complete = api_calls * 2
        else:
            time_to_complete = api_calls * 2 + subsequent_api_calls * sleep_time
        LOGGER.info(
            "Estimated time to complete import: %s seconds.", time_to_complete)

        # Set loop starting values.
        tweet_index = 0
        request_index = 0
        start_time = -1
        sliced_ids = csv_ids[:100]
        while sliced_ids:

            duration = time.time() - start_time
            LOGGER.critical(duration)

            # Sleep to not hit the rate limit.
            # Twitter rate-limits us. Space this out a bit to avoid a
            # super-long sleep at the end doesn't kill the connection.
            if request_index >= requests_before_sleeps:
                duration = time.time() - start_time
                if duration < sleep_time:
                    sleep_duration = sleep_time - duration
                    LOGGER.info(
                        "Sleeping for %s seconds to avoid hitting "
                        "Twitter's API rate limit...", sleep_duration)
                    sleep(sleep_duration)
            request_index += 1
            start_time = time.time()

            # Perform the import.
            LOGGER.info(
                "Attempting import of id %s to %s of %s...",
                tweet_index + 1, min(tweet_index + 100, num_imports),
                num_imports)
            try:
                statuses = self.LookupStatuses(
                    status_ids=[str(sliced_id) for sliced_id in sliced_ids],
                    trim_user=False,
                    include_entities=True)
                for status_dict in statuses:
                    status_id = int(status_dict["id"])
                    # media_urls_list = list()
                    # if status_dict.get("media"):
                    #     media_urls_list = [
                    #         media_dict["media_url_https"]
                    #         for media_dict in status_dict["media"]
                    #         ]
                    memory, existing = Memory.find_or_create(
                        db_session=database.session,
                        service_id=service.id,
                        service_uuid=status_id,
                        memory_dict=status_dict,
                    )
                    if existing is False:
                        twitter_user.posts.append(memory)
                        apply_tags_to_tweet(
                            db_session=database.session,
                            tweet=memory,
                            status_dict=status_dict)

                database.session.commit()

            except TwitterError as e:
                # If we overran the rate limit, try again.
                if e.message[0][u'code'] == 88:
                    LOGGER.warning(
                        "Overran rate limit. Sleeping %s seconds in an "
                        "attempt to recover...", sleep_time)
                    request_index = requests_before_sleeps
                    sleep(sleep_time)
                    continue
                database.session.rollback()
                raise
            tweet_index += 100
            sliced_ids = csv_ids[tweet_index:100 + tweet_index]
        database.session.commit()

        LOGGER.info("Parsing out CSV-only tweets...")
        # Refresh existing tweet ID list.
        for tweet_id, csv_only_tweet in csv_tweets_by_id.items():
            memory, existing = Memory.find_or_create(
                db_session=database.session,
                service_id=service.id,
                service_uuid=tweet_id,
                memory_dict=csv_only_tweet._asdict(),
            )
            if existing is False:
                twitter_user.posts.append(memory)
                apply_tags_to_tweet(
                    db_session=database.session,
                    tweet=memory,
                    status_dict=None)
        database.session.commit()


def import_tweets_from_api(
        database, config, tweet_storage_path, media_storage_path):
    service = __get_service(database.session)
    for config_section in config.sections():
        if config_section.startswith("Twitter_"):
            api = TwitterAPI(
                consumer_key=config.get(
                    section=config_section, option="consumer_key"),
                consumer_secret=config.get(
                    section=config_section, option="consumer_secret"),
                access_token_key=config.get(
                    section=config_section, option="access_key"),
                access_token_secret=config.get(
                    section=config_section, option="access_secret"),
            )
            for tweet_type in (USER, FAVORITES):
                api.import_tweets(
                    database=database,
                    service=service,
                    username=config.get(
                        section=config_section, option="username"),
                    tweet_storage_path=tweet_storage_path,
                    media_storage_path=media_storage_path,
                    tweet_type=tweet_type
                )


def import_tweets_from_csv(database, config, tweet_storage_path,
                           username, csv_filepath, media_storage_path):
    service = __get_service(database.session)

    for config_section in config.sections():
        if config_section.startswith("Twitter_%s" % username):
            break
    else:
        LOGGER.error("Username not found.")
        sys.exit(1)

    api = TwitterAPI(
        consumer_key=config.get(
            section=config_section, option="consumer_key"),
        consumer_secret=config.get(
            section=config_section, option="consumer_secret"),
        access_token_key=config.get(
            section=config_section, option="access_key"),
        access_token_secret=config.get(
            section=config_section, option="access_secret"),
    )
    api.import_from_csv(
        database=database,
        service=service,
        tweet_storage_path=tweet_storage_path,
        csv_filepath=csv_filepath,
        username=username,
        media_storage_path=media_storage_path,
    )


def apply_tags_to_tweet(db_session, tweet, status_dict):
    """Applies appropriate tags to the tweet."""
    tag_names = set()
    if status_dict is not None and "hashtags" in status_dict:
        for hashtag_dict in status_dict["hashtags"]:
            tag_names.add(hashtag_dict["text"])
    for tag_name in tag_names:
        tweet.tags.append(
            Tag.get_tag(
                db_session=db_session,
                tag_name=tag_name)
        )


def __get_service(db_session):
    service, unused_existing = Service.find_or_create(
        db_session=db_session,
        service_name="twitter",
        service_url="https://twitter.com",
    )
    return service
