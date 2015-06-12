from random import randint, uniform

from django.test import TestCase
from faker import Faker

from .models import TITLE_MAX_LENGTH, POINT_MAX_LENGTH, TEXT_MAX_LENGTH
from .models import Article, Comment
from ..utils import resample_records

f = Faker()


class UtilsTest(TestCase):
    def setUp(self):
        article = Article.objects.create(title=f.lorem()[:TITLE_MAX_LENGTH])
        Comment.objects.create(
            article=article, point=f.lorem()[:POINT_MAX_LENGTH],
            text=f.lorem()[:TEXT_MAX_LENGTH],
            impact=randint(0, 10),
            impact_rate=uniform(0, 1)
        )

    def tearDown(self):
        Article.objects.all().delete()

    def test_resample_records(self):
        article = Article.objects.first()

        article.title = 'a'
        article.save()

        article.title = 'b'
        article.save()

        record_count_before_resampling = article.records.count()
        resampled_records = resample_records(article.records.all(), 'H')
        record_count_after_resampling = resampled_records.count()

        self.assertTrue(record_count_before_resampling >
                        record_count_after_resampling)
        self.assertEqual(record_count_after_resampling, 1)
