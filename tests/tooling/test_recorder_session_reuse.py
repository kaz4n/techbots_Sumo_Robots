# Keeps a rejected parser terminal even if a caller feeds a later valid stream.
# First-error identity must survive accidental reuse; no retry or resynchronization.
# Uses literal v1 fixtures offline and preserves all earlier receiver test oracles.
import importlib
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tools'))
from tests.tooling.test_dump_match import wire

class RecorderSessionReuseTests(unittest.TestCase):
    def test_first_mismatch_is_sticky_across_later_feed_and_finish(self):
        module=importlib.import_module('dump_match')
        parser=module.Parser(expected_session=123456789)
        with self.assertRaises(module.CaptureError) as first:
            parser.feed(wire(session=202472))
        for data in (wire(session=123456789),wire(session=55),b'',b'garbage\n'):
            with self.assertRaises(module.CaptureError) as repeated:
                parser.feed(data)
            self.assertIs(repeated.exception,first.exception)
        with self.assertRaises(module.CaptureError) as final:
            parser.finish()
        self.assertIs(final.exception,first.exception)
        self.assertEqual((parser.expected_session,parser.observed_session,parser.rejected_session),
                         (123456789,202472,202472))

if __name__=='__main__':unittest.main()
