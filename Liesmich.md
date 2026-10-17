# Wigglinde 0.1 – Testversion 2

Den vollständigen Ordner entpacken und `Wigglinde.exe` starten. Modell, Renderer,
Laufzeiten und Fertigstellungssound sind enthalten; keine Installation, Anmeldung
oder Internetverbindung erforderlich. Sprache oben rechts: Deutsch oder English.

1. Ein Einzelbild oder einen Bildordner mit fertig justierten SBS-Bildern auswählen.
   Die andere Eingabe wird dabei geleert. Ordner werden mit Unterordnern verarbeitet.
2. Full-SBS beziehungsweise Half-SBS passend zur Eingabe wählen. Bei Bedarf L/R tauschen.
3. Ausgabeziel, Format, Größe, Bildrate und Zyklusdauer wählen.
4. Modell wählen: LAS2-M, LAS2-L oder LAS2-H. Standard beim ersten Start ist L.
5. Unter „Berechnung“ CPU oder eine gefundene Grafikkarte wählen. Mit Start verarbeiten.

Die Oberfläche zeigt Pfadfelder statt einer Dateiliste. Die aktuelle Datei erscheint
während der Verarbeitung im Statusbereich. Sprache, Modell, Gerätewahl und Ausgabeordner
bleiben gespeichert; Bilder werden beim nächsten Start nicht automatisch geladen.

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

## Modelle, GPU-Modus und Teststand

M benötigt weniger Rechenaufwand, L ist unser Standard, H verfeinert die Tiefenkarte
iterativ mit den veröffentlichten vier Durchläufen. H kann bei großen Fotos
besonders viel Speicher benötigen. Die Wahl ändert weder Auflösung noch Renderer.
Alle drei Modelle sind enthalten. Es gibt keine automatische Modellumschaltung.

Der GPU-Modus beschleunigt die LAS2-Tiefenberechnung über DirectML. Er benötigt eine
DirectX-12-fähige Grafikkarte und passende Treiber; kompatible NVIDIA-, AMD- und
Intel-Grafik wird unterstützt. CPU bleibt beim ersten Start vorausgewählt. Einzelne
von DirectML nicht unterstützte ONNX-Operationen können innerhalb der Modellsitzung
auf CPU laufen. Ein fehlgeschlagener GPU-Start wird gemeldet; kein stiller Wechsel
des gesamten Auftrags auf CPU. Bei Problemen CPU ausdrücklich auswählen.

**RVS rendert auch im GPU-Modus weiterhin auf CPU**, mit unveränderter zweifacher
interner Abtastung und Multispectral-Blending 1/4. Die gesamte Laufzeit wird deshalb
nicht im selben Verhältnis sinken wie die Tiefenberechnung. Modell, Präzision,
Auflösung und Rendererqualität werden nicht automatisch verändert.

Geschwindigkeit und Bildqualität des GPU-Modus müssen auf echten Grafikkarten
praktisch verglichen werden. Ein Windows-Buildtest auf einem gehosteten Server
ersetzt das nicht. Noch keine freigegebene 1.0. Große Auflösungen benötigen mehr
Zeit und Speicher. Das eigene Programmsymbol wird später ergänzt.

LAS2 hat einen festen Suchbereich von 192 Pixeln in der Berechnungsgröße.
Sehr große Parallaxen können fehlerhafte Tiefenkarten erzeugen. Die RVS-Endansichten
sind gerenderte Bilder, keine eingesetzten Originale. Glas, Spiegelungen und
Verdeckungen können weiterhin Fehler zeigen. Feine Aststrukturen können während
der Animation gedoppelt erscheinen; dieser gemeldete Qualitätsfehler ist noch offen.

Quellstand: `source`. Lizenzen: `licenses`. Keine automatischen Aktualisierungen
und keine Telemetrie.
