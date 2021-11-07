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

    def test_get_videos(self) -> None:
        youtube = YouTube('youtube-oath2-credentials.json', 'my-oauth2.json')
        channel = youtube.channel('UCo_fg5ZyCCHt75ryUUa6ebw')



if __name__ == '__main__':
    unittest.main()