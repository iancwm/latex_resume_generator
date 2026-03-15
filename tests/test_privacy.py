import unittest
from src.engine import redact_data

class TestPrivacy(unittest.TestCase):
    def test_redact_basic_strings(self):
        data = {"name": "Jane", "email": "jane@example.com"}
        # redact_data currently redacts all strings it sees
        redacted = redact_data(data)
        self.assertEqual(redacted["name"], "REDACTED: NAME")
        self.assertEqual(redacted["email"], "REDACTED: EMAIL")

    def test_privacy_override_public(self):
        # Spec: Ability to mark a field as private: false to override defaults
        data = {
            "name": "Jane",
            "email": {"value": "jane@example.com", "private": False}
        }
        # We need to update redact_data to handle this
        redacted = redact_data(data)
        self.assertEqual(redacted["name"], "REDACTED: NAME")
        self.assertEqual(redacted["email"], "jane@example.com")

    def test_privacy_override_private(self):
        # Spec: Ability to mark a field as private: true
        # Even if we call it on data that wouldn't normally be redacted (if we change the logic)
        data = {
            "company": {"value": "Tech Corp", "private": True}
        }
        redacted = redact_data(data)
        self.assertEqual(redacted["company"], "REDACTED: COMPANY")

    def test_nested_privacy_override(self):
        data = {
            "basics": {
                "location": {
                    "city": {"value": "San Francisco", "private": False},
                    "region": "CA"
                }
            }
        }
        redacted = redact_data(data)
        self.assertEqual(redacted["basics"]["location"]["city"], "San Francisco")
        self.assertEqual(redacted["basics"]["location"]["region"], "REDACTED: REGION")

if __name__ == '__main__':
    unittest.main()
