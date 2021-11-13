from os import PathLike
from typing import List, Union, Optional

from httplib2 import Http
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow
from googleapiclient.discovery import build, Resource

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account.
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_READONLY_SCOPE = "https://www.googleapis.com/auth/youtube.readonly"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


def error_msg(client_secret_file: str) -> str:
    # This variable defines a message to display if the CLIENT_SECRETS_FILE is
    # missing.
    return f"""
    WARNING: Please configure OAuth 2.0

    To make this sample run you will need to populate the client_secrets.json file
    found at:

       {client_secret_file}

    with information from the API Console
    https://console.developers.google.com/

    For more information about the client_secrets.json file format, please visit:
    https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
    """


def get_authenticated_service(client_secret_file: Union[str, PathLike, bytes],
                              authorization: Union[str, PathLike, bytes]) -> Resource:
    flow = flow_from_clientsecrets(client_secret_file,
                                   scope=YOUTUBE_READ_WRITE_SCOPE,
                                   message=error_msg(client_secret_file))

    storage = Storage(authorization)
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage)

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, http=credentials.authorize(Http()))


def get_channels(service: Resource, user_name: str = None, channel_id: str = None, max_results: int = 0) -> List[dict]:
    params = {'part': 'contentDetails,snippet,brandingSettings,statistics,topicDetails'}
    if user_name:
        params['forUsername'] = user_name
    elif channel_id:
        params['id'] = channel_id
    else:
        params['mine'] = True
    response = service.channels().list(maxResults=max_results or 50, **params).execute()
    channels = []
    while 'items' in response:
        channels.extend([item for item in response['items']])
        if 'pageToken' not in response or (max_results and max_results < len(channels)):
            return channels
        page_token = response['pageToken']
        response = service.channels().list(maxResults=max_results - len(channels) if max_results else 50, **params,
                                           pageToken=page_token).execute()
    return channels


def get_playlists(service: Resource,
                  channel_id: str = None,
                  playlist_id: str = None,
                  max_results: int = 0) -> List[dict]:
    params = {'part': 'contentDetails,snippet,status,player,localizations'}
    if channel_id:
        params['channelId'] = channel_id
    elif playlist_id:
        params['id'] = playlist_id
    playlists = []
    response = service.playlists().list(maxResults=max_results or 50, **params).execute()
    while 'items' in response:
        playlists.extend([item for item in response['items']])
        if 'nextPageToken' not in response or (max_results and max_results < len(playlists)):
            return playlists
        page_token = response['nextPageToken']
        response = service.playlists().list(maxResults=max_results - len(playlists) if max_results else 50,
                                            pageToken=page_token, **params).execute()
    return playlists


def get_videos(service: Resource,
               channel_id: str = None,
               playlist_id: str = None,
               *ids: str,
               max_results: int = 0) -> List[dict]:
    part = 'id,snippet,contentDetails,fileDetails,player,processingDetails,' \
           'recordingDetails,statistics,status,suggestions,topicDetails'
    videos = []
    if channel_id:
        pass
    elif playlist_id:
        pass
    else:
        return [get_video(service, id) for id in ids]

    #     response = service.videos().list(part=part, maxResults=max_results or 50, id=','.join(id))
    #     while 'items' in response:
    #         videos.extend([item for item in response['items']])
    #         if 'nextPageToken' not in response or (max_results and max_results < len(videos)):
    #             return videos
    #         page_token = response['nextPageToken']
    #         response = service.videos().list(maxResults=max_results - len(videos) if max_results else 50,
    #                                          pageToken=page_token, part=part).execute()
    # return videos


def get_video(service: Resource, id: str, mine: bool = False) -> dict:
    part = 'id,snippet,contentDetails,player,statistics,status,topicDetails'
    part += ',fileDetails,processingDetails,recordingDetails,suggestions,' if mine else ''
    videos = service.videos().list(part=part, maxResults=1, id=id).execute()
    return videos['items'][0] if 'items' in videos and videos['items'] else None


def get_playlist_videos(service: Resource, id: str, max_results: int = 0) -> List[dict]:
    ids = get_playlist_video_ids(service, id, max_results)
    return get_videos(service, None, None, max_results=max_results, *ids)


def get_playlist_video_ids(service: Resource, id: str, max_results: int = 0) -> List[str]:
    part = 'id,snippet'  #,contentDetails,status'
    items = service.playlistItems().list(part=part, playlistId=id, maxResults=max_results or 50).execute()
    videos = []
    while 'items' in items:
        videos.extend([item for item in items['items']])
        if 'nextPageToken' not in items or (max_results and max_results < len(videos)):
            return [v['snippet']['resourceId']['videoId'] for v in videos]
        page_token = items['nextPageToken']
        items = service.playlistItems().list(maxResults=max_results - len(videos) if max_results else 50,
                                             part=part, playlistId=id, pageToken=page_token).execute()
    return [v['snippet']['resourceId']['videoId'] for v in videos]
