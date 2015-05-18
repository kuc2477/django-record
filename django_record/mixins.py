from django.db.models import Model
from django.db.models.signals import class_prepared

from .models import RecordModel


class RecordedModelMixin(object):
    recording_fields = NotImplemented
    auditing_relatives = []

    class RecordMeta:
        audit_all_relatives = False


def register_record_model(sender, **kwargs):
    # Ensure that we register a record model only if the prepared class is
    # properly mixed-in class of RecordedModelMixin.
    if (issubclass(sender, Model) and
        issubclass(sender, RecordedModelMixin) and \
        # If the prepared model already has records, we don't
        # register new record model for the model.
        not hasattr(sender, 'records')):

        attrs = {}
        # Needed for django internal api compaitibility.
        attrs['__module__'] = sender.__module__
        attrs['recording_model'] = sender
        attrs['recording_fields'] = sender.recording_fields
        attrs['auditing_relatives'] = sender.auditing_relatives
        attrs['RecordMeta'] = sender.RecordMeta

        # Register a record model.
        type('{}Record'.format(sender.__name__), (RecordModel,), attrs)

class_prepared.connect(register_record_model, weak=False)
