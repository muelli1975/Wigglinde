# Wigglinde 0.1 – Testversion 5

Den vollständigen Ordner entpacken und `Wigglinde.exe` starten. Modell, Renderer,
Laufzeiten und Fertigstellungssound sind enthalten; keine Installation, Anmeldung
oder Internetverbindung erforderlich. Sprache oben rechts: Deutsch oder English.

1. Ein Einzelbild oder einen Bildordner mit fertig justierten Full-SBS-Bildern auswählen.
   Die andere Eingabe wird dabei geleert. Ordner werden mit Unterordnern verarbeitet.
2. Die linke Ansicht steht links, die rechte rechts. Beide Ansichten werden mit ihren
   vorhandenen Proportionen eingelesen.
3. Ausgabeziel, Format, Größe, Bildrate und Zyklusdauer wählen.
4. LAS2-H ist fest eingestellt: vier veröffentlichte Iterationen, Float32.
5. Unter „Berechnung“ CPU oder eine gefundene Grafikkarte wählen. Mit Start verarbeiten.

Die Oberfläche zeigt Pfadfelder statt einer Dateiliste. Die aktuelle Datei erscheint
während der Verarbeitung im Statusbereich. Sprache, Gerätewahl und Ausgabeordner
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
Dateien: `_temp` im jeweiligen Ausgabeordner. Ein leerer temporärer Ordner wird
nach der Verarbeitung entfernt.

## Modelle, GPU-Modus und Teststand

H bleibt nach dem praktischen Qualitätsvergleich fest eingestellt. Es gibt keine
Modellauswahl. Die Berechnung erfolgt mit den veröffentlichten vier Iterationen
und Float32. Große Bilder können besonders viel Speicher benötigen.

„Tiefenberechnung testen“ verarbeitet das gewählte Einzelbild mit derselben
Vorbereitung und denselben beiden Tiefenberechnungen wie ein Export. Der Renderer
wird dabei nicht gestartet, und es werden keine Bilddateien ausgegeben. Zuerst Format
und Größe wählen, dann CPU/GPU und den Testbutton. Die Ergebnisanzeige nennt die
Modellladezeit, Tiefenzeit und gemessene Speicherspitzen. Diese Spitzen sind
Stichproben im Abstand von 0,25 Sekunden, keine garantierten Maximalwerte.

`logs/latest_run.json` enthält den letzten Lauf einschließlich Berechnungsgröße,
Stufenzeiten, Anzahl paralleler Renderaufgaben, RAM-/Commit-Werten und verfügbaren DXGI-Prozesswerten für GPU-Speicher.
Die GPU-Werte beschreiben den Prozess und sein Budget, nicht die gesamte Belegung
der Grafikkarte. Vor dem nächsten Test die Datei bei Bedarf separat sichern.
Die fortlaufenden Protokolle `wigglinde.jsonl` und `errors.log` werden bei 5 MiB
rotiert; je Typ bleiben drei ältere Dateien erhalten. Vorhandene ältere übergroße
Logs werden beim nächsten Eintrag rotiert. Nicht lesbare Runtime-Meldungen werden
zusätzlich als ursprüngliche Bytes gesichert. Ein UTF-8-Fehler beweist für sich
allein noch keinen Grafikspeichermangel.

Ausgabenamen behalten ihre Angaben, nun klein geschrieben und mit `p` für die
Bildhöhe: beispielsweise `Original_wiggle_30fps_1080p.mp4`. GIF verwendet `px` für
die lange Seite, PNG-Folgen enden auf `_png`.

Der GPU-Modus beschleunigt die LAS2-Tiefenberechnung über DirectML. Er benötigt eine
DirectX-12-fähige Grafikkarte und passende Treiber; kompatible NVIDIA-, AMD- und
Intel-Grafik wird unterstützt. CPU bleibt beim ersten Start vorausgewählt. Einzelne
von DirectML nicht unterstützte ONNX-Operationen können innerhalb der Modellsitzung
auf CPU laufen. Ein fehlgeschlagener GPU-Start wird gemeldet; kein stiller Wechsel
des gesamten Auftrags auf CPU. Bei Problemen CPU ausdrücklich auswählen.

**RVS rendert auch im GPU-Modus weiterhin auf CPU**, in der gewählten
Ausgabeauflösung (Precision 1), mit Multispectral-Blending 1/4. Zwischenansichten werden parallel
berechnet, soweit CPU und verfügbarer Speicher es zulassen. Die Anzahl wird pro Bild
automatisch bestimmt; bei großen Bildern können weniger Ansichten gleichzeitig laufen.
Modell, Präzision,
Auflösung und Rendererqualität werden nicht automatisch verändert.

Geschwindigkeit und Bildqualität des GPU-Modus müssen auf echten Grafikkarten
praktisch verglichen werden. Ein Windows-Buildtest auf einem gehosteten Server
ersetzt das nicht. Noch keine freigegebene 1.0. Große Auflösungen benötigen mehr
Zeit und Speicher. Das gelieferte Wigglinde-Icon ist enthalten.

LAS2 hat einen festen Suchbereich von 192 Pixeln in der Berechnungsgröße.
Sehr große Parallaxen können fehlerhafte Tiefenkarten erzeugen. Die RVS-Endansichten
sind gerenderte Bilder, keine eingesetzten Originale. Glas, Spiegelungen und
Verdeckungen können weiterhin Fehler zeigen. H liefert im praktischen Vergleich die beste Qualität. An einzelnen Stellen bleiben
aber Störungen während der Übergänge und gedoppelte feine Äste offen. Die Diagnoseversion
verändert die Bildberechnung nicht und behauptet keine Behebung dieser Fehler.

Quellstand: `source`. Lizenzen: `licenses`. Keine automatischen Aktualisierungen
und keine Telemetrie.
