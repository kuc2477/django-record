*************
django-record
*************
    
``django-record`` automatically creates an extra record when an audited 
Django model instance has been changed either directly or indirectly.

``RecordModel`` will detect any changes in ``recording_fields`` of
``recording_model`` at it's post save() time or ``auditing_relatives``'s
post save() time and create an new record for it. 

You can access records via record manager ``records`` in your recorded model
instance. Also, you are able to access audited model instance via ``recording`` in
your records, which is in effect ``ForeignKey``.

More conveniently, just mixin ``RecordedModelMixin`` to your model and provide 
``recording_fields`` and ``auditing_relatives`` as ``RecordModel`` to record 
specific model.


Author
======
* `Jun Soo Ha <kuc2477@gmail.com>`_


Compatibility
=============
* Python3 is currently not supported.
  

Dependencies
============
* ``django-record`` supports `django <https://github.com/django/django>`_ (>= 1.7) or later.
* Requires `faker <https://github.com/joke2k/faker>`_ for tests.


Installation
============
``pip install django-record``


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
    
            auditing_relatives = ['author']
    
        
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
        
        
        class Comment(RecordedModelMixin, TimeStampedModel):
            article = models.ForeignKey(Article, related_name='comments')
            text = models.TextField()
    
            @property
            def title_of_article_with_prefix(self):
                return 'title: ' + self.article.title
    
        
        class Vote(models.Model):
            article = models.ForeignKey(Article, related_name='votes')
            score = models.IntegerField()
        
    
        # Record Models
    
        class ArticleRecord(RecordModel):
            recording_model = Article
            recording_fields = [
                'title',
                ('full_name_of_author', models.CharField(max_length=50)),
                ('total_comment_count', models.IntegerField()),
                ('total_score', models.IntegerField())
            ]
        
            auditing_relatives = ['user', 'comments', 'votes']
    
            # Uncomment this meta class if you want to audit
            # all relative instances to monitor their indirect
            # effects on our ``recording_model``.
            """
            class RecordMeta:
                audit_all_relatives = True
            """
            # Note that setting this attribute as True can cause
            # performance issue in large scale database.
    
    
        class CommentRecord(RecordModel):
            recording_model = Comment
            recording_fields = [
                'text', 
                ('title_of_article_with_prefix', models.CharField(max_length=200))
            ]
    
            class RecordMeta:
                audit_all_relatives = True
    


Usage
=====
.. code-block:: python
    
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


Note
====
* **Only primitive types are supported for properties** and **you must
  offer appropriate field** for them when you put a tuple of a property
  name and it's field in 'recording_fields' for expected recording.

* ``RecordModel`` is also a subclass of ``TimeStampedModel``, so **make sure that
  you don't record either 'created' or 'modified' fields.**
