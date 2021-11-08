from os import PathLike
from typing import List, Union

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


def error_msg(client_secrect_file: str) -> str:
    # This variable defines a message to display if the CLIENT_SECRETS_FILE is
    # missing.
    return f"""
    WARNING: Please configure OAuth 2.0

    To make this sample run you will need to populate the client_secrets.json file
    found at:

       {client_secrect_file}

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
    channels = service.channels().list(maxResults=max_results if max_results else 50, **params).execute()
    results = []
    while True:
        if 'items' not in channels:
            return results
        results.extend([item for item in channels['items']])
        if 'pageToken' not in channels or (max_results and max_results < len(results)):
            return results
        page_token = channels['pageToken']
        channels = service.channels().list(maxResults=max_results - len(results) if max_results else 50, **params,
                                           pageToken=page_token).execute()


def get_playlists(service: Resource,
                  channel_id: str = None,
                  playlist_id: str = None,
                  max_results: int = 0) -> List[dict]:
    params = {'part': 'contentDetails,snippet,status,player,localizations'}
    if channel_id:
        params['channelId'] = channel_id
    elif playlist_id:
        params['id'] = playlist_id
    playlists = service.playlists().list(maxResults=max_results if max_results else 50, **params).execute()
    results = []
    while True:
        results.extend([item for item in playlists['items']])
        if 'pageToken' not in playlists or (max_results and max_results < len(results)):
            return results
        page_token = playlists['nextPageToken']
        playlists = service.playlists().list(maxResults=max_results - len(results) if max_results else 50,
                                             pageToken=page_token, **params).execute()


def get_videos(service: Resource,
               channel_id: str = None,
               playlist_id: str = None,
               max_results: int = 0) -> List[dict]:
    params = {'part': 'id,snippet,contentDetails,fileDetails,player,processingDetails,'
                      'recordingDetails,statistics,status,suggestions,topicDetails'}
    results = []
    if channel_id:
        params['channelId'] = channel_id
    elif playlist_id:
        params['id'] = playlist_id


def get_video(service: Resource, id: str) -> dict:
    videos = service.videos().list(maxResults=1, id=id)
    return videos['items'][0] if 'items' in videos else None
