:mod:`convert` --- Cardsharp conversion module
==============================================

.. module:: convert
  :synopsis: Convert to and from different objects.

This module defines functions for performing cardsharp specific conversions on different Python objects. 

Cardsharp Conversion Functions
------------------------------

+-------------------+------------------------+-----------------+
| Name              | Input Type(s)          |  Return Type    |
+-------------------+------------------------+-----------------+
| as_str_           | all                    | str (unicode)   |
+-------------------+------------------------+-----------------+
| binary_to_binary_ | binary                 | str (bytes)     |
+-------------------+------------------------+-----------------+
| binary_to_str_    | binary                 | str (unicode)   |
+-------------------+------------------------+-----------------+
| datetime_to_date_ | datetime               | date            |
+-------------------+------------------------+-----------------+
| datetime_to_time_ | datetime               | time            |
+-------------------+------------------------+-----------------+
| str_to_binary_    | str                    | str (bytes)     |
+-------------------+------------------------+-----------------+
| str_to_datetime_  | str                    | datetime        |
+-------------------+------------------------+-----------------+
| str_to_date_      | str                    | date            |
+-------------------+------------------------+-----------------+
| str_to_time_      | str                    | time            |
+-------------------+------------------------+-----------------+
| str_to_float_     | str                    | float           |
+-------------------+------------------------+-----------------+
| round_            | str, float, decimal    | decimal         |
+-------------------+------------------------+-----------------+

Please see the codecs_ Python documentation for complete list of binary encodings.

   .. _codecs: http://docs.python.org/library/codecs.html#standard-encodings

cardsharp.convert Classes
-------------------------
.. class:: ContextDict(dict)

   Creates a dictionary which defines the :const:`DECIMAL_CONTEXTS` to use when calling round_
    
   >>> D = ContextDict()
   >>> context, model = D[(2, decimal.ROUND_UP)]
   >>> context.rounding
   'ROUND_UP'
   >>> model
   Decimal('0.01')
   
   >>> context, model = D[(4, decimal.ROUND_DOWN)]
   >>> context.rounding
   'ROUND_DOWN'
   >>> model
   Decimal('0.0001')

cardsharp.convert Methods
-------------------------

.. _as_str:
.. method:: as_str(v)
   
   Converts *v* to a unicode string. If *v* is ``None``, returns ``None`` instead. 
    
   >>> as_str(datetime(2007, 12, 5))
   u'2007-12-05 00:00:00'
   >>> as_str(None) is None
   True
   
.. _binary_to_binary:
.. function:: binary_to_binary(s, orig_encoding, new_encoding)

   Converts from original binary bytes string with *orig_encoding* to a new binary bytes string 
   using *new_encoding*. If *s* is ``None`` returns ``None`` instead.
    
   >>> binary_to_binary('out_str', 'latin_1', 'utf_16')
   '\\xff\\xfeo\\x00u\\x00t\\x00_\\x00s\\x00t\\x00r\\x00'
   >>> binary_to_binary(None, 'utf_8', 'utf_8') is None
   True

.. _binary_to_str:
.. function:: binary_to_str(s, encoding)

   Decodes from a binary bytes string using *encoding* and returns a unicode string.
   If *s* is ``None`` returns ``None`` instead.
    
   >>> binary_to_str('out_str', 'latin_1')
   u'out_str'
   >>> binary_to_str('\xff\xfeo\x00u\x00t\x00_\x00s\x00t\x00r\x00', 'utf_16') #doctest: +SKIP
   u'out_str'
   >>> binary_to_str(None, 'utf_8') is None
   True

.. _datetime_to_date:
.. function:: datetime_to_date(d [,format_str])

   Converts a datetime to a date. If *d* is ``None`` returns ``None`` instead. *format_str* 
   (not implemented) is ``None`` by default.
   
   >>> from datetime import datetime
   >>> d = datetime(2007, 12, 15, 12, 10, 10) 
   >>> datetime_to_date(d)
   datetime.date(2007, 12, 15)
   >>> datetime_to_date(None) is None
   True

.. _datetime_to_time:   
.. function:: datetime_to_time(d [,format_str])

   Converts a datetime to a time. If *d* is ``None`` returns ``None`` instead. *format_str* 
   (not implemented) is ``None`` by default.
   
   >>> from datetime import datetime
   >>> d = datetime(2007, 12, 5, 12, 10, 10) 
   >>> datetime_to_time(d)
   datetime.time(12, 10, 10)
   >>> datetime_to_date(None) is None
   True

.. function:: get_format_converter(source, dest)

   This function locates a conversion function to convert format *source* into format *dest*.
    
   >>> c = get_format_converter('string', 'integer')
   >>> c('12')
   12
   >>> c = get_format_converter('string', 'date')
   >>> c('1/1/2000', '%m/%d/%Y')
   datetime.date(2000, 1, 1)
   
   If no conversion is required (e.g., converting from a *float* to a *float*) this function returns ``None``.  It will throw an
   exception if no conversion is possible. 
    
   >>> get_format_converter('time', 'time') is None
   True
   >>> get_format_converter('time', 'datetime')
   Traceback (most recent call last):
       ...
   FormatError: Cannot automatically convert from time to datetime

.. _round:
.. function:: round(v, decimals [,rounding])

   Round to the nearest decimals places. If *v* is ``None`` returns ``None`` instead.
    
   *v* can be a float, str, or Decimal.
   
   *decimals* is an int. 
    
   >>> from decimal import *
   >>> round(1.235, 1)
   Decimal('1.2')
   >>> round('1.235', 2)
   Decimal('1.24')
   >>> round(None,None) is None
   True
    
   If *decimals* > decimal place of *v* then round and add zeros for any missing decimal places.
   
   >>> round(Decimal('1.2'), 5)
   Decimal('1.20000')
   >>> round('1.229', 5)
   Decimal('1.22900')
    
   By default the rounding convention is set to :const:`ROUND_HALF_EVEN`. 
   If you supply a *rounding* argument then *v* is rounded using supplied convention. 
    
   >>> round(Decimal('1.239'), 2, 'ROUND_DOWN')
   Decimal('1.23')
    
   The *rounding* option is one of the following constants defined in decimal_
   
   .. _decimal: http://docs.python.org/library/decimal.html

   * :const:`ROUND_CEILING` (towards :const:`Infinity`),
   * :const:`ROUND_DOWN` (towards zero),
   * :const:`ROUND_FLOOR` (towards :const:`-Infinity`),
   * :const:`ROUND_HALF_DOWN` (to nearest with ties going towards zero),
   * :const:`ROUND_HALF_EVEN` (to nearest with ties going to nearest even integer),
   * :const:`ROUND_HALF_UP` (to nearest with ties going away from zero), or
   * :const:`ROUND_UP` (away from zero).
   * :const:`ROUND_05UP` (away from zero if last digit after rounding towards zero would have been 0 or 5; otherwise towards zero)

.. _round_int:
.. function:: round_int(v [,rounding])

   Round to the nearest integer. *v* can be a float, str, or Decimal. 
   If *v* is None returns ``None`` instead.
    
   >>> round_int(1.235)
   1
   >>> round_int('1.5')
   2
   >>> round_int(None) is None
   True
    
   By default *rounding* is set to :const:`ROUND_HALF_EVEN`. Pass a rounding argument to have *v* 
   rounded using the passed rounding convention. See round_ for list of rounding arguments.
   
.. _str_to_binary:
.. function:: str_to_binary(s, encoding)
   
   Encodes a unicode string using given *encoding* to return a binary bytes string. 
   
   If *s* is ``None`` returns ``None`` instead. 
      
   >>> str_to_binary('out_str', 'utf_8')
   'out_str'
   >>> str_to_binary('out_str', 'utf_16')
   '\\xff\\xfeo\\x00u\\x00t\\x00_\\x00s\\x00t\\x00r\\x00'
   >>> str_to_binary(None, 'utf_8') is None
   True

.. _str_to_date:
.. function:: str_to_date(d [,format_str])

   Converts a unicode string to a date explicitly following the corresponding *format_str*. 
   If *d* is ``None`` returns ``None`` instead. *format_str* is ``None`` by default.
   
   >>> d = '05-10-1900'  
   >>> str_to_date(d, '%m-%d-%Y')  
   datetime.date(1900, 5, 10)
   >>> d = '10051900'  
   >>> str_to_date(d, '%m%d%Y')
   datetime.date(1900, 10, 5)
   >>> str_to_date(None) is None
   True

.. _str_to_datetime:
.. function:: str_to_datetime(d, format_str)

   Converts a str to a datetime object following the corresponding *format_str*. 
   If *d* is ``None`` returns ``None`` instead.
    
   >>> d = '05-10-1900 12:00:01' 
   >>> str_to_datetime(d, '%m-%d-%Y %H:%M:%S')
   datetime.datetime(1900, 5, 10, 12, 0, 1)
   >>> d = '10051900 120001'
   >>> str_to_datetime(d, '%m%d%Y %H%M%S')
   datetime.datetime(1900, 10, 5, 12, 0, 1)
   >>> str_to_datetime(None, None) is None
   True

.. _str_to_float:
.. function:: str_to_float(s [,format_str])

   Converts a string to a float. 
   If *s* is ``None`` returns ``None`` instead. *format_str* (not implemented) is ``None`` by default.
    
   >>> str_to_float('1')
   1.0
   >>> str_to_float('1.1')
   1.1000000000000001

.. _str_to_time:
.. function:: str_to_time(d, format_str)

   Converts a str to a time object following the corresponding format_str. 
   If *d* is ``None`` returns ``None`` instead.
    
   >>> d = '12:00:01' 
   >>> str_to_time(d, '%H:%M:%S')
   datetime.time(12, 0, 1)
   >>> d = '120001'
   >>> str_to_time(d, '%H%M%S')
   datetime.time(12, 0, 1)
   >>> str_to_time(None, None) is None
   True