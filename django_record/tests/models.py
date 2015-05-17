from django.db import models
from django.db.models import Sum

from django_record.models import TimeStampedModel
from django_record.models import RecordModel


TITLE_MAX_LENGTH = 100
POINT_MAX_LENGTH = 100
TEXT_MAX_LENGTH = 300


class Article(TimeStampedModel):
    title = models.CharField(max_length=TITLE_MAX_LENGTH)


class Comment(TimeStampedModel):
    article = models.ForeignKey(Article, related_name='comments')
    point = models.CharField(max_length=POINT_MAX_LENGTH)
    text = models.TextField(max_length=TEXT_MAX_LENGTH)
    impact = models.IntegerField()
    impact_rate = models.FloatField()

    @property
    def string_property(self):
        return self.point + self.text

    @property
    def integer_property(self):
        return self.impact + 1

    @property
    def float_property(self):
        return self.impact + self.impact_rate

    @property
    def related_property(self):
        return 0 if not self.votes.exists() else \
            int(self.votes.aggregate(Sum('score'))['score__sum'])

    @property
    def reverse_related_property(self):
        return self.article.title


class Vote(models.Model):
    comment = models.ForeignKey(Comment, related_name='votes')
    score = models.IntegerField()


class CommentRecord(RecordModel):
    recording_model = Comment
    recording_fields = [
        # Ordinary django fields.
        'point', 'text', 'impact', 'impact_rate',
        # Properties.
        ('string_property', models.CharField(max_length=1000)),
        ('integer_property', models.IntegerField()),
        ('float_property', models.FloatField()),
        ('related_property', models.IntegerField()),
        ('reverse_related_property', models.CharField(max_length=1000))
    ]

    class RecordMeta:
        audit_all_relatives = True
