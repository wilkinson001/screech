from unittest import TestCase, mock

from app.file_parser import FileParser, ValidationError


class FileParseTestCase(TestCase):
    def test_init(self):
        infile = "test_file"
        table = "test_table"
        session = "session"
        fp = FileParser(infile, table, session)
        self.assertEqual(fp.attrs["file"], infile)
        self.assertEqual(fp.attrs["table"], table)
        self.assertEqual(fp.session, session)

    @mock.patch("os.path")
    def test_parse_file_type(self, mock_os):
        mock_os.isfile.return_value = True
        mock_os.split.return_value = ("path_head", "path_tail.csv")
        infile = "/path_head/path_tail.csv"
        intable = "table"
        session = "session"
        fp = FileParser(infile, intable, session)
        fp.parse_file_type()
        self.assertEqual(fp.attrs["file_name"], "path_tail")
        self.assertEqual(fp.attrs["file_ext"], "csv")
        self.assertEqual(fp.attrs["file_path"], "path_head")

    @mock.patch("os.path")
    def test_parse_file_type_fail(self, mock_os):
        mock_os.isfile.side_effect = [False, True]
        mock_os.split.return_value = ("not", "a file")
        infile = "/path_head/path_tail.csv"
        intable = "table"
        session = "session"
        fp = FileParser(infile, intable, session)
        self.assertRaises(ValidationError, fp.parse_file_type)
        self.assertRaises(ValidationError, fp.parse_file_type)


if __name__ == "__main__":
    unittest.main()
