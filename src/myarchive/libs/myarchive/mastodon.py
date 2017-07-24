import getpass
import logging
import os

from configparser import NoOptionError

from myarchive.libs.mastodon import Mastodon
from myarchive.util.lib import CONFIG_FOLDER

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
            try:
                password = config.get(section=config_section, option="password")
            except NoOptionError:
                password = getpass.getpass()

            LOGGER.critical([host, username, password])

            mastodon_api = Mastodon(
                client_id=APP_SECRET_PATH,
                api_base_url=host,
            )
            mastodon_api.log_in(
                username,
                password,
            )
            user = mastodon_api.account_verify_credentials()

            toots = []

            results_page = mastodon_api.account_statuses(
                id=user["id"], max_id=None, since_id=None, limit=None)
            toots.extend(results_page)
            while results_page:
                results_page = mastodon_api.fetch_next(
                    previous_page=results_page)
                if results_page is not None:
                    toots.extend(results_page)
            LOGGER.info(len(toots))

            # results_page = mastodon.favourites(
            #     max_id=None, since_id=None, limit=None)
