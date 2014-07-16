import copy
import unittest

from tweepy import Status, API

from chromachipper import get_colours_from_message
from twitter import ChromachipStreamListener


class MockAPI():

    def __init__(self, *args, **kwargs):
        self.last_status = None
        self.last_reply_to = None

    def update_with_media(self, reply_to, status, *args, **kwargs):
        self.last_reply_to = reply_to
        self.last_status = status


class ColoursFromMessageTest(unittest.TestCase):

    def test_three_char_css_style_hex(self):
        self.assertEqual(get_colours_from_message("#0ef"), [['#00eeff']])

    def test_three_char_nix_style_hex(self):
        self.assertEqual(get_colours_from_message("0x0ef"), [['#00eeff']])

    def test_six_char_css_style_hex(self):
        self.assertEqual(get_colours_from_message("#663399"), [['#663399']])

    def test_six_char_nix_style_hex(self):
        self.assertEqual(get_colours_from_message("0x663399"), [['#663399']])

    def test_mixed_message_css_style(self):
        self.assertEqual(get_colours_from_message("Colour in a #ff0000 mixed message"), [['#ff0000']])

    def test_mixed_message_nix_style(self):
        self.assertEqual(get_colours_from_message("Colour in a 0xff0000 mixed message"), [['#ff0000']])

    def test_malformed(self):
        self.assertEqual(get_colours_from_message("#d00#bar"), [['#dd0000']])

    def test_multiple_colours_in_mixed_message_css_style(self):
        self.assertEqual(get_colours_from_message("Muliple colours! #0ff, #ff000 #00ff00. #d00#bar"), [['#00ffff', '#00ff00', '#dd0000']])

    def test_multiple_colours_in_mixed_message_nix_style(self):
        self.assertEqual(get_colours_from_message("Muliple colours! 0x0ff, 0xff000 0x00ff00. 0xd000xbar"), [['#00ffff', '#00ff00', '#dd0000']])

    def test_multiple_colours_mixed_styles(self):
        self.assertEqual(get_colours_from_message("0x0ff, #ff000 0x00ff00. 0xd00 #234234"), [['#00ffff', '#00ff00', '#dd0000', '#234234']])

    def test_no_colours_in_message(self):
        self.assertEqual(get_colours_from_message("No colours in this message :("), [])

    def test_line_breaks_no_colours_in_message(self):
        self.assertEqual(get_colours_from_message("There\nare\nlinebreaks!"), [])

    def test_line_breaks_in_message(self):
        self.assertEqual(get_colours_from_message("#ff0000\n#00ff00\n#0000ff"), [['#ff0000'], ['#00ff00'], ['#0000ff']])

    def test_line_breaks_in_message_multiple_colours(self):
        self.assertEqual(get_colours_from_message("#ff0000 #123123\n#00ff00\n#0000ff"), [['#ff0000', '#123123'], ['#00ff00'], ['#0000ff']])

    def test_line_breaks_in_mixed_message_multiple_colours(self):
        self.assertEqual(get_colours_from_message("#ff0000 A line with two colours #123123\nA line without colours\nA line with a colour #0000ff"), [['#ff0000', '#123123'], ['#0000ff']])


class StreamListenerTest(unittest.TestCase):

    def setUp(self):
        status_base_obj = {
            u'contributors': None,
            u'truncated': False,
            u'in_reply_to_status_id': None,
            u'id': 487394915643842560,
            u'retweeted': False,
            u'entities': {
                u'symbols': [],
                u'hashtags': [{u'indices': [97, 104], u'text': u'00b9f1'}],
                u'urls': []},
            u'in_reply_to_screen_name': u'chromachipper',
            u'id_str': u'487394915643842560',
            u'in_reply_to_user_id': 00000000,
            u'user': {
                u'id': 725633,
                u'id_str': u'725633',
                u'screen_name': u'IWantToGive',
                u'name': u'I am a Giver',
            },
        }
        status_with_mentions_obj = copy.deepcopy(status_base_obj)
        status_with_mentions_obj['text'] = u'@chromachipper what about if I mention another account. Can I gift someone a colour? @GiftToMe #00b9f1'
        status_with_mentions_obj['entities']['user_mentions'] = [
            {u'id': 00000000, u'indices': [0, 14], u'id_str': u'00000000', u'screen_name': u'chromachipper', u'name': u'Chroma Chipper'},
            {u'id': 11111111, u'indices': [85, 96], u'id_str': u'11111111', u'screen_name': u'GiftToMe', u'name': u'Gift Tome'},
            {u'id': 22222222, u'indices': [85, 96], u'id_str': u'22222222', u'screen_name': u'GiftToMeToo', u'name': u'Gift Tometoo'}
        ]

        status_without_mentions_obj = copy.deepcopy(status_base_obj)
        status_without_mentions_obj['text'] = u'@chromachipper send me a Chroma Chip! #00b9f1'
        status_without_mentions_obj['entities']['user_mentions'] = [
            {u'id': 00000000, u'indices': [0, 14], u'id_str': u'00000000', u'screen_name': u'chromachipper', u'name': u'Chroma Chipper'}
        ]

        self.api = MockAPI()
        self.status_with_mentions = Status.parse(api=API(), json=status_with_mentions_obj)
        self.status_without_mentions = Status.parse(api=API(), json=status_without_mentions_obj)

    def test_on_status_with_mentions(self):
        listener = ChromachipStreamListener(api=self.api, twitter_id=00000000)
        listener.on_status(self.status_with_mentions)
        self.assertEqual(self.api.last_status, u"@IWantToGive sent you a Chroma Chip! @GiftToMe @GiftToMeToo")

    def test_on_status_without_mentions(self):
        listener = ChromachipStreamListener(api=self.api, twitter_id=00000000)
        listener.on_status(self.status_without_mentions)
        self.assertNotEqual(self.api.last_status, u"@IWantToGive sent you a Chroma Chip! @GiftToMe @GiftToMeToo")
        self.assertTrue(self.api.last_status.replace("@IWantToGive ", "") in ChromachipStreamListener.REPLIES)


class MentionsReplyLengthTest(unittest.TestCase):

    def setUp(self):
        self.status_base_obj = {
            u'contributors': None,
            u'truncated': False,
            u'in_reply_to_status_id': None,
            u'id': 487394915643842560,
            u'retweeted': False,
            u'entities': {
                u'symbols': [],
                u'hashtags': [{u'indices': [97, 104], u'text': u'00b9f1'}],
                u'urls': []},
            u'in_reply_to_screen_name': u'chromachipper',
            u'id_str': u'487394915643842560',
            u'in_reply_to_user_id': 00000000,
            u'user': {
                u'id': 725633,
                u'id_str': u'725633',
                u'screen_name': u'IWantToGift2U',
                u'name': u'I am a Giver',
            },
        }

        self.api = MockAPI()

    def test_longreply_with_mentions(self):
        """
        A reply from chromachipper of 140 characters uses the correct reply
        text.
        """

        # This will cause chromachipper to create a reply of 140 chars with long reply text.
        status_140_char_obj = copy.deepcopy(self.status_base_obj)
        status_140_char_obj['text'] = u'@chromachipper #000 @abcdefghijklmno @pqrstuvwxyzabcd @efghijklmnopqur @stuvqxyzabcdefg @hijklmnopqrstuv @wxyzabcdefghijk'
        status_140_char_obj['entities']['user_mentions'] = [
            {u'id': 00000000, u'indices': [0, 14], u'id_str': u'00000000', u'screen_name': u'chromachipper', u'name': u'Chroma Chipper'},
            {u'id': 11111111, u'indices': [85, 96], u'id_str': u'11111111', u'screen_name': u'abcdefghijklmno', u'name': u'abcdefghijklmno'},
            {u'id': 22222222, u'indices': [85, 96], u'id_str': u'22222222', u'screen_name': u'pqrstuvwxyzabcd', u'name': u'pqrstuvwxyzabcd'},
            {u'id': 33333333, u'indices': [85, 96], u'id_str': u'33333333', u'screen_name': u'efghijklmnopqur', u'name': u'efghijklmnopqur'},
            {u'id': 44444444, u'indices': [85, 96], u'id_str': u'44444444', u'screen_name': u'stuvqxyzabcdefg', u'name': u'stuvqxyzabcdefg'},
            {u'id': 55555555, u'indices': [85, 96], u'id_str': u'55555555', u'screen_name': u'hijklmnopqrstuv', u'name': u'hijklmnopqrstuv'},
            {u'id': 66666666, u'indices': [85, 96], u'id_str': u'66666666', u'screen_name': u'wxyzabcdefghijk', u'name': u'wxyzabcdefghijk'},
        ]
        status_140_char = Status.parse(api=API(), json=status_140_char_obj)

        listener = ChromachipStreamListener(api=self.api, twitter_id=00000000)
        listener.on_status(status_140_char)

        self.assertEqual(self.api.last_status, u"@IWantToGift2U sent you a Chroma Chip! @abcdefghijklmno @pqrstuvwxyzabcd @efghijklmnopqur @stuvqxyzabcdefg @hijklmnopqrstuv @wxyzabcdefghijk")
        self.assertEqual(len(self.api.last_status), 140)

    def test_shortreply_with_mentions(self):
        """
        A reply from chromachipper uses the short reply where necessary.
        """

        # This will cause chromachipper to create a reply with short reply text.
        status_morethan140_char_obj = copy.deepcopy(self.status_base_obj)
        status_morethan140_char_obj['text'] = u'@chromachipper #000 @abcdefghijklmno @pqrstuvwxyzabcd @efghijklmnopqur @stuvqxyzabcdefg @hijklmnopqrstuv @wxyzabcdefghijk @ashortreply'
        status_morethan140_char_obj['entities']['user_mentions'] = [
            {u'id': 00000000, u'indices': [0, 14], u'id_str': u'00000000', u'screen_name': u'chromachipper', u'name': u'Chroma Chipper'},
            {u'id': 11111111, u'indices': [85, 96], u'id_str': u'11111111', u'screen_name': u'abcdefghijklmno', u'name': u'abcdefghijklmno'},
            {u'id': 22222222, u'indices': [85, 96], u'id_str': u'22222222', u'screen_name': u'pqrstuvwxyzabcd', u'name': u'pqrstuvwxyzabcd'},
            {u'id': 33333333, u'indices': [85, 96], u'id_str': u'33333333', u'screen_name': u'efghijklmnopqur', u'name': u'efghijklmnopqur'},
            {u'id': 44444444, u'indices': [85, 96], u'id_str': u'44444444', u'screen_name': u'stuvqxyzabcdefg', u'name': u'stuvqxyzabcdefg'},
            {u'id': 55555555, u'indices': [85, 96], u'id_str': u'55555555', u'screen_name': u'hijklmnopqrstuv', u'name': u'hijklmnopqrstuv'},
            {u'id': 66666666, u'indices': [85, 96], u'id_str': u'66666666', u'screen_name': u'wxyzabcdefghijk', u'name': u'wxyzabcdefghijk'},
            {u'id': 77777777, u'indices': [85, 96], u'id_str': u'77777777', u'screen_name': u'ashortreply', u'name': u'ashortreply'},
        ]
        status_140_char = Status.parse(api=API(), json=status_morethan140_char_obj)

        listener = ChromachipStreamListener(api=self.api, twitter_id=00000000)
        listener.on_status(status_140_char)

        self.assertEqual(self.api.last_status, u"@IWantToGift2U sent this! @abcdefghijklmno @pqrstuvwxyzabcd @efghijklmnopqur @stuvqxyzabcdefg @hijklmnopqrstuv @wxyzabcdefghijk @ashortreply")
        self.assertEqual(len(self.api.last_status), 140)

    def test_140_char_shortreply_with_mentions(self):
        """
        A reply from chromachipper uses no reply text where necessary.
        """

        # This will cause chromachipper to create a reply with no reply text.
        status_morethan140_char_obj = copy.deepcopy(self.status_base_obj)
        status_morethan140_char_obj['text'] = u'@chromachipper #000 @abcdefghijklmno @pqrstuvwxyzabcd @efghijklmnopqur @stuvqxyzabcdefg @hijklmnopqrstuv @wxyzabcdefghijk @anoreplymaximum'
        status_morethan140_char_obj['entities']['user_mentions'] = [
            {u'id': 00000000, u'indices': [0, 14], u'id_str': u'00000000', u'screen_name': u'chromachipper', u'name': u'Chroma Chipper'},
            {u'id': 11111111, u'indices': [85, 96], u'id_str': u'11111111', u'screen_name': u'abcdefghijklmno', u'name': u'abcdefghijklmno'},
            {u'id': 22222222, u'indices': [85, 96], u'id_str': u'22222222', u'screen_name': u'pqrstuvwxyzabcd', u'name': u'pqrstuvwxyzabcd'},
            {u'id': 33333333, u'indices': [85, 96], u'id_str': u'33333333', u'screen_name': u'efghijklmnopqur', u'name': u'efghijklmnopqur'},
            {u'id': 44444444, u'indices': [85, 96], u'id_str': u'44444444', u'screen_name': u'stuvqxyzabcdefg', u'name': u'stuvqxyzabcdefg'},
            {u'id': 55555555, u'indices': [85, 96], u'id_str': u'55555555', u'screen_name': u'hijklmnopqrstuv', u'name': u'hijklmnopqrstuv'},
            {u'id': 66666666, u'indices': [85, 96], u'id_str': u'66666666', u'screen_name': u'wxyzabcdefghijk', u'name': u'wxyzabcdefghijk'},
            {u'id': 77777777, u'indices': [85, 96], u'id_str': u'77777777', u'screen_name': u'anoreplymaximum', u'name': u'anoreplymaximum'},
        ]
        status_140_char = Status.parse(api=API(), json=status_morethan140_char_obj)

        listener = ChromachipStreamListener(api=self.api, twitter_id=00000000)
        listener.on_status(status_140_char)

        self.assertEqual(self.api.last_status, u"@IWantToGift2U @abcdefghijklmno @pqrstuvwxyzabcd @efghijklmnopqur @stuvqxyzabcdefg @hijklmnopqrstuv @wxyzabcdefghijk @anoreplymaximum")
