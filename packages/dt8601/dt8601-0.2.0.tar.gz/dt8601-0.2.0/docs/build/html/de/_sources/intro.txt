######
dt8601
######

dt8601 (Kurzform für "dates in ISO8601 logic") ist ein Lernprojekt für mich, um tiefer in die Programmierung
mit Python einzusteigen und gleichzeitig etws nützliches für die Python-Programmierer zu schaffen.
Dies ist mein erstes Open Source Projekt in Python, erfahrene Entwickler bitte ich also um Nachsicht,
wenn sie beim Anblick des Codes schreiend den Raum verlassen wollen ;-)

************
Schnellstart
************

*dt8601* bietet zwei grundlegende Objekte zum Arbeiten mit Datumswerten. Damit sind Sie in der Lage,
Berechnungen mit Datumswerten auf einfache Art und Weise auszuführen.
Der typische Einsatz sieht in vielen Fällen so aus::

    #!/usr/bin/env python

    import dt8601

    ymd = dt8601.IsoDate(2013, 06, 25, 'DE')

    print(ymd.day_of_year())   # Tag des Jahres ausgeben
    print(ymd.day_of_week())   # Wochentag ausgeben
    print(ymd.week_of_year())  # ISO-Kalenderwoche ausgeben




Sie wollen eine Liste mit dem Startdatum aller Kalenderwochen in 2013? Nichts einfacher als das::

 from dt8601 import IsoYear

 yr = IsoYear(2013)

 for the_week in yr.iso_weeks:
     print(the_week['start'])

