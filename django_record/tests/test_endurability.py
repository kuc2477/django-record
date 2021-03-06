from django.test import TestCase

from random import randint, uniform
from faker import Faker

from .models import TITLE_MAX_LENGTH, POINT_MAX_LENGTH, TEXT_MAX_LENGTH
from .models import Article, Comment, Vote, CommentRecord


f = Faker()
ARTICLE_NUM = 50
COMMENT_TRIAL = 4
COMMENT_RATE = 0.4
VOTE_TRIAL = 3
VOTE_RATE = 0.4


def probability(prob):
    return prob > uniform(0, 1)


class EndurabilityTest(TestCase):
    @classmethod
    def setUpClass(self):
        for _ in range(ARTICLE_NUM):
            Article.objects.create(title=f.text()[:TITLE_MAX_LENGTH])

        for article in Article.objects.all():
            for _ in range(COMMENT_TRIAL):
                if probability(COMMENT_RATE):
                    Comment.objects.create(
                        article=article,
                        point=f.text()[:POINT_MAX_LENGTH],
                        text=f.text()[:TEXT_MAX_LENGTH],
                        impact=randint(0, 10),
                        impact_rate=uniform(0, 1)
                    )

        for comment in Comment.objects.all():
            for _ in range(VOTE_TRIAL):
                if probability(VOTE_RATE):
                    Vote.objects.create(
                        comment=comment,
                        score=randint(0, 10)
                    )

    @classmethod
    def tearDownClass(self):
        Article.objects.all().delete()

    def test_no_duplicate_record_on_recorded_model_mixin_1(self):
        for article in Article.objects.all():
            for r in article.records.all():
                try:
                    r_next = r.get_next_by_created(recording=r.recording)
                except Exception:
                    break

                identical = True

                for f in Article.recording_fields:
                    if getattr(r, f) != getattr(r_next, f):
                        identical = False

                if identical:
                    self.fail('duplicate record')

    def test_no_duplicate_record_on_recorded_model_mixin_2(self):
        for vote in Vote.objects.all():
            for r in vote.records.all():
                try:
                    r_next = r.get_next_by_created(recording=r.recording)
                except Exception:
                    break

                identical = True

                for f in vote.recording_fields:
                    if getattr(r, f) != getattr(r_next, f):
                        identical = False

                if identical:
                    self.fail('duplicate record')

    def test_no_duplicate_record_on_record_model(self):
        for comment in Comment.objects.all():
            for r in comment.records.all():
                try:
                    r_next = r.get_next_by_created()
                except Exception:
                    continue

                identical = True

                for f in CommentRecord.recording_fields:
                    if getattr(r, f) != getattr(r_next, f):
                        identical = False

                if identical:
                    self.fail('duplicate record')
