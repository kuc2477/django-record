# TODO: Implement `RecordedModelMixin` for more DRY approach.
#
# Example:
#
#     class Article(RecordedModelMixin, models.Model):
#         title = CharField(...)
#
#         recording_fields = [...]
#         auditing_relatives = [...]
#
#         class RecordMeta:
#            audit_all_relatives = True
