import re
from abc import ABCMeta, ABC
from os import PathLike
from typing import List, Iterable, Iterator, Optional, Union

from isodate import parse_duration, duration_isoformat, Duration

from googleapiclient.discovery import Resource

from easytube.utils import get_playlists, get_authenticated_service, get_channels, get_playlist_videos


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
    @property
    def url(self) -> str:
        return self.__url

    @property
    def width(self) -> int:
        return self.__width

    @property
    def height(self) -> int:
        return self.__height

    def __init__(self, id: str, url: str, width: int, height: int) -> None:
        super().__init__('youtube#thumbnail', id)
        self.__url = url
        self.__width = width
        self.__height = height

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


class Video(YouTubeResource):
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
    def published_at(self) -> str:
        return self.__published_at

    @property
    def channel_id(self) -> str:
        return self.__channel_id

    @property
    def channel_title(self) -> str:
        return self.__channel_title

    @property
    def thumbnails(self) -> List[Thumbnail]:
        return self.__thumbnails

    @property
    def tags(self) -> List[str]:
        return self.__tags

    @property
    def category_id(self) -> int:
        return self.__category_id

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
    def view_count(self) -> int:
        return self.__view_count

    @property
    def like_count(self) -> int:
        return self.__like_count

    @property
    def dislike_count(self) -> int:
        return self.__dislike_count

    @property
    def favorite_count(self) -> int:
        return self.__favorite_count

    @property
    def comment_count(self) -> int:
        return self.__comment_count

    @property
    def player(self) -> str:
        return self.__player

    @property
    def topic_categories(self) -> List[str]:
        return self.__topic_categories


    @property
    def channel(self) -> Optional['Channel']:
        channels = get_channels(self.__service, channel_id=self.channel_id, max_results=1)
        return Channel.from_dict(self.__service, channels[0]) if channels else None

    def __init__(self, service: Resource, kind: str, id: str, etag: str, title: str, description: str,
                 published_at: str, thumbnails: List[Thumbnail], channel_id: str, channel_title: str,
                 tags: List[str], category_id: int, live_broadcast_content: str, default_audio_language: str,
                 duration: Duration, dimension: str, definition: str, caption: bool, licensed_content: bool,
                 content_rating: dict, projection: str,
                 upload_status: str, privacy_status: str, license: str, embeddable: bool, public_stats_viewable: bool,
                 made_for_kids: bool,
                 view_count: int, like_count: int, dislike_count: int, favorite_count: int, comment_count: int,
                 player: str, topic_categories: List[str]) -> None:
        self.__service = service
        super().__init__(kind, id)
        self.__etag = etag
        self.__title = title
        self.__description = description
        self.__published_at = published_at
        self.__thumbnails = thumbnails
        self.__channel_id = channel_id
        self.__channel_title = channel_title
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
        self.__view_count = view_count
        self.__like_count = like_count
        self.__dislike_count = dislike_count
        self.__favorite_count = favorite_count
        self.__comment_count = comment_count
        self.__player = player
        self.__topic_categories = topic_categories

    @staticmethod
    def from_dict(service: Resource, d: dict) -> 'Video':
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
                     int(d['statistics']['viewCount']), int(d['statistics']['likeCount']),
                     int(d['statistics']['dislikeCount']), int(d['statistics']['favoriteCount']),
                     int(d['statistics']['commentCount']),
                     d['player']['embedHtml'], d['topicDetails']['topicCategories'])

    def __dict__(self) -> dict:
        return {'kind': self.kind, 'etag': self.etag, 'id': self.id,
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
                    'viewCount': str(self.view_count),
                    'likeCount': str(self.like_count),
                    'dislikeCount': str(self.dislike_count),
                    'favoriteCount': str(self.favorite_count),
                    'commentCount': str(self.comment_count)
                },
                'player': {
                    'embedHtml': self.player
                },
                'topicDetails': {'topicCategories': self.topic_categories}
        }


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
        return [Video.from_dict(self.__service, video) for video in get_playlist_videos(self.__service, self.id)]

    @property
    def channel(self) -> Optional['Channel']:
        channels = get_channels(self.__service, channel_id=self.channel_id, max_results=1)
        return Channel.from_dict(self.__service, channels[0]) if channels else None

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
        return self.videos

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
            'snippet': {
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
