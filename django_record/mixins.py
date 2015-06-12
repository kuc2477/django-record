from django.db.models import Model
from django.db.models.signals import class_prepared

from .models import RecordModel


class RecordedModelMixin(object):
    """ Registers record model for the mixed in model automatically """
    recording_fields = []
    auditing_relatives = []

    class RecordMeta:
        audit_all_relatives = False


# =============================================================
# Listen for RecordedModelMixin mixed-in class prepared signals
# =============================================================

# Registers record model for `RecordedModelMixin` mixed-in models on thier
# `class_prepared` signals
def register_record_model(sender, **kwargs):
    # Ensure that we register a record model only if the prepared class is
    # properly mixed-in class of RecordedModelMixin.
    if (issubclass(sender, Model) and
        issubclass(sender, RecordedModelMixin) and
        # Registering record models should done only once
        # in app registering process.
        not sender._meta.apps.ready):

        attrs = {}

        # Needed for django model registration.
        attrs['__module__'] = sender.__module__
        attrs['recording_model'] = sender
        attrs['recording_fields'] = sender.recording_fields
        attrs['auditing_relatives'] = sender.auditing_relatives
        attrs['RecordMeta'] = sender.RecordMeta

        # Register a record model.
        type('{}Record'.format(sender.__name__), (RecordModel,), attrs)

        recording_fields = []
        # Refine `recording_fields` into plain list of names of recording
        # fields, rather than mix of tuples and strings, for users to
        # easily access and make use of this attribute.
        for field_entry in sender.recording_fields:
            if isinstance(field_entry, tuple):
                field_name, _ = field_entry
            else:
                field_name = field_entry
            recording_fields.append(field_name)

        sender.recording_fields = recording_fields

class_prepared.connect(register_record_model, weak=False)
