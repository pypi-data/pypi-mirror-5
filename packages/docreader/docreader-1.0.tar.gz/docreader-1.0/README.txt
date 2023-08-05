DocReader

A utility for reading a CSV file and mapping it's contents to python objects
based on the field names in the document.

Contains classes for reading loosly structured documents containing rows of 
text (eg. CSV files) and turning them into slightly higher level lists of
dictionaries.

Typical usage is to create a subclass of DocReader and define the cols attribute
once. To use it, instantiate the subclass with an open file-like object (that 
supports the iterator protocol and returns a full line of text on each next()
call).

Iterating over the DocReader subclass instance will then yield a dict where the
keys are as defined in the cols attribute and the values are the cell's logical
values that have passed through the correct conversion function.

The cols attribute is itself is either a list of column names or a dictionary 
mapping keys (which will be used as the keys in the final returned data) to an 
options dictionary for that column.

An options dictionary can have the following keys:
    - column: The name of the column as it appears in the document
    - convert: A callable that will be called with the string associated with
        the data in this cell. Often a type (eg int, float) or a lambda.

>>> import decimal
>>> def _price(val):
...     txt = val.replace('$', '').strip().lower()
...     txt = txt or None
...     return decimal.Decimal(txt)
...
>>> class MyReader(DocReader):
...     cols = dict(
...         a = dict(column='a', convert=int),
...         q = dict(column='b'),
...         c = dict(column='c', convert=lambda x: int(x)),
...         price = dict(convert=_price),
...     )
...
>>> import StringIO
>>> #Ignore the use of chr(10), doctest doesn't like \n.
>>> list(MyReader(StringIO.StringIO("a,b,c,price" + chr(10) + "1,2,3,$45.6" + chr(10) + "4,5,6,$55")))
[{u'a': 1, u'q': u'2', u'c': 3, u'price': Decimal('45.6')}, {u'a': 4, u'q': u'5', u'c': 6, u'price': Decimal('55')}]
>>> list(MyReader(StringIO.StringIO("a,b" + chr(10) + "1,2")))
Traceback (most recent call last):
...
MissingColumnException: Columns missing from input: c, price

