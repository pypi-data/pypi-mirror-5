:mod:`excel`
============

Excel has the following limitations:

- Only loads to unichr(55295) for unicode and (str) bytes type
- Dates and datetimes can only be >= year of 1904
- Dates and datetimes are loaded in as datetime
- Can not save as binary (str) because workbook is set to ASCII. To fix we convert binary to unicode before saving.

.. automodule:: cardsharp.loaders.excel
   :members:
   :undoc-members: