# django-record
<small>**Author**: Jun Soo Ha (<kuc2477@gmail.com>)</small>

**Compatibility**: __Python3 is currently not supported.__
  
**Dependencies**:
* Requires [django](https://github.com/django/django) 1.7+
* Requires [faker](https://github.com/joke2k/faker) for tests.  

*Automatically create records when an audited Django model instance has been changed.*

`RecordModel` will detect any changes of `recording_fields` in
`recording_model` at it's *post_save* time and create an record for it.  

You can access records via record manager `records` in your recorded model
instance. Also, you are able to access audited model instance via `recording` in
your records, which is in effect *ForeignKey*.

---

**Attributes**:
* `recording_model` (*class*): A model class to be audited and recorded.  
      Record will be created on every changed save() calls of it's  
      instance.  
* `recording_fields` (*list*): A List of to-be-recoreded field names or  
      tuples of property name and it's appropriate field.  

**Example**:
~~~ python
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


    class DebateRecord(RecordModel):
        recording_model = Debate
        recording_fields = [
            'title', 'num_of_pros', 'num_of_cons'
            ('pros_rate', models.FloatField()),
            ('cons_rate', models.FloatField())
        ]

    .
    .
    >>> d =  Debate.objects.first()
    >>> r =  d.records.latest()
    >>> assert(d.title == r.title)
    >>> assert(d.pros_rate == r.pros_rate)
    .
    .
    >>> records_before_yesterday = d.records.filter(created__lte=yesterday)
    >>> records_of_today = d.records.filter(created__gte=today)
~~~  

**Note**
:
* __Relational fields(e.g. *ForeignKey*, *ManyToManyField*, ...) are not__ 
    __currently supported.__  
* __Only *primitive types* are supported for properties__ and you must offer
    appropriate field for them when you put a tuple of a property
    name and it's field in `recording_fields` for expected recording.  
* `RecordModel` is also a subclass of `TimeStampedModel`, __so make sure that__
    __you don't record fields with either name of *created* or *modified*.__
