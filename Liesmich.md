# Wigglinde 0.1 – Testversion 1

Den vollständigen Ordner entpacken und `Wigglinde.exe` starten. Modelle und Laufzeiten
sind enthalten; keine Installation, Anmeldung oder Internetverbindung erforderlich.

1. Dateien oder einen Ordner mit fertig justierten SBS-Bildern auswählen.
2. Full-SBS beziehungsweise Half-SBS passend zur Eingabe wählen. Bei Bedarf L/R tauschen.
3. Ausgabeziel, Format, Größe, Bildrate und Zyklusdauer wählen; mit Start verarbeiten.

| Format | Größe | Bildrate | Ablauf |
| --- | --- | --- | --- |
| MP4 | maximal 720 / 1080 / 2160 Pixel Höhe | 30 / 60 fps | fünf Pendelzyklen |
| GIF | maximal 640 / 800 / 1024 Pixel lange Seite | 10 / 15 / 20 / 25 fps | Endlosschleife |
| PNG-Bildfolge | maximal 1080 / 2160 Pixel Höhe | 30 / 60 fps | ein Pendelzyklus |

Standard: MP4, maximal 1080 Pixel Höhe, 30 fps, zwei Sekunden pro Pendelzyklus.
Seitenverhältnis und vollständige Bildränder bleiben erhalten. Kleine Eingaben werden
nicht vergrößert. Die gewählte Größe bestimmt auch die Berechnung; bei Speichermangel
wird nichts automatisch heruntergesetzt. MP4 ergänzt bei ungeraden Maßen höchstens
eine schwarze Pixelzeile/-spalte für den Videocodec.

Keine Justage, kein Beschnitt und keine Änderung der vorhandenen Scheinfensterlage.
Eingebettete Farbprofile werden nach sRGB umgerechnet. Unterstützt werden deckende
Bilder mit 8 Bit pro Kanal.

Standardziel ist `output` im Eingabeordner. Bei Ordnerverarbeitung werden relative
Unterordner erhalten. Eigene Ausgabeordner sind möglich. Gleichnamige fertige
Ausgaben werden erst nach erfolgreicher Verarbeitung ersetzt. Ein Abbruch lässt
vorherige Ergebnisse bestehen. Protokolle: `logs` im Programmordner; temporäre
Dateien: `_temp` im jeweiligen Ausgabeordner.

## Teststand und Grenzen

LAS2-M und RVS, CPU-Verarbeitung. Keine NVIDIA-Grafikkarte erforderlich. Noch kein
GPU-Modus und keine freigegebene 1.0. Große Auflösungen benötigen mehr Zeit und RAM;
zunächst einen kleinen Stapel bei 720 oder 1080 testen. Keine automatische Qualitätsabsenkung.

LAS2-M hat einen festen Suchbereich von 192 Pixeln in der Berechnungsgröße.
Sehr große Parallaxen können fehlerhafte Tiefenkarten erzeugen. RVS nutzt die
zweifache interne Abtastung und Multispectral-Blending des Fotoversuchs; seine
Endansichten sind gerenderte Bilder, keine eingesetzten Originale. Glas, Spiegelungen
und Verdeckungen können weiterhin Fehler zeigen.

Quellstand: `source`. Lizenzen: `licenses`. Keine automatischen Aktualisierungen
und keine Telemetrie.
