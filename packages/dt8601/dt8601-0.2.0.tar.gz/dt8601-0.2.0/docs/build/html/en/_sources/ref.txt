
#########################
Reference and Definitions
#########################

******************
Definitions module
******************

The module ``definitions.py`` contains a dictionary named ``COUNTRYDATA`` with a dictionary for each country,
identified by the ISO2 code for the country. This is the definition for Germany::

        'DE': {
            'weekend': ['SA', 'SU'],
            'start_of_week': 'MO',
            'first_week': 'ISO',
            'long_day_names': {'MO':'Montag', 'TU':'Dienstag', 'WE':'Mittwoch', 'TH':'Donnerstag',
                               'FR':'Freitag', 'SA':'Samstag', 'SU':'Sonntag'},
            'short_day_names': {'MO':'MO', 'TU':'DI', 'WE':'MI', 'TH':'DO', 'FR':'FR', 'SA':'SA', 'SU':'SO'},
            'long_month_names': ['', 'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
                                 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'],
            'short_month_names': ['', 'Jan', 'Feb', 'Mrz', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez'],
            'holidays': [
                        {'name': 'Neujahrstag', 'date': 'F:01-01::'},
                        {'name': 'H. drei Könige', 'date': 'F:01-06::', 'states': ['BW', 'BY', 'ST']},
                        {'name': 'Karfreitag', 'date': 'V:easter:-2::'},
                        {'name': 'Ostersonntag', 'date': 'V:easter:::'},
                        {'name': 'Ostermontag', 'date': 'V:easter:+1::'},
                        {'name': 'Tag der Arbeit', 'date': 'F:05-01::'},
                        {'name': 'Christi Himmelfahrt', 'date': 'V:easter:+39::'},
                        {'name': 'Pfingstsonntag', 'date': 'V:easter:+49::'},
                        {'name': 'Pfingstmontag', 'date': 'V:easter:+50::'},
                        {'name': 'Fronleichnam', 'date': 'V:easter:+60::', 'states': ['BW', 'BY', 'HE', 'NW', 'RP', 'SL']},
                        {'name': 'Maria Himmelfahrt', 'states': ['BY'], 'date': 'F:08-15::'},
                        {'name': 'Tag der deutschen Einheit', 'date': 'F:10-03::'},
                        {'name': 'Reformationstag', 'states': ['BB', 'SN', 'MV', 'ST', 'TH'], 'date': 'F:10-31::'},
                        {'name': 'Allerheiligen', 'date': 'F:11-01::', 'states': ['BW', 'BY', 'NW', 'RP', 'SL']},
                        {'name': 'Buß- und Bettag', 'date': 'V:advent:-WE::1995-', 'states': ['SN']},
                        {'name': 'Buß- und Bettag', 'date': 'V:advent:-WE::-1994'},
                        {'name': '1. Weihnachtstag', 'date': 'F:12-25::'},
                        {'name': '2. Weihnachtstag', 'date': 'F:12-26::'},
                        ],
        }

Please have a look the code in the ``definitions.py`` module, where you also will find all the abbreviations
for the state codes. Country codes will always be ISO2.


**********************
How to define holidays
**********************

The `definitions.py` module contains core definitions for the package in a structure based on country.
The holiday section for each country may contain holiday definitions in a text-based formula.


Fixed or variable holiday
=========================

Public holidays may occur on a fixed date (same month and day every year) or on variable dates that
may change every year (Easter / Pentecost). For fixed holidays, use `F` as the first letter of the
definition, for variable holidays use a `V` as the first letter.


Fixed holidays
--------------

A definitions for a fixed holiday consists of four fields:

 * 'F'
 * <month>-<day>
 * <spread>
 * <validity>

A simple example would be Labor Day in Europe, always on May, 1st:  ``F:05-01::``.
As you can see, content for fields `spread` and validity` are optional.


Variable holidys
----------------

A definition for a variable holiday consists of five fields:

 * 'V'
 * <basedate>
 * <formula>
 * <spread>
 * <validity>

We use the definition for Ascension in Germany (39 days after Easter): ``V:Easter+39``.


What is "spread"?
-----------------

In many countries there are special rules if a holiday occurs on a weekend. Independence Day in
the United States is an example. If the 4th of July is a saturday, the firday will not be a
workday. The field `spread` is used for this purpose.

The definitions consists of the weekday of the holiday and the spreading of the day. Let's
stick to our example of Independence Day: if July 4th is a sunday, the monday will be a day off
in addition to the rule for saturday. So we define the field value as ``SA-FR``for the first
part and ``SU+MO`` for the second part. Both parts will be separated by a comma, like so:
``F:07-04:SA-FR,SU+MO:`` (the last field validity is empty).

In Great Britain there is a rule for Christmas Day: is December, 25th is on a weekend, the
next tuesday is not a working day: ``F:12-25:SA+TU,SU+TU:``


Validity
--------

If a holiday is valid only up until a certain year of from a certain year, you may use the
`validity` field to store that information. Starting next year, the Netherlands will be
celebrating "Konigsdag" on April 27. Up and including 2013, the "Koniginnendag" is
April 30th. This day has been celebrated starting 1949, when Queen Juliana became Queen.
(to our friends from The Netherlands: I hope I got that right, if I need to make corrections,
please let me know)

 * so this is the definitions for the Koniginnendag:  ``F:04-30:SU-SA:1949-2013``
 * and this is the definitions for the Konigsdag:  ``F:04-27:SU-SA:0-2014``



Formel
------

For variable holidays you may specify a formula, based on a starting point in time.
In th esouthern part of Germany, Ascension will be celebrated 39 days after Easter.
So the base date would be ``Easter``. As 39 days after Easter is always a thursday,
you have two options to specify this:

 * alternative 1: ``Easter+39``
 * alternative 2: ``Easter+TH+TH+TH+TH+TH+TH``


More examples
=============

October Bank Holiday (Irland)
----------------------------

V:Nov-1-MO  (last monday in october)


Independence Day (USA)
----------------------

F:07-04:SA-FR,SU+MO:

 * fixed
 * Falls Samstag, ist der Freitag frei
 * Falls Sonntag, ist der Montag frei


Martin Luther King Day (USA)
----------------------------

V:Feb+MO+MO+MO

 * variable
 * Basisdatum ist ``Feb`` (also der 1. Februar)
 * dann der dritte Montag


Christmas Day / Boxing Day (UK)
-------------------------------

F:12-25:SA+TU,SU+TU:
F:12-26:SA+MO,SU+MO:

 * fixed
 * falls der 25.12. ein Wochenende ist, ist der nächste Dienstag frei
 * falls der 26.12. ein Wochenende ist, ist der nächste Montag frei
 * keine Gültigkeit bedeutet immer


