# Wigglinde 1.1

[Downloads und SHA-256](https://github.com/muelli1975/Wigglinde/releases/tag/v1.1) · [English](README.md)

Wigglinde ist ein lokales Programm, das Wiggle-Animationen aus bereits
justierten Full-SBS-Stereofotos erzeugt. **Lite Any Stereo V2 H (LAS2-H)** oder
**IGEV++ Middlebury** berechnet aus den vorhandenen linken und rechten Ansichten die Tiefe; **MPEG-I RVS** rendert
die Zwischenansichten.

Die Verarbeitung läuft lokal, ohne Konto, Cloud oder Tracking. Das portable Paket
enthält Modell und Laufzeiten; automatische Downloads sind nicht erforderlich.
Die Oberfläche ist auf Deutsch und Englisch verfügbar.

![Wigglinde 1.1 – englische Oberfläche](docs/screenshots/Wigglinde.png)

## Voraussetzungen und Installation

- Windows 10 oder 11 mit 64 Bit; oder Linux x64 (Ubuntu 22.04 oder neuer); oder macOS ab Version 15, mit getrennten Paketen für Apple Silicon und Intel.
- CPU-Verarbeitung wird auf allen drei Systemen unterstützt. Unter Windows können kompatible NVIDIA-, AMD- und Intel-Grafikkarten
  mit DirectX-12-Treiber die Tiefenberechnung über DirectML beschleunigen.
- Keine separate Python-Installation, kein CUDA-Toolkit und keine Build-Werkzeuge nötig.

[Wigglinde_1.1_Windows_x64.zip](https://github.com/muelli1975/Wigglinde/releases/download/v1.1/Wigglinde_1.1_Windows_x64.zip) entpacken und `Wigglinde\Wigglinde.exe` starten.
Unter Linux [Wigglinde_1.1_Linux_x64.tar.gz](https://github.com/muelli1975/Wigglinde/releases/download/v1.1/Wigglinde_1.1_Linux_x64.tar.gz) entpacken und `Wigglinde/Wigglinde` starten.
Unter macOS das passende [Wigglinde_1.1_macOS_AppleSilicon.zip](https://github.com/muelli1975/Wigglinde/releases/download/v1.1/Wigglinde_1.1_macOS_AppleSilicon.zip) oder
[Wigglinde_1.1_macOS_Intel.zip](https://github.com/muelli1975/Wigglinde/releases/download/v1.1/Wigglinde_1.1_macOS_Intel.zip) entpacken und `Wigglinde/Wigglinde.app` öffnen.
Die Mac-Apps sind ad hoc signiert, ohne Apple-Notarisierung. macOS kann nach dem
ersten Start eine Freigabe unter **Systemeinstellungen → Datenschutz & Sicherheit → Dennoch öffnen** verlangen.
Den vollständigen Programmordner zusammenhalten, einschließlich Modell und Assets
neben der Mac-App. Die Verarbeitung funktioniert offline. Der Fertigstellungssound
unter Linux nutzt `paplay` oder `aplay`, sofern installiert. Linux und macOS verwenden
ausschließlich CPU/Float32.

## Bedienung

1. Einzelbild oder Bildordner auswählen. Nur Bilder direkt im gewählten Ordner
   werden verarbeitet; Unterordner bleiben unberücksichtigt.
2. Den Ausgabeordner neben der Eingabe verwenden oder einen eigenen Ordner auswählen.
3. Format, Größe, Bildrate und Zyklusdauer wählen.
4. **LAS2-H** (Standard) oder **IGEV++ Middlebury** wählen.
5. Bei Bedarf **Tiefenkarten zusätzlich speichern** einschalten.
6. CPU oder Grafikkarte auswählen und **Start** drücken.

Die Eingabe muss Full-SBS sein: das ungestauchte linke Halbbild links, das rechte
rechts. Wigglinde justiert nicht, tauscht keine Ansichten, beschneidet nicht und
ändert die Scheinfensterlage nicht. Unterstützt werden JPEG, PNG, TIFF und BMP
mit deckenden RGB-/Graustufenpixeln und 8 Bit pro Kanal. EXIF-Ausrichtung und
eingebettete Farbprofile werden berücksichtigt.

Beim ersten Start gelten **LAS2-H, MP4, 720p, 30 fps, zwei Sekunden pro Zyklus und CPU**.
Kleine Eingaben werden nicht vergrößert. Seitenverhältnis und vollständige Bildränder
bleiben erhalten. Vor der Tiefenberechnung wird mit Lanczos verkleinert.

## Animationsausgabe

| Format | Maximale Größe | Bildrate | Ablauf |
| --- | --- | --- | --- |
| MP4 | 720 / 1080 / 2160 Pixel Höhe | 30 / 60 fps | Fünf Pendelzyklen |
| AVIF | 720 / 1080 / 2160 Pixel Höhe | 30 / 60 fps | Endlosschleife; Qualität 60, 4:4:4 |
| GIF | 640 / 800 / 1024 Pixel lange Seite | 10 / 15 / 20 / 25 fps | Endlosschleife |
| PNG-Bildfolge | 1080 / 2160 Pixel Höhe | 30 / 60 fps | Ein nummerierter Zyklus |

Die Zyklusdauer ist von 0,5 bis 30 Sekunden einstellbar. Die Bewegung ist sinusförmig,
ohne doppeltes Schlussbild. Rückweg und Wiederholungen verwenden dieselben gerenderten
Ansichten. MP4 nutzt H.264 CRF 18/slow; GIF eine gemeinsame Palette für den gesamten
Zyklus. Ungerade MP4-Maße werden um höchstens eine schwarze Pixelzeile/-spalte ergänzt,
ohne Bildränder abzuschneiden.

LAS2-H bleibt der bewährte Standard und verwendet vier feste Iterationen.
IGEV++ Middlebury verwendet 16 feste Iterationen und ist eine langsamere Alternative
für schwierige Strukturen, etwa Geländer. Das Ergebnis hängt vom Motiv ab; keines
der Modelle ist bei jedem Bild besser. Auf CPU wird Float32 verwendet; auf GPU eine
separate Mixed-Precision-Fassung mit Float16/Float32. Ausgewählte Normalisierungs-,
Wahrscheinlichkeits-, Summen- und Abtastoperationen bleiben in Float32.
**RVS rendert in beiden Modi auf CPU**, mit Precision 1, RGB und Simple-Blending mit Faktor 5.
Unabhängige Ansichten werden innerhalb der CPU- und Speichergrenzen parallel berechnet.

Große Bilder benötigen mehr Speicher. Mixed Precision garantiert nicht, dass 2160p
auf jede Grafikkarte passt. Speicherfehler ändern Gerät, Modell, Auflösung oder
Präzision nicht automatisch. Feine Strukturen, Verdeckungen, Glas und Spiegelungen
können weiterhin Doppelkonturen oder Übergangsstörungen verursachen.


AVIF startet mit 720p bei 30 fps und wird als Endlosschleife abgespielt.

## Ausgabe und Tiefenkarten

Standardziel ist `output` neben dem Einzelbild beziehungsweise im gewählten Bildordner.
Alternativ kann ein eigener Ausgabeordner verwendet werden.

| Ordner | Inhalt |
| --- | --- |
| `wiggle` | MP4, GIF, AVIF oder ein Ordner je PNG-Bildfolge |
| `depth_maps` | Optionale linke/rechte 16-Bit-PNG-Tiefenkarten und Angaben zur Skala |
| `_temp` | Temporäre Arbeitsdateien, die nach der Verarbeitung entfernt werden |

Namen behalten den ursprünglichen Stamm, beispielsweise `Bild_wiggle_30fps_720p_las2-h.mp4`,
ohne Quellordnerpräfixe. Zusätze werden klein geschrieben. Der feste Modellzusatz lautet
`las2-h` oder `igev-middlebury`, auch bei GIFs, PNG-Bildfolgen und Tiefenkarten.
Dadurch bleiben Ergebnisse beider Modelle nebeneinander erhalten, beispielsweise
`Bild_depth_720p_igev-middlebury_left.png`. Fertige Animationen werden
erst nach erfolgreichem Export ersetzt. **Abbrechen** stoppt die Verarbeitung;
bereits fertige Dateien bleiben erhalten. Originale werden nicht verändert.
Auch ein leerer `_temp`-Ordner wird entfernt.

**Tiefenkarten zusätzlich speichern** verwendet die bereits berechneten Karten ohne
weiteren Modelldurchlauf. Jede gehört zum jeweiligen linken/rechten Halbbild in der
Berechnungsgröße. Beide teilen eine lineare Skala: Weiß ist nah, Schwarz ist fern.
Sie enthalten **relative Disparität, keine Entfernung in Metern**. Eine JSON-Datei dokumentiert Skala, Rückrechnung, Modell, Iterationszahl,
Rechengenauigkeit und Berechnungsgerät. Lentikular-Druckvorbereitung ist nicht enthalten.

## Einstellungen und Diagnose

Sprache, Modell, Gerät, letzte Eingabepfade, Ausgabemodus/-ordner, Tiefenkartenoption und
Animationseinstellungen werden in `settings.json` neben dem Programm gespeichert.
Diese Datei bei Aktualisierungen behalten. Wiederhergestellte Eingabepfade starten
keine automatische Verarbeitung.

**Tiefenberechnung testen** verarbeitet ein Einzelbild ohne Renderer und ohne
Kartenausgabe. Zuerst die Ausgabegröße wählen. Protokolle erfassen Laufzeiten,
Rechengenauigkeit und stichprobenartige Speicherwerte. `logs/latest_run.json` wird
bei jedem Lauf überschrieben. Fortlaufende Logs rotieren bei 5 MiB mit je drei
Sicherungen. Im normalen Stapelbetrieb laufen keine vollständigen Ausgabe-Dekodiertests.

## Quellcode und langfristige Nutzung

Das Repository enthält den Programmquellcode und Build-Anleitungen. Hinweise zur
Quellcodenutzung und zu portablen Builds stehen in [BUILD.md](BUILD.md), Prüfdetails
in den [Entwicklungsnotizen](docs/DEVELOPMENT.md). Das Release enthält den passenden
Quellstand unter `source` und Fremdlizenzhinweise unter `licenses`.

Wigglinde soll für die Weiterentwicklung und die stereoskopische Gemeinschaft
verständlich und langfristig nutzbar bleiben. Aktive Pflege, Support, Bearbeitung
von Issues oder Prüfung von Pull Requests können nicht garantiert werden.

## Lizenz

Originalcode und Dokumentation von Christoph Müller stehen unter der
[MIT-Lizenz](LICENSE). Fremdsoftware und Modellgewichte behalten ihre jeweiligen
Lizenzen. Siehe [THIRD_PARTY.md](THIRD_PARTY.md).
