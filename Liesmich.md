# Wigglinde 1.0

Wigglinde erzeugt Wiggle-Animationen aus fertig justierten Full-SBS-Stereofotos.
Den vollständigen Ordner entpacken und `Wigglinde.exe` starten. Modell, Renderer,
Laufzeiten, Icon und Fertigstellungssound sind enthalten. Windows 10/11 x64;
keine Installation, Anmeldung oder Internetverbindung für die Verarbeitung erforderlich.
Sprache oben rechts: Deutsch oder English.

1. Einzelbild oder Bildordner auswählen. Die andere Eingabe wird dabei geleert.
   Bildordner werden einschließlich ihrer Unterordner verarbeitet.
2. Die linke Ansicht muss links und die rechte rechts stehen, mit ungestauchten Halbbildern.
3. Ausgabeziel, Format, Größe, Bildrate und Zyklusdauer wählen.
4. Bei Bedarf „Tiefenkarten zusätzlich speichern“ einschalten.
5. CPU oder Grafikkarte unter „Berechnung“ wählen und Start drücken.

Standard: **MP4, maximal 720 Pixel Höhe, 30 fps, zwei Sekunden pro Pendelzyklus, CPU**.
LAS2-H bleibt fest eingestellt: vier Iterationen, Float32. Sprache, Gerätewahl,
Tiefenkartenoption und Ausgabeordner bleiben gespeichert. Bilder werden beim
nächsten Start nicht automatisch geladen. Die Oberfläche verwendet keine Dateiliste.

| Format | Maximale Größe | Bildrate | Ablauf |
| --- | --- | --- | --- |
| MP4 | 720 / 1080 / 2160 Pixel Höhe | 30 / 60 fps | Fünf Pendelzyklen |
| GIF | 640 / 800 / 1024 Pixel lange Seite | 10 / 15 / 20 / 25 fps | Endlosschleife |
| PNG-Bildfolge | 1080 / 2160 Pixel Höhe | 30 / 60 fps | Ein Pendelzyklus |

Zyklusdauer 0,5 bis 30 Sekunden, sinusförmige Bewegung ohne doppeltes Schlussbild.
Rückweg und Wiederholungen verwenden dieselben berechneten Ansichten.
MP4: H.264 CRF 18/slow; GIF: gemeinsame Palette für den gesamten Zyklus.

Die gewählte Größe bestimmt die Berechnung bereits vor LAS2. Verkleinerung mit
Lanczos, Seitenverhältnis und vollständige Bildränder bleiben erhalten. Kleine
Eingaben werden nicht vergrößert. MP4 ergänzt bei ungeraden Maßen höchstens eine
schwarze Pixelzeile/-spalte. Unterstützt werden deckende RGB-/Graustufenbilder mit
8 Bit pro Kanal. Eingebettete Farbprofile werden nach sRGB umgerechnet.
Keine Justage, kein L/R-Tausch, kein Beschnitt und keine Scheinfensteränderung.

## Ausgabe

Standardziel ist `output` im gewählten Eingabeordner beziehungsweise neben dem
Einzelbild. Ein eigener Ausgabeordner ist ebenfalls möglich. Darin liegen:

- `wiggle`: MP4, GIF oder Ordner mit PNG-Bildfolgen.
- `depth_maps`: die optionalen Tiefenkarten, nur bei eingeschalteter Speicheroption.

Wie bei SplatTricia wird der relative Unterordnerpfad in den Dateinamen übernommen,
mit `__` als Trenner. Bei Eingabeordner `Urlaub` wird `Urlaub/Tag1/Bild.jpg` zum Beispiel
zu `output/wiggle/Tag1__Bild_wiggle_30fps_720p.mp4`. Es entsteht kein Unterordner `Tag1`.
Einzelbilder behalten ihren ursprünglichen Stammnamen. Zusätze sind klein geschrieben:
`p` für die Bildhöhe, bei GIF `px` für die lange Seite; PNG-Folgen enden auf `_png`.
Fertige Animationen werden erst nach erfolgreichem Export ersetzt; Originale bleiben erhalten.

Die Tiefenkarten werden ohne zusätzliche Modellberechnung als 16-Bit-Graustufen-PNG
in der gewählten Berechnungsgröße gespeichert, je eine für links und rechts.
Beide verwenden dieselbe lineare Normierung: Weiß ist nah, Schwarz ist fern.
Es handelt sich um **relative Disparität, nicht um Entfernungen in Metern**.
Eine JSON-Begleitdatei dokumentiert gemeinsame Minimal-/Maximalwerte und Rückrechnung.
Eine Karte gehört zum jeweiligen linken/rechten Halbbild mit gleicher Ausrichtung
und Größe. Die Option ist anfangs ausgeschaltet. Eine reine Tiefenkartenausgabe und
Lentikular-Druckvorbereitung sind nicht Bestandteil dieser Version.

## Berechnung und Protokolle

Der GPU-Modus beschleunigt LAS2 über DirectML und benötigt eine kompatible
DirectX-12-Grafikkarte samt Treiber. NVIDIA, AMD und Intel werden unterstützt.
CPU ist beim ersten Start vorausgewählt; eine gespeicherte Gerätewahl bleibt erhalten.
Einzelne nicht unterstützte ONNX-Operationen können innerhalb der DirectML-Sitzung
auf CPU laufen. Ein fehlgeschlagener GPU-Start wird gemeldet. Modell, Gerät,
Präzision und Auflösung werden niemals automatisch heruntergesetzt oder gewechselt.

**RVS rendert auch im GPU-Modus auf CPU**, mit Precision 1, RGB und Multispectral 1/4.
Zwischenansichten werden innerhalb der CPU- und Speichergrenzen parallel berechnet.
Hohe Auflösungen benötigen entsprechend mehr Zeit und Speicher.

„Tiefenberechnung testen“ verarbeitet das gewählte Einzelbild mit derselben Vorbereitung
und beiden Tiefenberechnungen, ohne Renderer und ohne Bildausgabe. Zuerst Größe wählen.
Protokolle liegen unter `logs` im Programmordner. `latest_run.json` wird bei jedem Lauf
überschrieben. Es enthält Stufenzeiten, Renderparallelität sowie stichprobenartige
RAM-/Commit- und verfügbare DXGI-Prozesswerte für GPU-Speicher. Die GPU-Werte sind
Prozesswerte samt Budget, keine gesamte Grafikkartenbelegung. `wigglinde.jsonl` und
`errors.log` rotieren bei 5 MiB; je Typ bleiben drei ältere Dateien erhalten.
Temporäre Dateien unter `_temp` im Ausgabeziel werden nach der Verarbeitung entfernt;
ein leerer `_temp`-Ordner wird ebenfalls entfernt.

Extreme Parallaxen, Verdeckungen, Glas, Spiegelungen und feine Strukturen können
Übergangsstörungen oder Doppelkonturen verursachen. Fehlerfreie Ergebnisse für jedes
Motiv sind nicht garantiert.

Quellstand: `source`. Lizenzen: `licenses`. Eigener Code unter MIT; Fremdkomponenten
und Modellgewichte behalten ihre jeweiligen Lizenzen. Keine Telemetrie oder automatischen Downloads.
