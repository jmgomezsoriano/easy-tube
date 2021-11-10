from abc import ABCMeta, ABC, abstractmethod
from typing import List, Iterator, Iterable

from googleapiclient.discovery import Resource


class YouTubeResource(ABC):
    """ Abstract class for youtube resources. """
    __metaclass__ = ABCMeta

    @property
    def kind(self) -> str:
        """
        :return: The kind of the resource.
        """
        return self.__kind

    @property
    def id(self) -> str:
        """
        :return: The resource id.
        """
        return self.__id

    def __init__(self, kind: str, id: str) -> None:
        """ Constructor.

        :param kind: The kind of the resource.
        :param id: The resource id.
        """
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

    def __init__(self, view_count: int = None, subscriber_count: int = None, hidden_subscriber_count: bool = None,
                 video_count: int = None, like_count: int = None, dislike_count: int = None, favorite_count: int = None,
                 comment_count: int = None) -> None:
        self.__view_count = view_count
        self.__subscriber_count = subscriber_count
        self.__hidden_subscriber_count = hidden_subscriber_count
        self.__video_count = video_count
        self.__like_count = like_count
        self.__dislike_count = dislike_count
        self.__favorite_count = favorite_count
        self.__comment_count = comment_count

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


class ItemYouTubeResource(YouTubeResource):
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
    @abstractmethod
    def url(self) -> str:
        pass

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
    def thumbnails(self) -> List[Thumbnail]:
        return self.__thumbnails

    @property
    def statistics(self) -> Statistics:
        return self.__statistics

    def __init__(self, service: Resource, kind: str, id: str, etag: str, title: str, description: str, channel_id: str,
                 channel_title: str, published_at: str, thumbnails: List[Thumbnail],
                 statistics: Statistics = Statistics()):
        self._service = service
        super().__init__(kind, id)
        self.__etag = etag
        self.__title = title
        self.__description = description
        self.__channel_id = channel_id
        self.__channel_title = channel_title
        self.__published_at = published_at
        self.__thumbnails = thumbnails
        self.__statistics = statistics

    @abstractmethod
    def __dict__(self) -> dict:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass

    def __repr__(self) -> str:
        return str(self)


class IterableYouTubeResource(ItemYouTubeResource, Iterable, ABC):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __iter__(self) -> Iterator:
        pass

    @abstractmethod
    def __len__(self) -> int:
        pass


class Playable(object):
    @property
    def player(self) -> str:
        return self.__player

    def __init__(self, player: str) -> None:
        self.__player = player
