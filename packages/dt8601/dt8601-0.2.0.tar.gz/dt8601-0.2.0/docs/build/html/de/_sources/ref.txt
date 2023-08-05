
#########################
Referenz und Definitionen
#########################

*****************
Definitions-Modul
*****************

Das Modul ``definitions.py`` enthält ein Dictionary mit dem Namen ``COUNTRYDATA`` und einem Dictionary
für jedes Land, das durch den ISO2-Codes identifiziert wird. Hier die Definition für Deutschland::

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

Im Modul ``definitions.py`` finden Sie auch die Abkürzungen für die einzelnen Bundesstaaten der Länger.


*************************
Definition von Feiertagen
*************************


Feste oder variable Feiertage
=============================

Ein Feiertag kann entweder ein fixer Feiertag sein (der an jedem Jahr zum gleichen Datum gefeiert wird)
oder ein variabler Feiertag, dessen Datum sich jährlich ändern kann (z.B. Pfingsten).
Dies wird durch die Verwendung von `F` oder `V` als erstem Buchstaben der Definition ausgedrückt.

Feste Feiertage
---------------

Für einen fixen Feiertag besteht die Definition aus vier Feldern:

 * 'F'
 * <monat>-<tag>
 * <verschiebung>
 * <gueltigkeit>

Einfaches Beispiel für den Tag der Arbeit, dieser findet immer am 1. Mai statt:  ``F:05-01::``.
Die Felder für `verschiebung` und `gueltigkeit` sind nicht gefüllt.


Variable Feiertage
------------------

Für einen variablen Feiertag besteht die Definition aus fünf Feldern:

 * 'V'
 * <basisdatum>
 * <formel>
 * <verschiebung>
 * <gueltigkeit>

Einfaches Beispiel für Christi Himmelfahrt (39 Tage nach Ostern): ``V:Easter+39``.


Verschiebung (spread)
---------------------

Für manche Feiertage gelten in vielen Ländern besondere Regelungen, wenn der Feiertag auf ein
Wochenende fällt. Dies gilt z.B. für den Independence Day in den Vereinigten Staaten.
Fällt der 4. Juli auf einen Samstag, ist der Freitag davor arbeitsfrei. Fällt der 4. Juli
auf einen Sonntag, so ist der Montag darauf arbeitsfrei. Diese Definitionen werden im Feld
für die Verschiebung (spread) abgebildet.

Die Definition besteht aus dem Wochentag des Feiertag und der Verschiebung, bestehend aus einem
Vorzeichen und einem Wochentag. Für den ersten Teil der Regelung wäre dies ``SA-FR`` (falls
Samstag, dann rückwärts der Freitag vorher). Gibt es wie im Fall des 4. Juli mehr als einen
betroffenen Tag, werden diese Teile durch Kommata getrennt. Die vollständige Definition
lautet daher ``F:07-04:SA-FR,SU+MO:`` (das Feld für die Gültigkeit ist hier leer).

Noch ein Beispiel für den ersten Weihnachtstag in Großbritannien: fällt dieser auf einen Samstag
oder Sonntag, so ist der darauf folgende Dienstag arbeitsfrei: ``F:12-25:SA+TU,SU+TU:``


Gültigkeit
----------

Bestimmte Feiertage sind erst ab einem gewissen Jahr oder nur bis zu einem bestimmten Jahr gültig.
So wurde beispielsweise in den Niederlanden der Königinnentag immer am 30. April gefeiert, aber
nur bis 2013. Ab dem Jahr 2014 wird der Königstag am 27. April gefeiert. Ein "schon immer" oder
"bis immer" kann durch den Wert 0 ausgedrückt werden. Für den Königinnentag lautet die
vollständige Definition also ``F:04-30:SU-SA:0-2013``.


Formel
------

Für variable Feiertag kann eine Formel angegeben werden, die ausgehend von einem Basisdatum
das Datum des Feiertages definiert. So wird in Süddeutschland Christi Himmelfahrt 39 Tage
nach Ostern gefeiert. Mit der Angabe von ``Easter`` als Basisdatum lautet die Formel also
``Easter+39``. Die 39 Tage sind 5 Wochen und 4 Tage, Ostern wird an einem Sonntag gefeiert,
daher ist Christi Himmelfahrt immer ein Donnerstag. Der sechste Donnerstag nach Ostersonntag, um
genau zu sein. Daher lässt sich die Formel auch folgendermaßen schreiben: ``V:Easter+TH+TH+TH+TH+TH+TH``.


Beispiele
=========

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



