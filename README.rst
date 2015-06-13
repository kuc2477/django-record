*************
django-record
*************
.. image:: https://img.shields.io/pypi/l/django-record.svg
   :target: https://img.shields.io/pypi/django-record
.. image:: https://secure.travis-ci.org/kuc2477/django-record.png?branch=master
   :target: http://travis-ci.org/kuc2477/django-record
.. image:: https://coveralls.io/repos/kuc2477/django-record/badge.svg?branch=master
   :target: https://coveralls.io/r/kuc2477/django-record?branch=master
.. image:: https://img.shields.io/pypi/v/django-record.svg
   :target: https://img.shields.io/pypi/django-record
.. image:: https://img.shields.io/pypi/dm/django-record.svg
   :target: https://img.shields.io/pypi/django-record
   :alt: Latest Version


Author
======
* `Ha Junsoo <kuc2477@gmail.com>`_


Compatibility
=============
* Python3 is currently not supported.
  

Dependencies
============
* *django-record* supports `django <https://github.com/django/django>`_ (>= 1.7) or later.
* Requires `unipath <https://github.com/mikeorr/Unipath>`_ and `faker <https://github.com/joke2k/faker>`_ for tests.


Installation
============
``pip install django-record``


Rationale
=========
Often there are situations where you want to record your properties of your models and
where you want to track their changes. Although that recording process can be implemented
by `handcrafted, ad-hoc signals`_ or `overriding save() methods of your models`_, it's
not a generic way, and **it'll eventually mess up your code base**.

*django-record* **automatically creates an snapshot-like extra record** when an audited 
Django model instance has been changed **either directly or indirectly**,
without messing up your code base.

``RecordModel`` will detect any changes in ``recording_fields`` of
``recording_model`` at it's ``post_save`` time or ``auditing_relatives``'s
``post_save`` time and create an new record for it. 

You can access records via record manager ``records`` in your recorded model
instance. You can also access recorded model's instance via ``recording``, 
which is in effect ``ForeignKey``. from your records.

More conveniently, just mixin ``RecordedModelMixin`` to your model and provide 
``recording_fields`` and ``auditing_relatives`` as ``RecordModel`` to record 
specific model.

.. _`handcrafted, ad-hoc signals`: https://djangosnippets.org/snippets/500/
.. _`overriding save() methods of your models`: https://trickveda.wordpress.com/2014/01/22/overriding-save-method-in-django-models/


Mixins
======
``django-record`` provides mixins which auto-registers ``RecordModel`` for your mixed in
model to help your model instance recording.

* *RecordedModelMixin*
    **Attributes**
        - ``recording_fields`` (*list*): A List consists of either to-be-recoreded field
          names or tuples of a property name and it's field instance to
          be saved in database.
    
        - ``auditing_relatives`` (*list*): A List of audited relatives. An extra record
          will be created on every ``save()`` calls of these relative instances that indirectly
          affects the recording instance, along with recording on direct ``save()`` calls from
          ``recording_model`` instances.
    
        - ``RecordMeta`` (*class*): A class storing meta information for recording. Set
          ``audit_all_relatives`` to audit all relatives of your recorded model's instance.
          Note that auditing all relatives can cause a performance issue in large scale
          database.
    
    **Example**
    
    .. code-block:: python
    
        from django.db import models
        from django.db.models import Sum
        
        from django_record.models import TimeStampedModel
        from django_record.mixins import RecordedModelMixin
        
        
        class Article(RecordedModelMixin, TimeStampedModel):
            author = models.ForeignKey(User, related_name='articles')
            title = models.CharField(max_length=100)
            
            @property
            def total_comment_count(self):
                return self.comments.count()
            
            @property
            def total_score(self):
                return 0 if not self.votes.exists() else \
                int(self.votes.aggregate(Sum('score'))['score__sum'])
                
            @property
            def full_name_of_author(self):
                return self.author.username
    
            recording_fields = [
                'title',
                ('total_comment_count', models.IntegerField()),
                ('total_score', models.IntegerField()),
                ('full_name_of_author', models.CharField(max_length=100))
            ]
            
            class RecordMeta:
               audit_all_relatives = True
    
        
        class Comment(RecordedModelMixin, TimeStampedModel):
            article = models.ForeignKey(Article, related_name='comments')
            text = models.TextField()
    
            @property
            def title_of_article_with_prefix(self):
                return 'title: ' + self.article.title
    
            recording_fields = [
                'text', 
                ('title_of_article_with_prefix', models.CharField(max_length=200))
            ]
    
            class RecordMeta:
                audit_all_relatives = True
    
        
        class Vote(models.Model):
            article = models.ForeignKey(Article, related_name='votes')
            score = models.IntegerField()


Models
======
``django-record`` provides models for recording model instances, including RecordModel and
TimeStampedModel.

* *RecordModel*
    **Attributes**
        - ``recording_model`` (*class*): A model class to be recorded. An extra record
          will be created on every changed ``save()`` calls of it's instance or
          audited relative's ``save()`` calls.
    
        - ``recording_fields`` (*list*): A List consists of either to-be-recoreded field
          names or tuples of a property name and it's field instance to
          be saved in database.
    
        - ``auditing_relatives`` (*list*): A List of audited relatives. An extra record
          will be created on every ``save()`` calls of these relative instances that indirectly
          affects the recording instance, along with recording on direct ``save()`` calls from
          ``recording_model`` instances.
    
        - ``RecordMeta`` (*class*): A class storing meta information for recording. Set
          ``audit_all_relatives`` to audit all relatives of your recorded model's instance.
          Note that auditing all relatives can cause a performance issue in large scale
          database.
    
    **Example**
    
    .. code-block:: python
    
        from django.db import models
        from django.db.models import Sum
        
        from django_record.models import TimeStampedModel
        from django_record.models import RecordModel
    
    
        # Models
        
        class Article(TimeStampedModel):
            author = models.ForeignKey(User, related_name='articles')
            title = models.CharField(max_length=100)
            
            @property
            def total_comment_count(self):
                return self.comments.count()
            
            @property
            def total_score(self):
                return 0 if not self.votes.exists() else \
                int(self.votes.aggregate(Sum('score'))['score__sum'])
                
            @property
            def full_name_of_author(self):
                return self.author.username
        
        
        class Comment(TimeStampedModel):
            article = models.ForeignKey(Article, related_name='comments')
            text = models.TextField()
    
            @property
            def title_of_article_with_prefix(self):
                return 'title: ' + self.article.title
    
        
        class Vote(models.Model):
            article = models.ForeignKey(Article, related_name='votes')
            score = models.IntegerField()
        
    
        # Record Model
    
        class ArticleRecord(RecordModel):
            recording_model = Article
            recording_fields = [
                'title',
                ('full_name_of_author', models.CharField(max_length=50)),
                ('total_comment_count', models.IntegerField()),
                ('total_score', models.IntegerField())
            ]
            
            class RecordMeta:
               auditing_all_relatives = True
    
    
        class CommentRecord(RecordModel):
            recording_model = Comment
            recording_fields = [
                'text', 
                ('title_of_article_with_prefix', models.CharField(max_length=200))
            ]
    
            class RecordMeta:
                audit_all_relatives = True
    


Note
====
* **Recursive auditing is not currently supported.** Indirect effect only those 
  from direct relatives will be detected and recorded.
* **Only primitive types are supported for properties.** You must offer appropriate django field for them.
* ``RecordModel`` is also a subclass of ``TimeStampedModel``, so make sure that
  you don't record either 'created' or 'modified' fields.


Usage
=====
.. code-block:: python

        from django.db import models
        from django.db.models import Sum
        
        from django_record.models import TimeStampedModel
        from django_record.models import RecordModel
    
    
        # Models
        
        class Article(RecordedModelMixin, TimeStampedModel):
            author = models.ForeignKey(User, related_name='articles')
            title = models.CharField(max_length=100)
            
            @property
            def total_comment_count(self):
                return self.comments.count()
            
            @property
            def total_score(self):
                return 0 if not self.votes.exists() else \
                int(self.votes.aggregate(Sum('score'))['score__sum'])
                
            @property
            def full_name_of_author(self):
                return self.author.username
                
            recording_fields = [
                'title',
                ('full_name_of_author', models.CharField(max_length=50)),
                ('total_comment_count', models.IntegerField()),
                ('total_score', models.IntegerField()),
            ]
            auditing_relatives = [
               'user', 'comments', 'votes'
            ]
        
        
        class Comment(RecordedModelMixin, TimeStampedModel):
            article = models.ForeignKey(Article, related_name='comments')
            text = models.TextField()
    
            @property
            def title_of_article_with_prefix(self):
                return 'title: ' + self.article.title
                
            recording_fields = [
               'article',
               ('title_of_article_with_prefix', models.CharField(100)),
            ]
            auditing_relatives = [
               'article',
            ]
    
        
        class Vote(models.Model):
            article = models.ForeignKey(Article, related_name='votes')
            score = models.IntegerField()

    
    >>> a =  Article.objects.first()
    >>> v = a.votes.first()
    >>>
    >>> v.score = 999
    >>> v.save()                                # recorder creates a new article record, updating 'total_score'.
    >>>
    >>> r =  a.records.latest()
    >>> a.total_score == r.total_score
    >>> True
    
    ...
    
    >>> count_before = a.total_comment_count
    >>>
    >>> Comment.objects.create(article=a, text='text of comment')   # recorder creates first record for created comment and
    >>>                                                             # a new record for existing article, updating 'total_comment_count'.
    >>> r = a.records.latest()
    >>> r.total_comment_count == count_before + 1
    >>> True
    
    ...
    
    >>> records_before_yesterday = d.records.filter(created__lte=yesterday)     # you can filter records by created time.
    >>> records_of_today = d.records.filter(created__gte=today)
    
    ...
