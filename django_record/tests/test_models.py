from django.test import TestCase

from random import randint, uniform
from faker import Faker

from .models import Article, Comment, CommentRecord


f = Faker()


class ModelTest(TestCase):
    def setUp(self):
        article = Article.objects.create(
            title=f.lorem()[:Article.TITLE_MAX_LENGTH]
        )

        comment = Comment.objects.create(
            article=article,
            point=f.lorem()[Comment.POINT_MAX_LENGTH],
            text=f.lorem()[Comment.TEXT_MAX_LENGTH],
            impact=randint(0, 10),
            impact_rate=uniform(0, 1)
        )

    def test_record_on_creation(self):
        self.assertTrue(CommentRecord.objects.exists())
