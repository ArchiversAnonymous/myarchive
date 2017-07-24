import getpass
import logging
import os

from configparser import NoOptionError

from myarchive.libs.mastodon import Mastodon
from myarchive.util.lib import CONFIG_FOLDER

LOGGER = logging.getLogger(__name__)
SECRET_PATH = os.path.join(CONFIG_FOLDER, "mastodon.secret")


def download_toots(db_session, media_storage_path, config):

    if not os.path.exists(SECRET_PATH):
        Mastodon.create_app(
             'myarchive',
             api_base_url='awoo.space',
             to_file=SECRET_PATH
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

            mastodon = Mastodon(
                client_id=SECRET_PATH,
                api_base_url=host,
            )
            mastodon.log_in(
                username,
                password,
                to_file=SECRET_PATH,
            )

            # mastodon.toot(
            #     status="OMG IT WORKS!")
