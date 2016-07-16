# Requires python-lj 0.2.
from lj import lj
from lj.backup import (
    DEFAULT_JOURNAL, update_journal_entries, update_journal_comments)


class LJAPIServerConnection(object):

    def __init__(self, host, user_agent, username, password):
        self._server = lj.LJServer(
            "Python-Blog3/1.0",
            user_agent=user_agent,
            host=host)
        self._server.login(
            user=username,
            password=password)
        self.journal = DEFAULT_JOURNAL.copy()

    def post_journal(self, subject, post, tags):
        """
        Posts a journal to the specified LJ server.

        WARNING: MUST use HTTPS since this API uses *md5sum* for authentication! D:
        """
        self._server.postevent(
            event=post,
            subject=subject,
            props={"taglist": ",".join(tags)})

    def download_journals_and_comments(self):
        """Downloads journals and comments to a defined dictionary."""
        self.journal = DEFAULT_JOURNAL.copy()
        # Sync entries from the server
        print("Downloading journal entries")
        nj = update_journal_entries(server=self._server, journal=self.journal)

        # Sync comments from the server
        print("Downloading comments")
        nc = update_journal_comments(server=self._server, journal=self.journal)

        print("Updated %d entries and %d comments" % (nj, nc))
