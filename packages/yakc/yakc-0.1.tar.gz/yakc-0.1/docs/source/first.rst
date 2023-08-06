========================================
Yet Another Kyoto Cabinet Python Binding
========================================

:author: Yasunobu OKAMURA

yakc (Yet Another Kyoto Cabinet Python Binding) is a Python module to
manipulate Kyoto Cabinet with Python dictionary manner. This module
also can be used as drop-in replacement of Python dict if you want to
store many data in dict.

yakc focuses to replace Python dict to store huge amount of data. If
you want to Kyoto Cabinet database as key/value store, I recommend to
use the official Python binding.

License
=======

::

  Yet Another Kyoto Cabinet Python Binding
  Copyright (C) 2013  Yasunobu OKAMURA
  
  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.
  
  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.
  
  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.

How to Install
==============

From pypi
---------

::

   pip install yakc


From source code
----------------

::

   python setup.py build
   python setup.py install

Basic use
=========

::

  import yakc
  d = yakc.KyotoDB('test.kch')
  d['a'] = 123
  d[98] = [12,3,4]
  for key, value in d.iteritems():
      print key, value


