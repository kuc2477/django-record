from django_record import TimeStampedModel
from django_record import RecordModel


class Article(TimeStampedModel):
    pass


class Comment(TimeStampedModel):
    pass


class CommentRecord(RecordModel):
    recording_model = Comment
    pass
