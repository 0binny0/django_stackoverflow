
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase

from ..models import Tag, Question
from ..serializers import TagSerializer
from authors.models import Profile


class TestQuestionTagAdded(APITestCase):
    '''Verify that a Question cannot have more than 4 tags.'''

    fixtures = ["exceed_tag_limit.json", ]

    @classmethod
    def setUpTestData(cls):
        cls.serializer1 = TagSerializer(
            data={"name": ["Tag1", "Tag2", "Tag3", "Tag4", "Tag5"]}
        )
        cls.serializer2 = TagSerializer(
            data={"name": ["Tag1", "Tag2", "Tag3", "Tag4"]}
        )

    def test_question_tag_limit_exceeded(self):
        self.assertFalse(self.serializer1.is_valid())
        self.assertEqual(
            str(self.serializer1.errors['name'][0]),
            "Tag limit exceeded: 4 tags per question"
        )

    def test_question_tag_limit_permitted(self):
        self.assertTrue(self.serializer2.is_valid())
        self.assertEqual(
            self.serializer2.validated_data['name'],
            ["Tag1", "Tag2", "Tag3", "Tag4"]
        )
