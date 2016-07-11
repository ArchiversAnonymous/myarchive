#!/usr/bin/python

import argparse
import os
import sys

import twitterlib
from db import TagDB
# from gui import Gtk, MainWindow
from util.logger import myarchive_LOGGER as logger


def main():
    """Starts up the DB connection and GUI."""

    parser = argparse.ArgumentParser(
        description='Manages tagged files.')
    parser.add_argument(
        "-D", "--db_filename",
        action="store",
        default="/tmp/myarchive/db/archive.sqlite",
        help="Database filename.")
    parser.add_argument(
        '--media-path',
        action="store",
        default="/tmp/myarchive/media/",
        help='Prints all tweets.')
    parser.add_argument(
        "--import-folder",
        type=str,
        dest="import_folder",
        help="Folder to organize.")
    parser.add_argument(
        '--username',
        action="store",
        help='Accepts a service username.')
    parser.add_argument(
        '--import-tweets-from-api',
        action="store_true",
        default=False,
        help='Downloads favorites. Accepts a Twitter username.')
    parser.add_argument(
        '--import-tweets-from-archive-csv',
        action="store",
        help='Downloads favorites. Accepts a Twitter username.')
    parser.add_argument(
        '--parse-tweets',
        action="store_true",
        default=False,
        help='Prints all tweets.')
    parser.add_argument(
        '--print-tweets',
        action="store_true",
        default=False,
        help='Prints all tweets.')
    args = parser.parse_args()

    logger.debug(args)

    if args.import_folder:
        if not os.path.exists(args.import_folder):
            raise Exception("Import folder path does not exist!")
        if not os.path.isdir(args.import_folder):
            raise Exception("Import folder path is not a folder!")

    if args.db_filename:
        tag_db = TagDB(
            drivername='sqlite',
            db_name=args.db_filename)
    else:
        tag_db = TagDB()

    raw_tweets = []
    csv_only_tweets = []
    if args.import_tweets_from_archive_csv:
        if not args.username:
            logger.error("Username is required for tweet imports!")
            sys.exit(1)
        csv_raw_tweets, csv_only_tweets = twitterlib.import_from_csv(
            db_session=tag_db.session,
            csv_filepath=args.import_tweets_from_archive_csv,
            username=args.username)
        raw_tweets.extend(csv_raw_tweets)
    if args.import_tweets_from_api:
        if not args.username:
            logger.error("Username is required for tweet imports!")
            sys.exit(1)
        raw_tweets.extend(
            twitterlib.archive_tweets(
                db_session=tag_db.session,
                username=args.username)
        )
    if args.parse_tweets is True:
        twitterlib.parse_tweets(
            db_session=tag_db.session, parse_all_raw=True)
    if args.print_tweets is True:
        twitterlib.print_tweets(db_session=tag_db.session)

    if raw_tweets or csv_only_tweets:
        print "Processing %s new raw tweets and %s CSV-only tweets..." % (
            len(raw_tweets), len(csv_only_tweets))
        twitterlib.parse_tweets(
            db_session=tag_db.session, raw_tweets=raw_tweets,
            csv_only_tweets=csv_only_tweets)

    # MainWindow(tag_db)
    # Gtk.main()


if __name__ == '__main__':
    main()
