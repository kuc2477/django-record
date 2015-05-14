from django.test import TestCase

from .models import Article, Comment, CommentRecord


class ModelTest(TestCase):
    def setUp(self):
        Article.objects.create(title='')
