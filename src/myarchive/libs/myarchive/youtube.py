# @Author: Zeta Syanthis <zetasyanthis>
# @Date:   2017/07/21
# @Email:  zeta@zetasyanthis.org
# @Project: MyArchive
# @Last modified by:   zetasyanthis
# @Last modified time: 2017/07/21
# @License MIT

import os

from datetime import datetime
from logging import getLogger

from myarchive.db.tag_db.tables import Service, Memory, TrackedFile, Tag
from myarchive.libs import pafy

LOGGER = getLogger(__name__)


def download_youtube_playlists(db_session, media_storage_path, playlist_urls):
    """Downloads videos"""

    service, unused_existing = Service.find_or_create(
        db_session=db_session,
        service_name="youtube",
        service_url="https://youtube.com",
    )
    db_session.add(service)

    LOGGER.warning(
        "Youtube downloads may take quite a lot of drive space! Make sure you "
        "have a good amount free before triggering video downloads.")

    for playlist_url in playlist_urls:
        playlist = pafy.get_playlist2(playlist_url=playlist_url)
        LOGGER.info(
            "Parsing playlist %s [%s]...", playlist.title, playlist.author)

        playlist_dict = {
            "author": playlist.author,
            "title": playlist.title,
            "description": playlist.description,
            "plid": playlist.plid,
        }
        db_playlist, unused_existing = Memory.find_or_create(
            db_session=db_session,
            service_id=service.id,
            service_uuid=str(playlist.plid),
            memory_dict=playlist_dict,
        )
        db_session.add(db_playlist)
        db_session.commit()

        total_bytes = 0
        video_stream_tuples = []
        for video in playlist:
            try:
                pafy_stream = video.getbest()
                video_stream_tuples.append([video, pafy_stream])
                total_bytes += pafy_stream.get_filesize()
            except Exception as whatwasthat:
                LOGGER.error(whatwasthat)
        LOGGER.info("Playlist DL size: %s MB" % int(total_bytes / 2 ** 20))

        for video, stream in video_stream_tuples:
            LOGGER.info("Downloading %s...", stream.title)
            temp_filepath = "/tmp/" + stream.title + "." + stream.extension
            stream.download(filepath=temp_filepath)
            try:
                tracked_file, existing = TrackedFile.add_file(
                    db_session=db_session,
                    media_path=media_storage_path,
                    file_source="youtube",
                    copy_from_filepath=temp_filepath,
                    move_original_file=True,
                )
                if existing is True:
                    os.remove(temp_filepath)
                else:
                    db_session.add(tracked_file)

                video_dict = {
                    "uploader": video.username,
                    "description": video.description,
                    "duration": video.duration,
                    "publish_time": video.published,
                    "videoid": video.videoid,
                }
                ytvideo, unused_existing = db_playlist.add_child(
                    db_session=db_session,
                    service_id=service.id,
                    service_uuid=str(video.videoid),
                    memory_dict=video_dict,
                )
                if tracked_file not in ytvideo.files:
                    ytvideo.files.append(tracked_file)
                for keyword in video.keywords:
                    tag = Tag.get_tag(db_session=db_session, tag_name=keyword)
                    ytvideo.tags.append(tag)
                    tracked_file.tags.append(tag)
                db_session.commit()
            except:
                db_session.rollback()
                raise

    db_session.commit()
