import unittest

from easytube import YouTube


class MyTestCase(unittest.TestCase):
    def test_get_channel(self) -> None:
        youtube = YouTube('youtube-oath2-credentials.json', 'my-oauth2.json')
        self.assertIsNone(youtube.channel('UCo_fg5ZyCCHt75ryUUa6ebwa'))
        channel = youtube.channel('UCo_fg5ZyCCHt75ryUUa6ebw')
        self.assertEqual(channel.title, 'A Smart Code')
        self.assertEqual(channel.url, 'https://www.youtube.com/channel/UCo_fg5ZyCCHt75ryUUa6ebw')
        channel = youtube.channel_from_url('https://www.youtube.com/channel/UCo_fg5ZyCCHt75ryUUa6ebw/about')
        self.assertEqual(channel.title, 'A Smart Code')

    def test_get_playlists(self) -> None:
        youtube = YouTube('youtube-oath2-credentials.json', 'my-oauth2.json')
        channel = youtube.channel('UCo_fg5ZyCCHt75ryUUa6ebw')
        self.assertGreaterEqual(len(channel.playlists), 4)
        self.assertEqual(youtube.playlist('PLmf8nIhY4ISvHi1tUiZqEYjEiI185nzJH').title, 'Programación')

    def test_get_videos(self) -> None:
        youtube = YouTube('youtube-oath2-credentials.json', 'my-oauth2.json')
        playlist = youtube.playlist('PLmf8nIhY4ISvHi1tUiZqEYjEiI185nzJH')
        self.assertGreaterEqual(playlist.num_videos, 26)
        print(playlist.videos)



if __name__ == '__main__':
    unittest.main()
