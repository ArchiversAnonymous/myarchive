import getpass
import logging
import os

from configparser import NoOptionError

from myarchive.libs.mastodon import Mastodon
from myarchive.util.lib import CONFIG_FOLDER
from myarchive.db.tag_db.tables import Person, Memory

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
            user = mastodon_api.account_verify_credentials()
            mastodon_user = Person(
                service_name="Mastodon",
                service_url=host,
                user_id=user["id"],
                username=username,
                user_dict=user,
            )
            db_session.add(mastodon_user)
            db_session.commit()

            # Fetch user toots.
            results_page = mastodon_api.account_statuses(
                id=user["id"], max_id=None, since_id=None, limit=None)
            while results_page is not None:
                for status_dict in results_page:
                    # media_urls_list = []
                    # for media_dict in status_dict.get(
                    #         "media_attachments", list()):
                    #     media_urls_list.append(media_dict["url"])
                    status = Memory(
                        service_memory_id=status_dict["id"],
                        memory_dict=status_dict,
                        type_="toot",
                    )
                    mastodon_user.memories.append(status)
                db_session.commit()
                results_page = mastodon_api.fetch_next(
                    previous_page=results_page)

            # # Fetch user favorites.
            # results_page = mastodon_api.favourites(
            #     max_id=None, since_id=None, limit=None)
            # while results_page is not None:
            #     for status_dict in results_page:
            #         # media_urls_list = []
            #         # for media_dict in status_dict.get(
            #         #         "media_attachments", list()):
            #         #     media_urls_list.append(media_dict["url"])
            #         status = Memory(
            #             service_memory_id=status_dict["id"],
            #             memory_dict=status_dict,
            #         )
            #         db_session.add(status)
            #     db_session.commit()
            #     results_page = mastodon_api.fetch_next(
            #         previous_page=results_page)
