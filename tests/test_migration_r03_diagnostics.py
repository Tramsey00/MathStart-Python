"""Product child-output privacy survives retirement of the development runner."""
import unittest

from scripts.verification_diagnostics import MAX_DIAGNOSTIC_CHARS, safe_diagnostic


class DiagnosticTests(unittest.TestCase):
    def test_sensitive_lines_redacted_before_truncation(self):
        for value in ("api_key=private", "password=private", "Authorization: Bearer private",
                      "token:private", "postgresql://private", "Set-Cookie: sessionid=private",
                      "dsn=private"):
            self.assertEqual(safe_diagnostic("start\n" + value + "\nend\n"),
                             "start\n[redacted sensitive line]\nend\n")

    def test_output_bounded_and_non_sensitive_text_retained(self):
        self.assertEqual(safe_diagnostic("failure: route mismatch\n"), "failure: route mismatch\n")
        self.assertEqual(safe_diagnostic("x" * (MAX_DIAGNOSTIC_CHARS + 1)),
                         "x" * MAX_DIAGNOSTIC_CHARS + "\n[output truncated]\n")


if __name__ == "__main__":
    unittest.main()
