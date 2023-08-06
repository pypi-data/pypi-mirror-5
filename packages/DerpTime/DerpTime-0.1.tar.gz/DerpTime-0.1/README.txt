===========
DerpTime
===========

DerpTime helps you to calculate deifferences between datetimes while excluding 
weekends (calculating with workdays only).

Typical usage::

    #!/usr/bin/env python

    from derptime import WorkingHoursDateTime
    from datetime import datetime, timedelta

    whdt = WorkingHoursDateTime(2013,11,11,10,10)
    
    if (whdt - timedelta(hours=24)) > datetime.now():
        print "We still have some time before the deadline!"
    


Usage
*****

Adding `timedelta` objects::
----------------------------

    >>> from derptime import WorkingHoursDateTime
    >>> from datetime import timedelta
    >>>
    >>> WorkingHoursDateTime(2013,11,8,10,10) + timedelta(hours=24)
    WorkingHoursDateTime(2013, 11, 11, 10, 10)

Subtracting `timedelta` objects::
---------------------------------

    >>> from derptime import WorkingHoursDateTime
    >>> from datetime import timedelta
    >>>
    >>> WorkingHoursDateTime(2013,11,11,10,10) - timedelta(hours=24)
    WorkingHoursDateTime(2013, 11, 8, 10, 10)

Subtracting `WorkingHoursDateTime` and/or `datetime` objects::
--------------------------------------------------------------

    >>> from derptime import WorkingHoursDateTime
    >>> from datetime import datetime, timedelta
    >>>
    >>> WorkingHoursDateTime(2013,11,11,10,10) - WorkingHoursDateTime(2013,11,8,10,10)
    datetime.timedelta(1)
    >>>
    >>> WorkingHoursDateTime(2013,11,11,10,10) - datetime(2013,11,8,10,10)
    datetime.timedelta(1)

Convert from datetime::
-----------------------

    >>> from derptime import WorkingHoursDateTime
    >>> from datetime import datetime
    >>>
    >>> WorkingHoursDateTime.from_datetime(datetime(2013,11,8,10,10))
    WorkingHoursDateTime(2013, 11, 8, 10, 10)

Convert to datetime::
---------------------

    >>> from derptime import WorkingHoursDateTime
    >>> from datetime import datetime
    >>>
    >>> WorkingHoursDateTime(2013,11,11,10,10).to_datetime()
    datetime.datetime(2013, 11, 11, 10, 10)

Using `now`::
-------------

    >>> from derptime import WorkingHoursDateTime
    >>>
    >>> # You can still use the good-old "new" classmethod the same way
    >>> WorkingHoursDateTime.now()
    WorkingHoursDateTime(2013, 11, 8, 16, 29, 28, 977699)
