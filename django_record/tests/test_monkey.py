from django.test import TestCase

from random import randint, uniform
from faker import Faker

from .models import TITLE_MAX_LENGTH, POINT_MAX_LENGTH, TEXT_MAX_LENGTH
from .models import Article, Comment, Vote

f = Faker()


class MonkeyTest(TestCase):
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

        Vote.objects.create(
            comment=comment,
            score=randint(0, 10)
        )

    def tearDown(self):
        Article.objects.all().delete()

    def test_shortcut_monkey_patch_with_record_model(self):
        comment = Comment.objects.first()
        try:
            comment.records_in_hour
            comment.records_in_day
            comment.records_in_week
            comment.records_in_month
            comment.records_in_year
        except Exception as e:
            self.fail(e.message)

    def test_resampling_shortcut_monkey_patch_with_record_model(self):
        comment = Comment.objects.first()
        try:
            comment.resampled_records_in_hour
            comment.resampled_records_in_day
            comment.resampled_records_in_week
            comment.resampled_records_in_month
            comment.resampled_records_in_year
        except Exception as e:
            self.fail(e.message)

    def test_shortcut_monkey_patch_with_recorded_model_mixin(self):
        article = Article.objects.first()
        try:
            article.records_in_hour
            article.records_in_day
            article.records_in_week
            article.records_in_month
            article.records_in_year
        except Exception as e:
            self.fail(e.message)

    def test_resampling_shortcut_monkey_patch_with_recorded_model_mixin(self):
        article = Article.objects.first()
        try:
            article.resampled_records_in_hour
            article.resampled_records_in_day
            article.resampled_records_in_week
            article.resampled_records_in_month
            article.resampled_records_in_year
        except Exception as e:
            self.fail(e.message)