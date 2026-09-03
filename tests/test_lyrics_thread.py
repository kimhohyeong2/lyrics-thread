import unittest

from lyrics_thread import analyze_sentence


class LyricsThreadTest(unittest.TestCase):
    def test_korean_condition(self):
        result = analyze_sentence("네가 돌아오면 나는 기다릴게")
        self.assertEqual(result[0].pattern_id, "ko.condition_response")

    def test_korean_reversal(self):
        result = analyze_sentence("영원할 거라고 생각했지만 너는 떠났어")
        self.assertEqual(result[0].pattern_id, "ko.expectation_reversal")

    def test_japanese_condition(self):
        result = analyze_sentence("君が笑うなら僕は歌う")
        self.assertEqual(result[0].pattern_id, "ja.condition_response")

    def test_english_condition(self):
        result = analyze_sentence("If you stay, I will stay")
        self.assertEqual(result[0].pattern_id, "en.condition_response")

    def test_unknown(self):
        self.assertEqual(analyze_sentence("오늘은 날씨가 좋다"), [])


if __name__ == "__main__":
    unittest.main()
