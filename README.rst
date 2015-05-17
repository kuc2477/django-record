*************
django-record
*************
    
``django-record`` automatically creates an extra record when an audited 
Django model instance has been changed either directly or indirectly.

``RecordModel`` will detect any changes of ``recording_fields`` in
``recording_model`` at it's post save() time or ``auditing_relatives``'s
post save() time and create an new record for it. 

You can access records via record manager ``records`` in your recorded model
instance. Also, you are able to access audited model instance via ``recording`` in
your records, which is in effect ``ForeignKey``.

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

Attributes
==========
    * ``recording_model`` (*class*): A model class to be recorded. An extra record
      will be created on every changed ``save()`` calls of it's instance or
      auditing relative's ``save()`` calls.

    * ``recording_fields`` (*list*): A List consists of either to-be-recoreded field
      names or tuples of a property name and it's field instance to
      be saved in database.

    * ``auditing_relatives`` (*list*): A List of audited relatives. An extra record
      will be created on every ``save()`` calls of these relative instances that indirectly
      affects the recording instance, along with recording on direct ``save()`` calls from
      ``recording_model`` instances.

Example
=======
.. code-block:: python

    from django.db import models
    from django.contrib.auth.models import User
    from django_record.models import TimeStampedModel
    from django_record.models import RecordModel
    
    
    class Debate(models.Model):
        user = models.ForeignKey(User)
    
        title = models.CharField(max_length=100)
        num_of_pros = models.IntegerField()
        num_of_cons = models.IntegerField()
    
        @property
        def pros_rate(self):
            return self.num_of_pros // (self.num_of_pros + self.num_of_cons)
    
        @property
        def cons_rate(self):
            return self.num_of_cons // (self.num_of_pros + self.num_of_cons)
    
        @property
        def user_name(self):
            return user.username
    
    
    class DebateRecord(RecordModel):
        recording_model = Debate
        recording_fields = [
            'title', 'num_of_pros', 'num_of_cons'
            ('pros_rate', models.FloatField()),
            ('cons_rate', models.FloatField()),
            ('user_name', models.CharField(max_length=100))
        ]
    
        auditing_relatives = ['user', ]

        # Uncomment this meta class if you want to audit
        # all relative instances to monitor their indirect
        # effects on our ``recording_model``.
        """
        class RecordMeta:
            audit_all_relatives = True
        """
        # Note that settings this attribute as True can cause
        # performance issue in large scale database.
    
    
    >>> d =  Debate.objects.first()
    >>> r =  d.records.latest()
    >>> assert(d.title == r.title)
    >>> assert(d.pros_rate == r.pros_rate)
    
    ...
    
    >>> records_before_yesterday = d.records.filter(created__lte=yesterday)
    >>> records_of_today = d.records.filter(created__gte=today)
    
    ...
    
    >>> u = d.user
    >>> u.username = 'changed user name'
    >>> u.save()
    >>> r = d.records.latest()
    >>> assert(d.user_name == r.user_name)
    >>> assert(d.user.username == r.user_name)

Note
====
* **Only primitive types are supported for properties** and **you must
  offer appropriate field** for them when you put a tuple of a property
  name and it's field in 'recording_fields' for expected recording.

* ``RecordModel`` is also a subclass of ``TimeStampedModel``, so **make sure that
  you don't record either 'created' or 'modified' fields.**
