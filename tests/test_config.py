import unittest
import os
import yaml
from src.config import load_config

class TestConfig(unittest.TestCase):

    def test_load_config_templates_should_fail_initially(self):
        # This test is designed to fail initially because the 'templates' key
        # is not yet present in the main config.yaml or is not structured correctly.
        config = load_config("config.yaml") # Load the actual config.yaml
        self.assertIn("templates", config, "The 'templates' key should be present in config.yaml")
        self.assertIsInstance(config["templates"], list, "The 'templates' value should be a list")
        # Add more assertions that will fail if the structure isn't there
        self.assertGreater(len(config["templates"]), 0, "There should be at least one template defined")

    def test_load_config_defaults(self):
        # This test will continue to check defaults from the actual config.yaml
        config = load_config("config.yaml")
        self.assertIn("defaults", config)
        self.assertEqual(config["defaults"]["resume_template"], "modern")
        self.assertEqual(config["defaults"]["cover_letter_template"], "standard")