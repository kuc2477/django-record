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
        Comment.objects.create(
            article=article,
            point=f.lorem()[Comment.POINT_MAX_LENGTH],
            text=f.lorem()[Comment.TEXT_MAX_LENGTH],
            impact=randint(0, 10),
            impact_rate=uniform(0, 1)
        )

    def tearDown(self):
        Comment.objects.all().delete()
        Article.objects.all().delete()

    def test_record_on_creation(self):
        self.assertTrue(CommentRecord.objects.exists())

    def test_unchanged_save_recording(self):
        comment = Comment.objects.first()

        number_of_records_before_save = comment.records.count()
        comment.save()

        self.assertEqual(
            number_of_records_before_save, comment.records.count()
        )

    def test_changed_save_recording(self):
        comment = Comment.objects.first()

        number_of_records_before_save = comment.records.count()
        comment.text = 'changed text'
        comment.save()

        self.assertEqual(
            number_of_records_before_save + 1, comment.records.count()
        )
        self.assertEqual(comment.text, comment.records.latest().text)

    def test_indirect_effect_recording(self):
        comment = Comment.objects.first()
        article = comment.article

        number_of_records_before_save = comment.records.count()
        article.title = 'changed text'
        article.save()

        self.assertEqual(
            number_of_records_before_save + 1, comment.records.count()
        )
        self.assertEqual(
            comment.article.title,
            comment.records.latest().related_property
        )
