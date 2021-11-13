import re
from os import PathLike
from typing import List, Iterable, Iterator, Optional, Union

from isodate import parse_duration, duration_isoformat, Duration

from googleapiclient.discovery import Resource

from easytube.resources import YouTubeResource, Thumbnail, Statistics, ItemYouTubeResource, IterableYouTubeResource, \
    Playable
from easytube.utils import get_playlists, get_authenticated_service, get_channels, get_playlist_videos, get_video


class Video(ItemYouTubeResource, Playable):
    @property
    def tags(self) -> List[str]:
        return self.__tags

    @property
    def category_id(self) -> int:
        return self.__category_id

    @property
    def url(self) -> str:
        return f'https://www.youtube.com/watch?v={self.id}'

    @property
    def live_broadcast_content(self) -> str:
        return self.__live_broadcast_content

    @property
    def default_audio_language(self) -> str:
        return self.__default_audio_language

    @property
    def duration(self) -> Duration:
        return self.__duration

    @property
    def dimension(self) -> str:
        return self.__dimension

    @property
    def definition(self) -> str:
        return self.__definition

    @property
    def caption(self) -> bool:
        return self.__caption

    @property
    def licensed_content(self) -> bool:
        return self.__licensed_content

    @property
    def content_rating(self) -> dict:
        return self.__content_rating

    @property
    def projection(self) -> str:
        return self.__projection

    @property
    def upload_status(self) -> str:
        return self.__upload_status

    @property
    def privacy_status(self) -> str:
        return self.__privacy_status

    @property
    def license(self) -> str:
        return self.__license

    @property
    def embeddable(self) -> bool:
        return self.__embeddable

    @property
    def public_stats_viewable(self) -> bool:
        return self.__public_stats_viewable

    @property
    def made_for_kids(self) -> bool:
        return self.__made_for_kids

    @property
    def topic_categories(self) -> List[str]:
        return self.__topic_categories

    @property
    def channel(self) -> Optional['Channel']:
        if self.__channel:
            return self.__channel
        channels = self.__channel or get_channels(self._service, channel_id=self.channel_id, max_results=1)
        self.__channel = Channel.from_dict(self._service, channels[0]) if channels else None
        return self.__channel

    def __init__(self, service: Resource, kind: str, id: str, etag: str, title: str, description: str,
                 published_at: str, thumbnails: List[Thumbnail], channel_id: str, channel_title: str,
                 tags: List[str], category_id: int, live_broadcast_content: str, default_audio_language: str,
                 duration: Duration, dimension: str, definition: str, caption: bool, licensed_content: bool,
                 content_rating: dict, projection: str,
                 upload_status: str, privacy_status: str, license: str, embeddable: bool, public_stats_viewable: bool,
                 made_for_kids: bool, statistics: Statistics,
                 player: str, topic_categories: List[str]) -> None:
        super().__init__(service, kind, id, etag, title, description, channel_id, channel_title, published_at,
                         thumbnails, statistics)
        Playable.__init__(self, player)
        self.__tags = tags
        self.__category_id = category_id
        self.__live_broadcast_content = live_broadcast_content
        self.__default_audio_language = default_audio_language
        self.__duration = duration
        self.__dimension = dimension
        self.__definition = definition
        self.__caption = caption
        self.__licensed_content = licensed_content
        self.__content_rating = content_rating
        self.__projection = projection
        self.__upload_status = upload_status
        self.__privacy_status = privacy_status
        self.__license = license
        self.__embeddable = embeddable
        self.__public_stats_viewable = public_stats_viewable
        self.__made_for_kids = made_for_kids
        self.__topic_categories = topic_categories
        self.__channel = None
        self.__playlists = None

    @staticmethod
    def from_dict(service: Resource, d: dict) -> Optional['Video']:
        if not d:
            return None
        view_count = int(d['statistics']['viewCount'])
        like_count = int(d['statistics']['likeCount'])
        dislike_count = int(d['statistics']['dislikeCount'])
        favorite_count = int(d['statistics']['favoriteCount'])
        comment_count = int(d['statistics']['commentCount'])
        statistics = Statistics(view_count=view_count, like_count=like_count, dislike_count=dislike_count,
                                favorite_count=favorite_count, comment_count=comment_count)
        return Video(service, d['kind'], d['id'], d['etag'],
                     d['snippet']['title'], d['snippet']['description'], d['snippet']['publishedAt'],
                     [Thumbnail.from_dict(id, d) for id, d in d['snippet']['thumbnails'].items()],
                     d['snippet']['channelId'], d['snippet']['channelTitle'], d['snippet']['tags'],
                     int(d['snippet']['categoryId']), d['snippet']['liveBroadcastContent'],
                     d['snippet']['defaultAudioLanguage'],
                     parse_duration(d['contentDetails']['duration']), d['contentDetails']['dimension'],
                     d['contentDetails']['definition'], d['contentDetails']['caption'].lower() == 'true',
                     d['contentDetails']['licensedContent'], d['contentDetails']['contentRating'],
                     d['contentDetails']['projection'],
                     d['status']['uploadStatus'], d['status']['privacyStatus'], d['status']['license'],
                     d['status']['embeddable'], d['status']['publicStatsViewable'], d['status']['madeForKids'],
                     statistics,
                     d['player']['embedHtml'], d['topicDetails']['topicCategories'])

    def __dict__(self) -> dict:
        return {
            'kind': self.kind, 'etag': self.etag, 'id': self.id,
            'snippet': {
                'publishedAt': self.published_at, 'channelId': self.channel_id,
                'title': self.title, 'description': self.description,
                'thumbnails': {th.id: th.__dict__() for th in self.thumbnails},
                'channelTitle': self.channel_title,
                'tags': self.tags,
                'categoryId': str(self.category_id),
                'liveBroadcastContent': self.live_broadcast_content,
                'localized': {'title': self.title, 'description': self.description},
                'defaultAudioLanguage': self.default_audio_language
            },
            'contentDetails': {
                'duration': duration_isoformat(self.duration),
                'dimension': self.dimension,
                'definition': self.definition,
                'caption': 'true' if self.caption else 'false',
                'licensedContent': self.licensed_content,
                'contentRating': self.content_rating,
                'projection': self.projection
            },
            'status': {
                'uploadStatus': self.upload_status,
                'privacyStatus': self.privacy_status,
                'license': self.license,
                'embeddable': self.embeddable,
                'publicStatsViewable': self.public_stats_viewable,
                'madeForKids': self.made_for_kids
            },
            'statistics': {
                'viewCount': str(self.statistics.view_count),
                'likeCount': str(self.statistics.like_count),
                'dislikeCount': str(self.statistics.dislike_count),
                'favoriteCount': str(self.statistics.favorite_count),
                'commentCount': str(self.statistics.comment_count)
            },
            'player': {
                'embedHtml': self.player
            },
            'topicDetails': {'topicCategories': self.topic_categories}
        }

    def __str__(self) -> str:
        return str((self.id, self.title, str(self.duration)))


class Playlist(IterableYouTubeResource, Playable):
    @property
    def url(self) -> str:
        return f'https://www.youtube.com/playlist?list={self.id}'

    @property
    def localized(self) -> str:
        return self.__localized

    @property
    def status(self) -> str:
        return self.__status

    @property
    def videos(self) -> List[Video]:
        return [Video.from_dict(self._service, video) for video in get_playlist_videos(self._service, self.id)]

    @property
    def channel(self) -> Optional['Channel']:
        channels = get_channels(self._service, channel_id=self.channel_id, max_results=1)
        return Channel.from_dict(self._service, channels[0]) if channels else None

    def __init__(self, service: Resource, kind: str, id: str, etag: str, title: str, description: str, channel_id: str,
                 channel_title: str, published_at: str, thumbnails: List[Thumbnail], localized: str, status: str,
                 statistics: Statistics, player: str) -> None:
        super().__init__(service, kind, id, etag, title, description, channel_id, channel_title,
                         published_at, thumbnails, statistics)
        Playable.__init__(self, player)
        self.__localized = localized
        self.__status = status

    def __iter__(self) -> Iterator[Video]:
        return self.videos

    def __len__(self) -> int:
        return len(self.videos)

    @staticmethod
    def from_dict(service: Resource, d: dict) -> 'Playlist':
        return Playlist(service, d['kind'], d['id'], d['etag'],
                        d['snippet']['title'],
                        d['snippet']['description'],
                        d['snippet']['channelId'],
                        d['snippet']['channelTitle'],
                        d['snippet']['publishedAt'],
                        [Thumbnail.from_dict(id, t) for id, t in d['snippet']['thumbnails'].items()],
                        d['snippet']['localized'],
                        d['status']['privacyStatus'],
                        Statistics(video_count=d['contentDetails']['itemCount']),
                        d['player'])

    @staticmethod
    def from_id(service: Resource, id: str) -> 'Playlist':
        playlists = get_playlists(service, max_results=1, playlist_id=id)
        return Playlist.from_dict(service, playlists[0]) if playlists else None

    def __dict__(self) -> dict:
        return {
            'kind': self.kind,
            'id': self.id,
            'etag': self.etag,
            'snippet': {
                'title': self.title,
                'description': self.description,
                'thumbnails': {t.id: t.__dict__() for t in self.thumbnails},
                'localized': self.localized,
            },
            'status': {'privacyStatus': self.status},
            'contentDetails': {'itemCount': self.statistics.video_count},
            'player': self.player
        }

    def __str__(self) -> str:
        return f'{self.kind}{self.id, self.title, self.status}'


class Channel(IterableYouTubeResource):
    @staticmethod
    def from_url(service: Resource, url: str) -> YouTubeResource:
        pass

    def __len__(self) -> int:
        return len(self.playlists)

    @staticmethod
    def from_id(service: Resource, id: str) -> 'Channel':
        pass

    @property
    def likes(self) -> str:
        return self.__likes

    @property
    def uploads(self) -> Playlist:
        return self.__uploads

    @property
    def custom_url(self) -> str:
        return self.__custom_url

    @property
    def topics(self) -> dict:
        return self.__topics

    @property
    def playlists(self) -> List[Playlist]:
        if self.__playlists:
            return self.__playlists
        self.__playlists = [Playlist.from_dict(self._service, d) for d in get_playlists(self._service, self.id)]
        return self.__playlists

    @property
    def url(self) -> str:
        return f'https://www.youtube.com/channel/{self.id}'

    def __init__(self, service: Resource, kind: str, id: str, etag: str, title: str, description: str, custom_url: str,
                 published_at: str, thumbnails: List[Thumbnail], statistics: Statistics, likes: str,
                 uploads: Playlist, topics: dict) -> None:
        super().__init__(service, kind, id, etag, title, description, id, title, published_at, thumbnails, statistics)
        self.__custom_url = custom_url
        self.__likes = likes
        self.__uploads = uploads
        self.__topics = topics
        self.__playlists = None

    @staticmethod
    def from_dict(service: Resource, d: dict) -> 'Channel':
        return Channel(service, d['kind'], d['id'], d['etag'], d['snippet']['title'], d['snippet']['description'],
                       d['snippet']['customUrl'] if 'customUrl' in d['snippet'] else None, d['snippet']['publishedAt'],
                       [Thumbnail.from_dict(id, t) for id, t in d['snippet']['thumbnails'].items()],
                       Statistics.from_dict(d['statistics']), d['contentDetails']['relatedPlaylists']['likes'],
                       Playlist.from_id(service, d['contentDetails']['relatedPlaylists']['uploads']),
                       d['topicDetails'])

    def __iter__(self) -> List[Playlist]:
        return self.playlists

    def __dict__(self) -> dict:
        return {
            'kind': self.kind,
            'id': self.id,
            'etag': self.etag,
            'snippet': {
                'title': self.title,
                'description': self.description,
                'customUrl': self.custom_url,
                'publishedAt': self.published_at,
                'thumbnails': self.thumbnails.__dict__,
            },
            'statistics': self.statistics.__dict__(),
            'relatedPlaylists': {
                'likes': self.likes,
                'uploaded': self.uploads.id,
            },
            'topicDetails': self.topics
        }

    def __str__(self) -> str:
        return f'{self.kind}({{"id":{self.id}, "title": {self.title}, description": {self.description}}})'


class YouTube(object):
    """ A class that represents the YouTube connection. """
    def __init__(self, client_secret_file: Union[str, PathLike, bytes], authorization: [str, PathLike, bytes]) -> None:
        """ Create a new YouTube connection.

        :param client_secret_file: The secret file obtained from the
        :param authorization:
        """
        self.__service = get_authenticated_service(client_secret_file, authorization)

    def first_channel(self, user_name: str = None) -> Channel:
        return self.channels(user_name)[0]

    def channels(self, user_name: str = None) -> List[Channel]:
        channels = get_channels(self.__service, user_name=user_name)
        return [Channel.from_dict(self.__service, channel) for channel in channels]

    def channel_titles(self, user_name: str = None) -> List[str]:
        return [channel.title for channel in self.channels(user_name)]

    def channel(self, id: str) -> Optional[Channel]:
        channels = get_channels(self.__service, channel_id=id, max_results=1)
        return Channel.from_dict(self.__service, channels[0]) if channels else None

    def channel_from_url(self, url: str) -> Optional[Channel]:
        id = re.sub(r'^.*/channel/([^/]*)(/[^/]+)?$', r'\1', url)
        return self.channel(id)

    def playlist(self, id: str) -> Playlist:
        playlists = get_playlists(self.__service, playlist_id=id)
        return Playlist.from_dict(self.__service, playlists[0]) if playlists else None

    def video_from_id(self, id: str) -> Optional[Video]:
        return Video.from_dict(self.__service, get_video(self.__service, id))
