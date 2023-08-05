import unittest
from ginsfsm.gmsg import (
    GMsg,
#    GMsgError,
#    SegmError
)


class TestGMsg(unittest.TestCase):
    def setUp(self):
        self.gmsg = GMsg(3, 5)

    def test_getdata_half(self):
        self.gmsg.putdata("123ab")
        data = self.gmsg.getdata(3)
        self.assertEqual(data, b"123")
        data = self.gmsg.getdata(3)
        self.assertEqual(data, b"ab")
        data = self.gmsg.getdata(3)
        self.assertEqual(data, None)

        data = self.gmsg.reset_rd()
        data = self.gmsg.getdata(3)
        self.assertEqual(data, b"123")

    def test_getdata_full(self):
        self.gmsg.putdata("123ab")
        data = self.gmsg.getdata(5)
        self.assertEqual(data, b"123ab")

    def test_getdata_all(self):
        self.gmsg.putdata("1234567890abcde")

    def test_getchar(self):
        self.gmsg.putdata("123ab")
        for char in "123ab":
            self.assertEqual(self.gmsg.getchar(), ord(char))
        self.assertEqual(self.gmsg.getchar(), None)

    def test_check_char(self):
        self.gmsg.putdata("123ab")
        for char in "123ab":
            self.assertEqual(self.gmsg.check_char(), ord('1'))

    def test_cur_seg_rd(self):
        self.gmsg.putdata("123ab")
        data = self.gmsg.cur_seg_rd()
        self.assertEqual(data, bytearray(b"123"))

    def test_insert_data_full(self):
        self.gmsg.putdata("123ab")
        ret = self.gmsg.insert_data("x")
        self.assertFalse(ret)

    def test_insert_data_half(self):
        self.gmsg.putdata("12")
        ret = self.gmsg.insert_data("x")
        self.assertTrue(ret)

        data = self.gmsg.cur_seg_rd()
        self.assertEqual(data, bytearray(b"x12"))
        self.assertEqual(data, b"x12")

    def test_mark_and_overwrite(self):
        self.gmsg.putdata("12")
        self.gmsg.mark_pos_write()
        self.gmsg.putdata("3abx")
        marked_bytes_len = self.gmsg.marked_bytes()
        self.assertEqual(marked_bytes_len, 3)

        self.gmsg.overwrite_data("qwerty")
        data = self.gmsg.getdata(20)
        self.assertEqual(data, b"12qwe")
        marked_count = self.gmsg.marked_bytes()
        self.assertEqual(marked_count, 0)

    def test_bytesleft(self):
        self.gmsg.putdata("12")
        count = self.gmsg.bytesleft()
        self.assertEqual(count, 2)
        self.gmsg.putdata("abcd")
        count = self.gmsg.bytesleft()
        self.assertEqual(count, 5)
        self.gmsg.getdata(2)
        count = self.gmsg.bytesleft()
        self.assertEqual(count, 3)
        self.gmsg.getdata(12)
        count = self.gmsg.bytesleft()
        self.assertEqual(count, 0)

    def test_totalbytes(self):
        self.gmsg.putdata("12")
        count = self.gmsg.totalbytes()
        self.assertEqual(count, 2)
        count = self.gmsg.freebytes()
        self.assertEqual(count, 3)
        self.gmsg.putdata("abcd")
        count = self.gmsg.bytesleft()
        self.assertEqual(count, 5)
        count = self.gmsg.freebytes()
        self.assertEqual(count, 0)

    def test_no_circular(self):
        # fill the buffer
        count = self.gmsg.putdata("123")
        self.assertEqual(count, 3)

        count = self.gmsg.totalbytes()
        self.assertEqual(count, 3)
        count = self.gmsg.freebytes()
        self.assertEqual(count, 2)

        count = self.gmsg.putdata("456")
        self.assertEqual(count, 2)

        count = self.gmsg.totalbytes()
        self.assertEqual(count, 5)
        count = self.gmsg.freebytes()
        self.assertEqual(count, 0)

        # pull all the buffer
        data = self.gmsg.getdata(3)
        self.assertEqual(data, bytearray(b"123"))
        data = self.gmsg.getdata(3)
        self.assertEqual(data, bytearray(b"45"))

        count = self.gmsg.bytesleft()
        self.assertEqual(count, 0)

        count = self.gmsg.totalbytes()
        self.assertEqual(count, 5)
        count = self.gmsg.freebytes()
        self.assertEqual(count, 0)
