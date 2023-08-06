Tutorial
========

**Tutorial under active development**

Setting up Cardsharp
--------------------

Dependencies
~~~~~~~~~~~~
- `Python 2.6 or above`_
- 7zip_
- pyyaml
- pyodbc
- xlrd, xlwt, xlutils (required for working with Excel files, see Excel_ configuration section below)
- SAS 9.1 (required for working with SAS files, see SAS_ configuration section below)

	.. _Python 2.6 or above: http://www.python.org/download/
	.. _7zip: http://www.7-zip.org/

First Steps
~~~~~~~~~~~
a. Install

  - `Python 2.6 or above`_
  - 7zip_

  .. _Python 2.6 or above: http://www.python.org/download/
  .. _7zip: http://www.7-zip.org/
  
b. setuptools installations

 - Download and install setuptools_ to install pyyaml, pyodbc, xlrd, xlwt, and xlutils (for windows 64 bit processors follow the 
   instructions at http://selfsolved.com/problems/setuptools-06c11-fails-to-instal to get setuptools working).

 .. _setuptools: http://pypi.python.org/pypi/setuptools
 
Example of setuptools usage:

**Linux:**
::
	$ sudo easy_install xlrd

**Windows:**

First make sure that the Python Scripts directory is in your path, if it is not then you can temporarily add it,
::
	C:\> path=%path%;c:\python2.7\Scripts
  
Then,
::
	C:\> easy_install xlrd

c. Make sure to have your Python development environment setup. A common method is to use the 
	 Eclipse_ IDE with the pydev_ eclipse plugin. First install Eclipse_ and after the install 
	 is complete go to help -> software updates -> Available Software -> Add Site with the following 
	 location url http://pydev.org/updates
	 
   .. _Eclipse: http://www.eclipse.org/downloads/
   .. _pydev: http://pydev.org/download.html
   
   
d. Setup Python Interpreter 
  
Cardsharp Installation
~~~~~~~~~~~~~~~~~~~~~~
Two options available for the install:

1) Install from Source
''''''''''''''''''''''
Download the `Cardsharp source code`_ and

**Linux:**
::
	$ tar xzf cardsharp-tip
	$ cd cardsharp-tip
	$ python setup.py install

.. _Cardsharp source code: http://bitbucket.org/catsclaw/cardsharp/downloads

**Windows:**

use winzip or similar application to unpack cardsharp-tip.zip, then:
::
	C:\> cd cardsharp-tip
	C:\cardsharp-tip> \Python26\python setup.py install

2) Clone the Repository
'''''''''''''''''''''''
If you have Mercurial_ installed you can create a clone of the latest version of the repository.

>>> hg clone http://cardsharp.norc.org/cardsharp

.. _Mercurial: http://mercurial.selenic.com/

Create a Pydev project in Eclipse
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
1) File -> New -> Pydev Project
   a. Choose a name
   b. For project contents unselect 'default' and browse to the location where you installed cardsharp

Configuring Cardsharp
~~~~~~~~~~~~~~~~~~~~~

Cardsharp Config File
'''''''''''''''''''''
Once you have the source code installed open chsarp.config and set the path to the 7zip_exe config option
to the path of the 7zip executable (7z.exe). 
::
	[csharp]
	7zip_exe = c:\7-Zip\7z.exe

.. _Excel:

Excel Configuration
'''''''''''''''''''
For the Excel handler to work the following packages need to be installed:

* `xlrd <http://pypi.python.org/pypi/xlrd>`_
* `xlwt <http://pypi.python.org/pypi/xlwt>`_
* `xlutils <http://pypi.python.org/pypi/xlutils>`_

Please see the Tutorial on python-excel_ for installation details.
	.. _python-excel: http://www.python-excel.org/

.. _SAS:

SAS Configuration
'''''''''''''''''
For SAS to work correctly you need to have `SAS 9.1`_ or above installed and running in a Microsoft Windows environment.
Additionally, you must take the following steps:

1. Install the `SAS ODBC driver`_
2. Follow the steps outlined at `SAS ODBC driver configuration`_

	.. _SAS 9.1: http://www.sas.com/
	.. _SAS ODBC driver: http://www.sas.com/apps/demosdownloads/92_SDL_sysdep.jsp?packageID=000606&jmpflag=N
	.. _SAS ODBC driver configuration: http://support.sas.com/techsup/technote/ts626.html
	
Dataset Manipulation
--------------------
Loading_ and Saving_ datasets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. _Filename_ex:

Once you have completed the above installation steps all that is required to load a dataset is to call 
cardsharp.load and pass it a filename parameter.  

>>> import cardsharp as cs
>>> dataset = cs.load(filename = 'txt_load_demo.txt')

Cardsharp looks at the file extension and chooses what it thinks is the most appropriate loader to use. 
If it can not find a loader to use based on the extension it will throw a LoadError_

>>> invalid_dataset = cs.load(filename = 'test.tz')
Traceback (most recent call last):
	...
cardsharp.errors.LoadError: Cannot determine the format of the data: Unidentified file extension: test.tz  

.. _LoadError: ../modules/errors.html

In the above example the object ``dataset`` now holds a csharp dataset.

>>> print dataset
<cardsharp.data.Dataset object at 0x010F8D70>

This ``dataset`` contains a variable for each column.

>>> print dataset[0:]
[Variable('a', u'string'), Variable('b', u'string'), Variable('c', u'string'), Variable('d', u'string')]

**Note:** csharp datasets support python slice_ notation: ``dataset[0:]``. 
See `variable manipulation`_ for more on using slice notation on a dataset.

Iterating over the dataset gives you access to each row contained within the dataset.

>>> for row in dataset:
... 	print row
['1', '2', '3', '4']
['1', '2', '3', '4']

--------

.. _Saving:

Saving a csharp dataset is very similar to loading. One difference is that there are two required options 
filename_ and format_. The format_ option tells Cardsharp what format the data should be in when it saves. 
To save the above ``dataset``, loaded from a .txt file, to an excel dataset: 

>>> dataset.save(filename = 'txt_to_xls_save_demo.xls', format = 'excel')

Since txt_to_xls_save_demo.xls did not exist Cardsharp created the excel workbook and saved the data to a worksheet in that workbook.

If filename already exists then a SaveError_ will be thrown.

>>> dataset.save(filename = 'txt_load_demo.txt', format = 'text')
Traceback (most recent call last):
	...
cardsharp.errors.SaveError: Cannot find a handler for format text: File txt_load_demo.txt exists, but overwrite is not set

.. _SaveError: ../modules/errors.html

To replace the contents of the existing file use ``overwrite`` option

>>> dataset.save(filename = 'txt_load_demo.txt', format = 'text', overwrite = True)

Working with Text Files
~~~~~~~~~~~~~~~~~~~~~~~

.. _Delimiter_ex:

When loading and saving a text file it is assumed that the file is tab delimited ``delimiter = \t`` 
and line delimited by \\n ``line_delimiter = \n``. To use different delimiters pass the delimiter and/or 
line_delimiter option when saving and loading. 

>>> dataset = cs.load(filename = 'txt_load_delim_demo.txt', format = 'text', delimiter = '!!!', line_delimiter = '\n\n\n')

By default the delimiter is escaped with a //. To specify a different escape character for the delimiter 
pass the escape_char option when saving and loading.

>>> dataset = cs.load(filename = 'txt_load_escape_demo.txt', format = 'text', escape_char = '#')

*Text for escape escape_eol_chars*
 
>>> dataset = cs.load(filename = 'txt_demo.txt', format = 'text', escape_eol_chars = False)

The default encoding for text files is utf-8. To load a file which is in a different encoding or to save a
file to a specific encoding use the encoding option.

>>> dataset = cs.load(filename = 'txt_load_enc_demo.txt', format = 'text', encoding = 'utf-16')
>>> dataset.save(filename = 'txt_save_enc_demo.txt', format = 'text', encoding = 'base64')
 
Working with Excel Files
~~~~~~~~~~~~~~~~~~~~~~~~
* invalid date
* styles
 
Working with SAS files
~~~~~~~~~~~~~~~~~~~~~~
* library
	
Get Dataset Information
~~~~~~~~~~~~~~~~~~~~~~~
* list datasets
* get info

Creating a Dataset
~~~~~~~~~~~~~~~~~~
To create a new csharp dataset call Dataset and pass it a list of tuples (variable name, variable type)

>>> import cardsharp as cs
>>> ds1 = cs.Dataset([('a', 'string'), ('b', 'integer'), ('c', 'datetime')])
>>> ds1[0:]
[Variable(u'a', u'string'), Variable(u'b', u'integer'), Variable(u'c', u'datetime')]

Another method is to pass a list of variable names. When a (variable name, variable type) tuple is not provided
the variable type is defaulted to 'string'.

>>> ds = cs.Dataset(['a', 'b', 'c'])
>>> ds[0:]
[Variable(u'a', u'string'), Variable(u'b', u'string'), Variable(u'c', u'string')]

**Note:** Be careful when trying to create a dataset with only one variable. Since a string is an iterator 
passing a single string to dataset will result in creating a dataset with one variable for each character 
in the string

>>> ds = cs.Dataset('abc')
>>> ds[0:]
[Variable(u'a', u'string'), Variable(u'b', u'string'), Variable(u'c', u'string')]

>>> ds = cs.Dataset(('a','integer'))
>>> ds[0:]
[Variable(u'a', u'string'), Variable(u'integer', u'string')]

>>> ds = cs.Dataset([('a','integer'),])
>>> ds[0:]
[Variable(u'a', u'integer')]

Adding a row
~~~~~~~~~~~~
Once you have created a dataset you may want to fill it up with data. You can add a row to the dataset 
with the add_row method. Add_row takes a list of values and assigns them to the variables in the order they are supplied. 

>>> import cardsharp as cs
>>> ds = cs.Dataset(list ((x, 'integer') for x in map(chr, range(97, 117))))
>>> ds.add_row(range(20))
>>> ds.add_row(range(20))
>>> def print_row(ds): 
...     for row in ds: 
...         print row
>>> print_row(ds)
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]

If your list of values is less then the number of variables None will be assigned to the variables that have missing values.

>>> ds.add_row(range(18))
>>> print_row(ds)
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, None, None]

If you supply more values than variables a FormatError will be thrown.

>>> ds.add_row(range(21))
Traceback (most recent call last):
	...
cardsharp.errors.FormatError: Cannot store u'b' in Format('integer')

Dropping a row
~~~~~~~~~~~~~~

>>> import cardsharp as cs
>>> ds = cs.Dataset('abc')
>>> ds.add_row('abc')
>>> ds.add_row('abc')
>>> ds[0:]
['a', 'b', 'c']
['a', 'b', 'c']
>>> for row in ds:
... 	row.delete()
>>> ds.add_row('def')
>>> for row in ds:
... 	print row
['d', 'e', 'f']


Waiting
~~~~~~~

Cardsharp:
cs.wait()

Dataset:
dataset.wait()

>>> import cardsharp as cs
>>> ds = cs.Dataset('abc')
>>> for x in range(1000):
... 	ds.add_row('abc')
>>> ds.save(filename = 'wait_demo.txt', format = 'text')
>>> ds1 = ds.load(filename = 'wait_demo.txt', format = 'text')

Tells Cardsharp to wait until no active marks before continuing
>>> ds.save(filename = 'wait_demo.txt', format = 'text')
>>> cs.wait()
>>> ds1 = ds.load(filename = 'wait_demo.txt', format = 'text')

Tells Cardsharp to wait until no active marks on ds before continuing 
>>> ds.save(filename = 'wait_demo.txt', format = 'text')
>>> ds.wait()
>>> ds1 = ds.load(filename = 'wait_demo.txt', format = 'text')



Options
~~~~~~~
Cardsharp supports the following load and save options.

filename_ : All : Required
	Name of the file you are trying to save to or load from

format_ : All : Required
	The format of the dataset you are trying to save or load
	
+-----------------------+------------+-------------------+
| Load/Save Paramerter  | Applies To |      Example      |
+-----------------------+------------+-------------------+
| filename_             |    All     | Filename_ex_      |
+-----------------------+------------+-------------------+
| format_               |    All     | Format_ex_        |
+-----------------------+------------+-------------------+
| handler_              |    All     | Handler_ex_       |
+-----------------------+------------+-------------------+
| dataset_              |    All     | Dataset_ex_       |
+-----------------------+------------+-------------------+
| limit_                |    All     | Limit_ex_         |
+-----------------------+------------+-------------------+
| sample_               |    All     | Sample_ex_        |
+-----------------------+------------+-------------------+
| skip_                 |    All     | Skip_ex_          |
+-----------------------+------------+-------------------+
| rename_     ????      |    All     | Rename_ex_        |
+-----------------------+------------+-------------------+
| delimiter_            |    Text    | Delimiter_ex_     |
+-----------------------+------------+-------------------+
| line_delimiter_       |    Text    | Line_delim_ex_    |
+-----------------------+------------+-------------------+
| escape_char_          |    Text    | Escape_char_ex_   |
+-----------------------+------------+-------------------+
| escape_eol_chars_     |    Text    | Esc_eol_chrs_ex_  |
+-----------------------+------------+-------------------+
| encoding_             |    Text    | Encoding_ex_      |
+-----------------------+------------+-------------------+
| invalid_date_         |   Excel    | Invalid_date_ex_  | 
+-----------------------+------------+-------------------+
| styles_               |   Excel    | Styles_ex_        |
+-----------------------+------------+-------------------+
| library_              |    SAS     | Library_ex_       |
+-----------------------+------------+-------------------+

.. _Loading: 

.. _Format_ex:
	
To specify which format Cardsharp should use to load the file as pass in a format parameter, this will 
also help determine the handler that Cardsharp should use.

>>> dataset = cs.load(filename = 'txt_demo.txt', format = 'text')
	
.. _Handler_ex:

While there currently are none, Cardsharp supports multiple loaders for a given file format, to force 
Cardsharp to use a specific loader use the handler_ parameter.

>>> dataset = cs.load(filename = 'txt_demo.txt', format = 'text', handler = 'cardsharp.loaders.text')

.. _Dataset_ex: 

>>> d1 = cs.load(filename = 'excel_demo.txt', format = 'excel' dataset = 'Sheet1')
>>> d2 = cs.load(filename = 'excel_demo.txt', format = 'excel' dataset = 'Sheet2')

.. _Limit_ex:

Limit: To limit the dataset to a certain number of rows pass the number of rows you want included 
to the limit parameter. Cardsharp will load limit number of rows starting at row 0. 
Below example limits the dataset to the first two rows. 

>>> dataset = cs.load(filename = 'txt_demo.txt', format = 'text', limit = 2)

.. _Sample_ex:

Sample: To get a sample of the dataset pass in the sample parameter, 0 < valid_range <= 1. 
The sample paramet make every row have an x chance to be loaded where x = sample. In the below example 
each row will have a 50% chance to be loaded.
 
>>> dataset = cs.load(filename = 'txt_demo.txt', format = 'text', sample = .5)

.. _Skip_ex:

Skip: To skip rows when loading pass the number of rows you want to skip to the skip parameter. 
Below example skips the first three rows in the dataset.

>>> dataset = cs.load(filename = 'txt_demo.txt', format = 'text', skip = 3)

.. _rename:

Rename: Internal function?

Variable Manipulation
---------------------
Add Variables
~~~~~~~~~~~~~

Drop Variables
~~~~~~~~~~~~~~
>>> import cardsharp as cs
>>> ds = cs.Dataset(list ((x, 'integer') for x in map(chr, range(97, 117))))
>>> ds.add_row(range(20))
>>> ds.add_row(range(20))
>>> for row in ds: print row
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]

remove an individual column from the dataset by directly calling the variable's integer index

>>> del ds[0]
>>> del ds[-1]
>>> for row in ds: print row
[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]

remove ranges of columns with slice notation using variable index

>>> del ds[-4:]
>>> for row in ds: print row
[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]

using variable names in slice: remove ranges of columns

>>> del ds['b':'d']
>>> for row in ds: print row
[3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
[3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]

remove columns with extended slice step argument

>>> del ds[::-3]
>>> for row in ds: print row
[3, 4, 6, 7, 9, 10, 12, 13]
[3, 4, 6, 7, 9, 10, 12, 13]
	
Set Variable Values
~~~~~~~~~~~~~~~~~~~
>>> import cardsharp as cs
>>> ds = cs.Dataset(list ((x, 'integer') for x in map(chr, range(97, 117))))
>>> ds.add_row(range(20))
>>> ds.add_row(range(20))
>>> def print_row(ds): 
...     for row in ds: 
...         print row
>>> print_row(ds)
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]

assign values to individual columns in the dataset by assigning to the variable's integer index 

>>> for row in ds: 
...     ds[0] = 100
>>> print_row(ds)
[100, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
[100, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]

assign values to ranges of columns with slice notation using variable index

>>> for row in ds: 
...     ds[14:] = 0
>>> print_row(ds)
[100, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 0, 0, 0, 0, 0, 0]
[100, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 0, 0, 0, 0, 0, 0]

assign values to ranges of columns with slice notation using variable names

>>> for row in ds: 
...     ds['k':'o'] = 1
>>> print_row(ds)
[100, 1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0]
[100, 1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0]

assign values to columns with extended slice step argument

>>> x = 20
>>> for row, x in zip(ds, range(20)): 
...     ds[::2] = 50
>>> print_row(ds)
[50, 1, 50, 3, 50, 5, 50, 7, 50, 9, 50, 1, 50, 1, 50, 0, 50, 0, 50, 0]
[50, 1, 50, 3, 50, 5, 50, 7, 50, 9, 50, 1, 50, 1, 50, 0, 50, 0, 50, 0]
	

Converting Variables
~~~~~~~~~~~~~~~~~~~~
Covert all the values of a specific variable:

>>> import cardsharp as cs
>>> ds = cs.Dataset(('int_var', 'integer'), ('float_var', 'float'))
>>> ds.add_row(1, 1.1)
>>> ds.add_row(2, 2.2)
>>> ds['int_var'].convert('string')
>>> for row in ds:
... 	print row
[u'1', 1.1]
[u'2', 2.2]

If the conversion is not supported you get an FormatError

>>> ds['float_var'].convert('datetime')
Traceback (most recent call last):
	...
cardsharp.errors.FormatError: Cannot automatically convert from float to datetime

See convert_ for list of all avaialable conversions.

.. _convert: ../modules/convert.html