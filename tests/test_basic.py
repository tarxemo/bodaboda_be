from django.test import TestCase

class BasicTest(TestCase):
    def test_math_works(self):
        """A simple test to verify the CI pipeline works."""
        self.assertEqual(1 + 1, 2)

    def test_app_exists(self):
        """Verify the project is set up correctly."""
        from django.conf import settings
        self.assertIsNotNone(settings.SECRET_KEY)
