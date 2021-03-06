import unittest, sys, os

from datetime import timedelta

from lumos.buddy_log_entry import BuddyLogEntry

USER_ID = 1
START_TIME = 12345
END_TIME = 24689
MSGS_USER = 15
MSGS_BUDDY = 27

class TestBuddyLogEntry(unittest.TestCase):

    def setUp(self):
        self.entry = BuddyLogEntry(user_id=USER_ID, buddy_sn='someusername',
            buddy_id=USER_ID + 1, size=((MSGS_USER + MSGS_BUDDY) * 100),
            cumu_msgs_ct=(MSGS_USER + MSGS_BUDDY),
            msgs_user=MSGS_USER, msgs_buddy=MSGS_BUDDY, start_time=START_TIME,
            end_time=END_TIME, timestamp=START_TIME)

    def test_expected_values(self):
        self.assertEqual(END_TIME - START_TIME, self.entry.duration())
        self.assertEqual(MSGS_USER + MSGS_BUDDY, self.entry.msg_ct())

        delta = self.entry.pretty_end_time() - self.entry.pretty_start_time()
        expected_seconds = END_TIME - START_TIME

        self.assertEqual(timedelta(0, expected_seconds), delta)

