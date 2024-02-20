from django.test import TestCase
from django.contrib.auth.models import Group

class GroupTestCase(TestCase):
    def test_groups_created(self):
        """Test that user groups are created."""
        expected_groups = ['Admin', 'Moderator', 'Free User', 'Plus Subscriber', 'Gold Subscriber', 'VIP Subscriber']
        for group_name in expected_groups:
            with self.subTest(group_name=group_name):
                self.assertTrue(Group.objects.filter(name=group_name).exists(), f"{group_name} group not found")
