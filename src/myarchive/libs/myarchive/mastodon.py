import getpass
import logging
import os

from configparser import NoOptionError

from myarchive.libs.mastodon import Mastodon
from myarchive.util.lib import CONFIG_FOLDER
from myarchive.db.tag_db.tables import Service, User, Memory, TrackedFile

LOGGER = logging.getLogger(__name__)
APP_SECRET_PATH = os.path.join(CONFIG_FOLDER, "mastodon.app.secret")


def download_toots(db_session, media_storage_path, config):

    if not os.path.exists(APP_SECRET_PATH):
        Mastodon.create_app(
             'myarchive',
             api_base_url='awoo.space',
             to_file=APP_SECRET_PATH
        )

    for config_section in config.sections():
        if config_section.startswith("Mastodon_"):
            host = config.get(section=config_section, option="host")
            username = config.get(section=config_section, option="username")
            LOGGER.info("Grabbing toots for %s [%s]...", username, host)
            try:
                password = config.get(section=config_section, option="password")
            except NoOptionError:
                password = getpass.getpass()

            mastodon_api = Mastodon(
                client_id=APP_SECRET_PATH,
                api_base_url=host,
            )
            mastodon_api.log_in(
                username,
                password,
            )
            user_dict = mastodon_api.account_verify_credentials()

            service_name = "mastodon"
            service_url = host
            user_id = user_dict["id"]

            service, unused_existing = Service.find_or_create(
                db_session=db_session,
                service_name=service_name,
                service_url=service_url,
            )

            mastodon_user, unused_existing = User.find_or_create(
                db_session=db_session,
                service_id=service.id,
                user_id=user_id,
                username=username,
            )

            # Fetch user toots.
            results_page = mastodon_api.account_statuses(
                id=user_id, max_id=None, since_id=None, limit=None)
            while results_page is not None:
                for status_dict in results_page:
                    memory, existing = Memory.find_or_create(
                        db_session=db_session,
                        service_id=service.id,
                        service_uuid=str(status_dict["id"]),
                        memory_dict=status_dict,
                    )
                    if existing is True:
                        results_page = None
                        break
                    if memory.user_id is None:
                        mastodon_user.posts.append(memory)
                    for media_dict in status_dict.get(
                            "media_attachments", list()):
                        tracked_file, existing = TrackedFile.download_file(
                            db_session, media_path=media_storage_path,
                            url=media_dict["url"], file_source=service_name)
                        if tracked_file not in memory.files:
                            memory.files.append(tracked_file)
                db_session.commit()
                # If we kicked out of the inner loop, no reason to continue
                # here.
                if results_page is not None:
                    results_page = mastodon_api.fetch_next(
                        previous_page=results_page)

            # Fetch user favorites.
            results_page = mastodon_api.favourites(
                max_id=None, since_id=None, limit=None)
            while results_page is not None:
                for status_dict in results_page:
                    memory, unused_existing = Memory.find_or_create(
                        db_session=db_session,
                        service_id=service.id,
                        service_uuid=str(status_dict["id"]),
                        memory_dict=status_dict,
                    )
                    if memory not in mastodon_user.favorites:
                        mastodon_user.favorites.append(memory)
                    for media_dict in status_dict.get(
                            "media_attachments", list()):
                        tracked_file, existing = TrackedFile.download_file(
                            db_session, media_path=media_storage_path,
                            url=media_dict["url"], file_source=service_name)
                        if tracked_file not in memory.files:
                            memory.files.append(tracked_file)
                db_session.commit()
                if results_page is not None:
                    results_page = mastodon_api.fetch_next(
                        previous_page=results_page)
