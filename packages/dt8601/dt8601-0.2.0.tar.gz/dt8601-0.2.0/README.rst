######
dt8601
######

dt8601 (short for "dates in ISO8601 logic") provides useful functionality to work with gregorian
dates. This is my first open source project in Python, so please bear with me. The code is based
on a date library I wrote back in to 90s in another language and has proven to be very helpful
when you have to work with date arithmetic.


***********
Quick start
***********

*dt8601* provides two objects to work with dates. One allows for easy storages and calculations with
a date and the other provides functionality that is associated with a calendar year.

Typical usage in most cases is as easy as this::

    #!/usr/bin/env python

    import dt8601

    ymd = dt8601.IsoDate(2013, 06, 25, 'DE')
    year = dr8601.IsoYear(2013)

    num_weeks = year.week_count  # number if weeks in 2013

    print(ymd.day_of_year())   # day of year
    print(ymd.day_of_week())   # get week day for 2013-06-25
    print(ymd.week_of_year())  # get ISO calendar week for 2013-06-25


You would like to get a list of all the start dates for every ISO calendar week in 2013?
As easy as::

 from dt8601 import IsoYear

 yr = IsoYear(2013)

 for the_week in yr.iso_weeks:
     print(the_week['start'])


You can find more information in the ``docs`` folder (es gibt auch eine deutsche Doku dort!)



Thanks also to
==============

This module is a result of porting and reworking a Borland Delphi library that is now more than 20 years old
(yes, we had computers back then <g>). Many people inspired this library, helped and added code or explained things.

Bernd Strehuber - Holiday calculations
Carley Phillips - Julian date calculations
Jeff Duntemann - Weekday calculations
Judson McClendon - Easter calculations
Martin Austermeier - Weekday calculations
Paul Schlyter - Easter calculation
Pit Biernath - Julian date calculations
Scott Bussinger - Julian date calculations
Markus Kuhn for his ISO8601 summary

Also many thanks to the Wikipedia authors of the ISO8601 articles and last, but not least, the awesome group of
people on http://www.stackoverflow.com




