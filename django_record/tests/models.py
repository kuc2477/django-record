from django.db import models

from django_record.models import TimeStampedModel
from django_record.models import RecordModel


class Article(TimeStampedModel):
    TITLE_MAX_LENGTH = 100

    title = models.CharField(max_length=TITLE_MAX_LENGTH)


class Comment(TimeStampedModel):
    POINT_MAX_LENGTH = 100
    TEXT_MAX_LENGTH = 300

    article = models.ForeignKey(Article)

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


class CommentRecord(RecordModel):
    recording_model = Comment
    recording_fields = [
        # Ordinary django fields.
        'point', 'text', 'impact', 'impact_rate',
        # Properties.
        ('string_property', models.CharField(max_length=1000)),
        ('integer_property', models.IntegerField()),
        ('float_property', models.FloatField())
    ]
