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


Requirements
============
* Tested against Python 2.7 and 3.4
* *django-record* supports `django <https://github.com/django/django>`_ 1.7 or later.
* Requires `pandas <https://github.com/pydaya/pandas>`__ 0.17.0 or later.
* Requires `faker <https://github.com/joke2k/faker>`_ for tests.


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
which is in effect just ordinary ``ForeignKey``, from your records.

More conveniently, **just mix** ``RecordedModelMixin`` into your model and provide 
``recording_fields`` and ``auditing_relatives``.

.. _`handcrafted, ad-hoc signals`: https://djangosnippets.org/snippets/500/
.. _`overriding save() methods of your models`: https://trickveda.wordpress.com/2014/01/22/overriding-save-method-in-django-models/


Usage
=====
.. code-block:: python

   from django.db import models
   from django_record.mixins import RecordedModelMixin


   class MyTopic(models.Model):
       title = models.CharField(max_length=100)


   class MyArticle(RecordedModelMixin, models.Model):
       topic = models.ForeignKey(MyTopic)
       text = models.TextField()

       @property
       def my_local_property(self):
           return self.text
      
       @property
       def my_nonlocal_property(self):
           return self.topic.title + self.text
       
       # We will monitor `topic` relative to watch if he changes!
       auditing_relatives = ['topic']

       recording_fields = [
           # Record changes of the model instance's `text` field
           'text', 
           # Yayy! we can record changes on properties too!
           ('my_local_property', models.TextField()),
           # Even indirect effects from relatives are recordable!
           ('my_nonlocal_property', models.TextField())
       ] 


    # To get the model instance's all records
    >>> my_article.records.all()

    # To get queryset of the model instance's records created in specific 
    # time threshold
    >>> my_article.records.created_in_years(2)
    >>> my_article.records.created_in_days(3)
    >>> my_article.records.created_in_minutes(5)

    # To resample records of today by hour
    >>> my_article.records.created_in_days().resample('T')

    # To get record contents
    >>> my_article.records.first().text
    >>> my_article.records.first().my_local_property
    >>> my_article.records.first().my_nonlocal_property


Note
====
* **Recursive auditing is currently not supported.** Indirect effect only those 
  from direct relatives will be detected and recorded.
* **Only primitive types are supported for properties.** You must offer appropriate django field for them.
* ``RecordModel`` is also a subclass of ``TimeStampedModel``, so make sure that
  you don't record either 'created' or 'modified' fields.
