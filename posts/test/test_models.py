
from datetime import date

from django.test import TestCase
from django.contrib.auth import get_user_model

from ..models import Tag, Question
from authors.models import Profile

class TestQuestiongManager(TestCase):
    fixtures = ["./fixtures/postings.json", ]
