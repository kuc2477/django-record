from django.test import TestCase

from random import randint, uniform
from faker import Faker

from .models import TITLE_MAX_LENGTH, POINT_MAX_LENGTH, TEXT_MAX_LENGTH
from .models import Article, Comment, Vote


f = Faker()


class ModelTest(TestCase):
    def setUp(self):
        article = Article.objects.create(
            title=f.text()[:TITLE_MAX_LENGTH]
        )

        comment = Comment.objects.create(
            article=article,
            point=f.text()[:POINT_MAX_LENGTH],
            text=f.text()[:TEXT_MAX_LENGTH],
            impact=randint(0, 10),
            impact_rate=uniform(0, 1)
        )

        Vote.objects.create(
            comment=comment,
            score=randint(0, 10)
        )

    def tearDown(self):
        Article.objects.all().delete()

    def test_record_on_creation(self):
        comment = Comment.objects.first()
        self.assertTrue(comment.records.exists())

    def test_changed_save_recording(self):
        comment = Comment.objects.first()

        number_of_records_before_save = comment.records.count()
        comment.text = 'changed text'
        comment.save()

        self.assertEqual(
            number_of_records_before_save + 1, comment.records.count()
        )
        self.assertEqual(comment.text, comment.records.latest().text)

    def test_unchanged_save_recording(self):
        comment = Comment.objects.first()

        number_of_records_before_save = comment.records.count()
        comment.save()

        self.assertEqual(
            number_of_records_before_save, comment.records.count()
        )

    def test_indirect_effect_recording_on_related_changed_save(self):
        comment = Comment.objects.first()
        vote = comment.votes.first()

        related_property_value_before_save = comment.related_property
        number_of_records_before_save = comment.records.count()
        vote.score = vote.score + 999
        vote.save()

        self.assertEqual(
            number_of_records_before_save + 1, comment.records.count()
        )
        self.assertEqual(
            related_property_value_before_save + 999,
            comment.records.latest().related_property
        )

    def test_indirect_effect_recording_on_related_unchanged_save(self):
        comment = Comment.objects.first()
        vote = comment.votes.first()

        number_of_records_before_save = comment.records.count()
        vote.save()

        self.assertEqual(
            number_of_records_before_save, comment.records.count()
        )

    def test_indirect_effect_recording_on_reverse_related_changed_save(self):
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
            comment.records.latest().reverse_related_property
        )

    def test_indirect_effect_recording_on_reverse_related_unchanged_save(self):
        comment = Comment.objects.first()
        article = comment.article

        number_of_records_before_save = comment.records.count()
        article.save()

        self.assertEqual(
            number_of_records_before_save, comment.records.count()
        )
