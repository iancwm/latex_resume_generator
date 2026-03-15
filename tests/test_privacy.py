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

    def test_list_item_privacy_override(self):
        data = {
            "work": [
                {
                    "company": "Public Corp",
                    "position": {"value": "Secret Agent", "private": True}
                },
                {
                    "company": {"value": "Hidden Ltd", "private": False},
                    "position": "Analyst"
                }
            ]
        }
        # default_private=False for public work data
        redacted = redact_data(data, is_redaction_mode=True, default_private=False)
        
        self.assertEqual(redacted["work"][0]["company"], "Public Corp")
        self.assertEqual(redacted["work"][0]["position"], "REDACTED: POSITION")
        self.assertEqual(redacted["work"][1]["company"], "Hidden Ltd")
        self.assertEqual(redacted["work"][1]["position"], "Analyst")

if __name__ == '__main__':
    unittest.main()
