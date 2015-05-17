=======
Changes
=======

2015-05-17
==========
* Migrated entire recorder implemetation related methods to 
  ``RecordModel`` iteself, rather than putting them on ``__init__``
  method of ``RecordModelMetaClass``.

* ``indirect_effect_recorder`` now works as expected, recording
  effects both for *related* and *reverse related* instances

  * Tests for ``indirect_effect_recorder`` added and all passed.
