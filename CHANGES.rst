=======
Changes
=======

06.13.2015
==========
* Following shortcut properties added to *recording_model*. All of properties
  below are ordinary django querysets.

  * ``records_in_hour``: Records created in last recent hour.
  * ``records_in_day``: Records created today.
  * ``records_in_week``: Records created in this week.
  * ``records_in_month``: Records created in this month.
  * ``records_in_year``: Records created in this year.

* Following shortcut properties providing resampled records has been added to
  *recording_model*.  All of properties below are ordinary django querysets.

  * ``resampled_records_in_hour``: Records created in last recent hour, 
    resampled with minutes.
  * ``resampled_records_in_day``: Records created today, resampled with hours.
  * ``resampled_records_in_week``: Records created in this week, resamped with
    days.
  * ``resampled_records_in_month``: Records created in this month, resampled 
    with days.
  * ``resamped_records_in_year``: Records created in this year, resampled with
    months.

05.18.2015
==========
* ``RecordedModelMixin`` added.
