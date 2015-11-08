from django.test import TestCase

from random import randint, uniform
from faker import Faker

from .models import TITLE_MAX_LENGTH, POINT_MAX_LENGTH, TEXT_MAX_LENGTH
from .models import Article, Comment, Vote


# fake factory
f = Faker()


class RecordQuerysetTest(TestCase):
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

    def test_time_filters_on_record_model(self):
        comment = Comment.objects.first()
        try:
            comment.records.created_in_seconds(2).exists()
            comment.records.created_in_minutes().exists()
            comment.records.created_in_hours().exists()
            comment.records.created_in_days().exists()
            comment.records.created_in_weeks().exists()
            comment.records.created_in_months().exists()
            comment.records.created_in_years().exists()
        except Exception as e:
            self.fail(e.message)

    def test_resampling_filter_on_record_model(self):
        comment = Comment.objects.first()
        try:
            comment.records.created_in_seconds(2).resample('D').exists()
            comment.records.created_in_minutes().resample('D').exists()
            comment.records.created_in_hours().resample('D').exists()
            comment.records.created_in_days().resample('D').exists()
            comment.records.created_in_weeks().resample('D').exists()
            comment.records.created_in_months().resample('D').exists()
            comment.records.created_in_years().resample('D').exists()
        except Exception as e:
            self.fail(e.message)

    def test_time_filters_on_recorded_model_mixin(self):
        article = Article.objects.first()
        try:
            article.records.created_in_seconds(2).exists()
            article.records.created_in_minutes().exists()
            article.records.created_in_hours().exists()
            article.records.created_in_days().exists()
            article.records.created_in_weeks().exists()
            article.records.created_in_months().exists()
            article.records.created_in_years().exists()
        except Exception as e:
            self.fail(e.message)

    def test_resampling_filter_on_recorded_model_mixin(self):
        article = Article.objects.first()
        try:
            article.records.created_in_seconds(2).resample('D').exists()
            article.records.created_in_minutes().resample('D').exists()
            article.records.created_in_hours().resample('D').exists()
            article.records.created_in_days().resample('D').exists()
            article.records.created_in_weeks().resample('D').exists()
            article.records.created_in_months().resample('D').exists()
            article.records.created_in_years().resample('D').exists()
        except Exception as e:
            self.fail(e.message)
