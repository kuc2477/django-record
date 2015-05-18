from django.test import TestCase

from random import randint, uniform
from faker import Faker

from .models import TITLE_MAX_LENGTH, POINT_MAX_LENGTH, TEXT_MAX_LENGTH
from .models import Article, Comment, Vote, CommentRecord


f = Faker()


class MixinTest(TestCase):
    def setUp(self):
        article = Article.objects.create(
            title=f.lorem()[:TITLE_MAX_LENGTH]
        )

        comment = Comment.objects.create(
            article=article,
            point=f.lorem()[POINT_MAX_LENGTH],
            text=f.lorem()[TEXT_MAX_LENGTH],
            impact=randint(0, 10),
            impact_rate=uniform(0, 1)
        )

        vote = Vote.objects.create(
            comment=comment,
            score = randint(0, 10)
        )

    def tearDown(self):
        Article.objects.all().delete()

    def test_record_on_creation(self):
        vote = Vote.objects.first()
        self.assertTrue(vote.records.exists())

    def test_changed_save_recording(self):
        vote = Vote.objects.first()

        score_before_save = vote.score
        number_of_records_before_save = vote.records.count()

        vote.score = 999
        vote.save()

        r = vote.records.latest()

        self.assertEqual(
            number_of_records_before_save + 1,
            vote.records.count()
        )
        self.assertEqual(vote.score, r.score)

    def test_unchanged_save_recording(self):
        vote = Vote.objects.first()

        number_of_records_before_save = vote.records.count()
        vote.save()

        self.assertEqual(
            number_of_records_before_save, vote.records.count()
        )

    def test_indirect_effect_recording_on_reverse_related_changed_save(self):
        vote = Vote.objects.first()
        comment = vote.comment

        number_of_records_before_save = vote.records.count()
        reverse_related_property_before_save = vote.reverse_related_property

        comment.point = 'changed point in relative'
        comment.text = 'changed text in relative'
        comment.save()

        r = vote.records.latest()

        self.assertEqual(
            number_of_records_before_save + 1,
            vote.records.count()
        )
        self.assertEqual(
            vote.reverse_related_property,
            r.reverse_related_property
        )

    def test_indirect_effect_recording_on_reverse_related_unchanged_save(self):
        vote = Vote.objects.first()
        comment = vote.comment

        number_of_records_before_save = vote.records.count()
        comment.save()

        self.assertEqual(number_of_records_before_save, vote.records.count())
