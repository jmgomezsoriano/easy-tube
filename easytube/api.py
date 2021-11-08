import re
from abc import ABCMeta, ABC
from os import PathLike
from typing import List, Iterable, Iterator, Optional, Union

from googleapiclient.discovery import Resource

from easytube.utils import get_playlists, get_authenticated_service, get_channels


class YouTubeResource(ABC):
    __metaclass__ = ABCMeta

    @property
    def kind(self) -> str:
        return self.__kind

    @property
    def id(self) -> str:
        return self.__id

    def __init__(self, kind: str, id: str) -> None:
        self.__kind = kind
        self.__id = id


class Thumbnail(YouTubeResource):
    def __init__(self, id: str, url: str, width: int, height: int) -> None:
        super().__init__('youtube#thumbnail', id)
        self.url = url
        self.width = width
        self.height = height

    @staticmethod
    def from_dict(id: str, d: dict) -> 'Thumbnail':
        return Thumbnail(id, d['url'], d['width'], d['height'])

    def __dict__(self) -> dict:
        return {
            'url': self.url,
            'width': self.width,
            'height': self.height
        }

    def __str__(self) -> str:
        return f'{self.kind}[{self.id}:({self.width}x{self.height}]'

    def __repr__(self) -> str:
        return str(self)


class Video(object):
    pass


class Playlist(YouTubeResource):
    @property
    def etag(self) -> str:
        return self.__etag

    @property
    def title(self) -> str:
        return self.__title

    @property
    def description(self) -> str:
        return self.__description

    @property
    def url(self) -> str:
        return f'https://www.youtube.com/playlist?list={self.id}'

    @property
    def channel_id(self) -> str:
        return self.__channel_id

    @property
    def channel_title(self) -> str:
        return self.__channel_title

    @property
    def published_at(self) -> str:
        return self.__published_at

    @property
    def localized(self) -> str:
        return self.__localized

    @property
    def status(self) -> str:
        return self.__status

    @property
    def num_videos(self) -> int:
        return self.__num_videos

    @property
    def player(self) -> str:
        return self.player

    @property
    def videos(self) -> List[Video]:
        return get_videos()

    def __init__(self, service: Resource, kind: str, id: str, etag: str, title: str, description: str, channel_id: str,
                 channel_title: str, published_at: str, thumbnails: List[Thumbnail], localized: str, status: str,
                 num_videos: int, player: str) -> None:
        self.__service = service
        super().__init__(kind, id)
        self.__etag = etag
        self.__title = title
        self.__description = description
        self.__channel_id = channel_id
        self.__channel_title = channel_title
        self.__published_at = published_at
        self.__thumbnails = thumbnails
        self.__localized = localized
        self.__status = status
        self.__num_videos = num_videos
        self.__player = player

    def __iter__(self) -> Iterator[Video]:
        pass

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
                        d['contentDetails']['itemCount'],
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
            'snippet' : {
                'title': self.title,
                'description': self.description,
                'thumbnails': {t.id: t.__dict__() for t in self.thumbnails},
                'localized': self.localized,
            },
            'status': {'privacyStatus': self.status},
            'contentDetails': {'itemCount': self.num_videos},
            'player': self.player
        }

    def __str__(self) -> str:
        return f'{self.kind}{self.id, self.title, self.status}'

    def __repr__(self) -> str:
        return str(self)


class Statistics(object):
    @property
    def view_count(self) -> int:
        return self.__view_count

    @property
    def subscriber_count(self) -> int:
        return self.__subscriber_count

    @property
    def hidden_subscriber_count(self) -> bool:
        return self.__hidden_subscriber_count

    @property
    def video_count(self) -> int:
        return self.__video_count

    def __init__(self, view_count: int, subscriber_count: int, hidden_subscriber_count: bool, video_count: int) -> None:
        self.__view_count = view_count
        self.__subscriber_count = subscriber_count
        self.__hidden_subscriber_count = hidden_subscriber_count
        self.__video_count = video_count

    @staticmethod
    def from_dict(d: dict) -> 'Statistics':
        views, subscribers, videos = int(d['viewCount']), int(d['subscriberCount']), int(d['videoCount'])
        return Statistics(views, subscribers, d['hiddenSubscriberCount'], videos)

    def __dict__(self) -> dict:
        return {
            'viewCount': str(self.view_count),
            'subscriberCount': str(self.subscriber_count),
            'hiddenSubscriberCount': self.hidden_subscriber_count,
            'videoCount': str(self.view_count)
        }

    def __str__(self) -> str:
        return str(self.__dict__())

    def __repr__(self) -> str:
        return str(self)


class Channel(YouTubeResource, Iterable):
    @property
    def etag(self) -> str:
        return self.__etag

    @property
    def likes(self) -> str:
        return self.__likes

    @property
    def uploads(self) -> Playlist:
        return self.__uploads

    @property
    def title(self) -> str:
        return self.__title

    @property
    def description(self) -> str:
        return self.__description

    @property
    def custom_url(self) -> str:
        return self.__custom_url

    @property
    def published_at(self) -> str:
        return self.__published_at

    @property
    def thumbnails(self) -> List[Thumbnail]:
        return self.__thumbnails

    @property
    def statistics(self) -> Statistics:
        return self.__statistics

    @property
    def topics(self) -> dict:
        return self.__topics

    @property
    def playlists(self) -> List[Playlist]:
        return [Playlist.from_dict(self.__service, d) for d in get_playlists(self.__service, self.id)]

    @property
    def url(self) -> str:
        return f'https://www.youtube.com/channel/{self.id}'

    def __init__(self, service: Resource, kind: str, id: str, etag: str, title: str, description: str, custom_url: str,
                 published_at: str, thumbnails: List[Thumbnail], statistics: Statistics, likes: str,
                 uploads: Playlist, topics: dict) -> None:
        self.__service = service
        super().__init__(kind, id)
        self.__etag = etag
        self.__title = title
        self.__description = description
        self.__custom_url = custom_url
        self.__published_at = published_at
        self.__thumbnails = thumbnails
        self.__statistics = statistics
        self.__likes = likes
        self.__topics = topics
        self.__uploads = uploads

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

    def __repr__(self) -> str:
        return str(self)


class YouTube(object):
    def __init__(self, client_secret_file: Union[str, PathLike, bytes], authorization: [str, PathLike, bytes]) -> None:
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
