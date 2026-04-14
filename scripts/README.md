# GBIF Occurrence Scanner & CSV Exporter

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

Ein leistungsstarkes Python-Tool zur automatisierten Abfrage von Biodiversitätsdaten aus der **GBIF-Datenbank** (Global Biodiversity Information Facility). Das Skript ermöglicht die gezielte Suche nach Arten in vordefinierten Regionen, berechnet das deutsche **Messtischblatt-Raster (TK25)** und exportiert die Ergebnisse in eine Excel-kompatible CSV-Datei.

**Autor:** Rainer Theuer  
**Lizenz:** GNU GPLv3

---

## 🚀 Hauptfunktionen

* **Vollständige Datenerfassung:** Umgeht das 1000er-Limit der GBIF-API durch automatische Paginierung (Offset-Handling).
* **MTB-Berechnung:** Wandelt GPS-Koordinaten (WGS84) automatisch in die entsprechende vierstellige **Messtischblatt-Nummer (TK25)** um.
* **Intelligente Urheber-Extraktion:** Findet Fotografen-Namen (z. B. "Rainer Theuer") auch in tief verschachtelten Multimedia-Metadaten (Dublin Core Extensions).
* **CSV-Export:** Erzeugt eine saubere, mit `;` getrennte Datei für die direkte Weiterverarbeitung in Excel, LibreOffice oder GIS-Software.
* **Vordefinierte Regionen:** Schneller Zugriff auf Polygone für **Sehnde**, **Hannover** und **Hildesheim**.

---

## 🛠 Installation

1.  **Repository klonen oder Skript kopieren:**
    ```bash
    git clone [https://github.com/dein-username/Lepidoptera.git](https://github.com/dein-username/Lepidoptera.git)
    cd Lepidoptera
    ```

2.  **Virtuelle Umgebung erstellen (empfohlen):**
    ```bash
    python -m venv .venv
    # Aktivieren unter Windows:
    .venv\Scripts\activate
    # Aktivieren unter Linux/Mac:
    source .venv/bin/activate
    ```

3.  **Abhängigkeiten installieren:**
    ```bash
    pip install pygbif
    ```

---

## 📖 Benutzung

Das Skript wird über die Kommandozeile gesteuert.

### Basis-Befehl
```bash
python gbif.py --specie "Apatura iris" --location Sehnde
