#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GBIF Occurrence Scanner & CSV Exporter
--------------------------------------
Author: Rainer Theuer
License: GNU General Public License v3.0 (GPLv3)

Description:
Dieses Skript sucht nach Funddaten einer Spezies in GBIF innerhalb definierter
Polygone (Sehnde, Hannover, Hildesheim). Es berechnet automatisch die TK25 (MTB)
Nummer und exportiert alle Funde ungekürzt in eine CSV-Datei.
"""

import argparse
import sys
import csv
import re
import math
from pygbif import occurrences as occ
from pygbif import species


class Gbif:
    def __init__(self, geometry):
        self.geometry = geometry

    def get_taxon_key(self, scientific_name):
        data = species.name_backbone(name=scientific_name)
        if data.get('matchType') == 'NONE':
            return None
        return data.get('usageKey')

    def calculate_mtb(self, lat, lon):
        """
        Berechnet die Nummer des Messtischblatts (TK25) basierend auf
        Breiten- und Längengrad (Referenzsystem Deutschland).
        """
        try:
            lat = float(lat)
            lon = float(lon)
            # TK25 Gitter-Logik:
            # Nord-Süd: Jedes Blatt ist 6' hoch. Referenz 56°N (Blatt 01xx)
            zeile = math.floor((56.0 - lat) * 10)
            # West-Ost: Jedes Blatt ist 10' breit. Referenz 6°E (Blatt xx01)
            spalte = math.floor((lon - 6.0) * 6) + 1
            return f"{zeile:02d}{spalte:02d}"
        except:
            return "n/a"

    def extract_creator(self, record):
        """Extrahiert den Urheber/Fotografen aus verschiedenen Metadaten-Feldern."""
        media_list = record.get('media', [])
        for item in media_list:
            if item.get('creator'): return item['creator']
            if item.get('rightsHolder'): return item['rightsHolder']

        extensions = record.get('extensions', {})
        multimedia = extensions.get('http://rs.tdwg.org/ac/terms/Multimedia', [])
        for m in multimedia:
            creator = m.get('http://purl.org/dc/elements/1.1/creator')
            if creator: return creator

        return record.get('rightsHolder') or record.get('recordedBy') or "Unbekannt"

    def fetch_all_occurrences(self, scientific_name):
        """Holt alle Funde via Paginierung ohne Limit."""
        taxon_key = self.get_taxon_key(scientific_name)
        if not taxon_key:
            print(f"[-] Fehler: Spezies '{scientific_name}' nicht gefunden.")
            return []

        all_results = []
        offset, limit = 0, 300
        print(f"[*] Starte Tiefensuche für '{scientific_name}'...")

        while True:
            sys.stdout.write(f"\r[ ] Lade Daten... (Bereits gefunden: {len(all_results)})")
            sys.stdout.flush()

            res = occ.search(taxonKey=taxon_key, geometry=self.geometry, limit=limit, offset=offset)
            records = res.get('results', [])
            all_results.extend(records)

            if len(records) < limit or res.get('endOfRecords'):
                break
            offset += limit

        print(f"\n[+] Suche abgeschlossen. {len(all_results)} Funde gefunden.")
        return all_results

    def display_and_save(self, results, species_name, location_name):
        """Speichert die Ergebnisse als CSV und gibt eine Vorschau im Terminal aus."""
        if not results:
            print(f"[-] Keine Funde in {location_name} verzeichnet.")
            return

        safe_species = re.sub(r'\W+', '_', species_name)
        filename = f"{safe_species}_{location_name}.csv"

        fields = ["Datum", "Ort", "Breitengrad", "Längengrad", "MTB_TK25", "Beobachter", "Urheber", "Quelle"]
        fmt = "{:<11} | {:<12} | {:<18} | {:<8} | {:<12} | {:<12} | {:<}"

        print(f"\n{'VORSCHAU: ' + filename:=^120}")
        print(fmt.format("Datum", "Ort", "Koordinaten", "MTB", "Beobachter", "Urheber", "Quelle"))
        print("-" * 140)

        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(fields)

            for record in results:
                date = record.get('eventDate', 'N/A')[:10]
                loc = record.get('locality', 'k.A.')
                lat = record.get('decimalLatitude', 'n/a')
                lon = record.get('decimalLongitude', 'n/a')
                coords = f"{lat}, {lon}" if lat != 'n/a' else "n/a"
                mtb = self.calculate_mtb(lat, lon)
                obs = record.get('recordedBy', 'N/A')
                cre = self.extract_creator(record)
                src = record.get('references') or record.get('occurrenceID') or "n/a"

                # Ungekürzt in CSV
                writer.writerow([date, loc, lat, lon, mtb, obs, cre, src])

                # Gekürzt für Terminal
                print(fmt.format(
                    date,
                    (loc[:10] + '..') if len(loc) > 12 else loc,
                    (coords[:16] + '..') if len(coords) > 18 else coords,
                    mtb,
                    (obs[:10] + '..') if len(obs) > 12 else obs,
                    (cre[:10] + '..') if len(cre) > 12 else cre,
                    src
                ))

        print(f"\n[+] Datei erfolgreich gespeichert: {filename}")


def main():
    locations = {
        'Sehnde': 'POLYGON((9.850617 52.279406, 10.084077 52.279406, 10.084077 52.370893, 9.850617 52.370893, 9.850617 52.279406))',
        'Hannover': 'POLYGON((9.40 52.15, 10.25 52.15, 10.25 52.65, 9.40 52.65, 9.40 52.15))',
        'Hildesheim': 'POLYGON((9.65 51.85, 10.20 51.85, 10.20 52.30, 9.65 52.30, 9.65 51.85))'
    }

    # Ausführlicher Hilfetext für -h
    epilog_text = """
HILFE ZUR ERSTELLUNG VON POLYGONEN:
----------------------------------
Polygone werden im WKT-Format (Well-Known Text) definiert.
Format: 'POLYGON((Lon1 Lat1, Lon2 Lat2, Lon3 Lat3, Lon4 Lat4, Lon1 Lat1))'

Anleitung:
1. Koordinaten finden (z.B. Google Maps oder bboxfinder.com).
2. WICHTIG: GBIF nutzt 'Längengrad Breitengrad' (Longitude Latitude). 
   Google Maps liefert meist 'Breitengrad, Längengrad'. Diese müssen vertauscht werden!
3. Das Polygon muss GESCHLOSSEN sein (der erste und letzte Punkt müssen identisch sein).
4. Beispiel für ein Rechteck:
   Süd-West Ecke: 9.85 52.27
   Nord-Ost Ecke: 10.08 52.37
   WKT: POLYGON((9.85 52.27, 10.08 52.27, 10.08 52.37, 9.85 52.37, 9.85 52.27))

Autor: Rainer Theuer | Lizenz: GNU GPLv3
"""

    parser = argparse.ArgumentParser(
        description="GBIF MTB Scanner: Funddaten abfragen und als CSV exportieren.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=epilog_text
    )

    parser.add_argument("--specie", type=str, required=True,
                        help="Wissenschaftlicher Name der Art (z.B. 'Apatura iris')")
    parser.add_argument("--location", type=str, required=True, choices=locations.keys(),
                        help="Vordefinierte Region für die Suche")

    args = parser.parse_args()

    scanner = Gbif(geometry=locations[args.location])
    results = scanner.fetch_all_occurrences(args.specie)
    scanner.display_and_save(results, args.specie, args.location)


if __name__ == "__main__":
    main()
