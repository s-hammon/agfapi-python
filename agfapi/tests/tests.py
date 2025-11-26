import unittest
from unittest.mock import patch

from agfapi import get_worklist

class TestGetWorklist(unittest.TestCase):

    @patch("agfapi._exec_cmd")
    def test_get_worklist_valid_json(self, mock_exec):
        mock_exec.return_value = iter([
            '{"id": "wl-123", "status": "active"}'
        ])

        result = get_worklist("wl-123")
        self.assertEqual(result["id"], "wl-123")
        self.assertEqual(result["status"], "active")

    @patch("agfapi._exec_cmd")
    def test_get_worklist_invalid_json(self, mock_exec):
        mock_exec.return_value = iter([
            "not json"
        ])

        with self.assertRaises(RuntimeError) as ctx:
            get_worklist("wl-555")

        msg = str(ctx.exception)
        self.assertIn("not json", msg)
        self.assertIn("wl-555", msg)

    @patch("agfapi._exec_cmd")
    def test_get_worklist_command_failure(self, mock_exec):
        mock_exec.side_effect = Exception("agfapi command failed")

        with self.assertRaises(Exception) as ctx:
            get_worklist("wl-999")

        self.assertIn("agfapi command failed", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
