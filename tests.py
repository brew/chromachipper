import unittest

from chromachipper import get_colours_from_message


class ColoursFromMessageTest(unittest.TestCase):

    def test_three_char_css_style_hex(self):
        self.assertEqual(get_colours_from_message("#0ef"), ['#00eeff'])

    def test_three_char_nix_style_hex(self):
        self.assertEqual(get_colours_from_message("0x0ef"), ['#00eeff'])

    def test_six_char_css_style_hex(self):
        self.assertEqual(get_colours_from_message("#663399"), ['#663399'])

    def test_six_char_nix_style_hex(self):
        self.assertEqual(get_colours_from_message("0x663399"), ['#663399'])

    def test_mixed_message_css_style(self):
        self.assertEqual(get_colours_from_message("Colour in a #ff0000 mixed message"), ['#ff0000'])

    def test_mixed_message_nix_style(self):
        self.assertEqual(get_colours_from_message("Colour in a 0xff0000 mixed message"), ['#ff0000'])

    def test_malformed(self):
        self.assertEqual(get_colours_from_message("#d00#bar"), ['#dd0000'])

    def test_multiple_colours_in_mixed_message_css_style(self):
        self.assertEqual(get_colours_from_message("Muliple colours! #0ff, #ff000 #00ff00. #d00#bar"), ['#00ffff', '#00ff00', '#dd0000'])

    def test_multiple_colours_in_mixed_message_nix_style(self):
        self.assertEqual(get_colours_from_message("Muliple colours! 0x0ff, 0xff000 0x00ff00. 0xd000xbar"), ['#00ffff', '#00ff00', '#dd0000'])

    def test_multiple_colours_mixed_styles(self):
        self.assertEqual(get_colours_from_message("0x0ff, #ff000 0x00ff00. 0xd00 #234234"), ['#00ffff', '#00ff00', '#dd0000', '#234234'])

    def test_no_colours_in_message(self):
        self.assertEqual(get_colours_from_message("No colours in this message :("), [])
