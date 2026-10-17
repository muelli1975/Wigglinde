# Entwicklungsstand und Qualitätsprüfung

## Test 2: Rückmeldungen und Änderungen

Christoph bestätigt insgesamt gute Bildqualität und saubere RVS-Kanten; CPU ist zu langsam.
Weiterer konkreter Befund: Feine Aststrukturen erscheinen während der Animation
teilweise gedoppelt. Noch keine gesicherte Ursache; bidirektionale Disparität,
Verdeckung und beidseitiges Blending gezielt am betroffenen Foto vergleichen.
GPU-Beschleunigung allein ist keine Lösung dieses Qualitätsfehlers.
Reduzierte Eingabe mit Einzelbild-/Ordnerpfad statt Dateiliste, Deutsch/Englisch,
unveränderter SplatTricia-Sound. Icon steht noch aus.
Modellwahl: LAS2-M/L/H, Standard L, letzte Wahl gespeichert; H mit vier veröffentlichten
Iterationen. Modelle, Auflösung und Geräte werden nicht automatisch reduziert.
LAS2 kann ausdrücklich auf
CPU oder einer per DXGI gefundenen Grafikkarte über DirectML laufen. Windows-Paket
nutzt privat gebautes ONNX Runtime DirectML 1.24.4 mit CPU-Provider und
`onnxruntime_USE_TELEMETRY=OFF` (schon beim Kompilieren); kein paralleles CPU-ORT-Paket.
Kein stiller Gesamtwechsel auf CPU bei fehlgeschlagenem GPU-Start. DirectML darf
wie dokumentiert einzelne nicht unterstützte Graphoperationen auf CPU ausführen.
RVS bleibt unverändert CPU, Precision 2, Multispectral 1/4; dessen OpenGL-Pfad
verwendet eine andere Bildzusammenführung und ist nicht gleichwertig freigegeben.
Protokoll ergänzt Modell, Tiefenzeit, Wartezeit auf Renderframes und ONNX-Provider.
Die Wartezeit ist kein isolierter Renderer-Benchmark, weil das Backend parallel rechnet.

21 schnelle Prüfungen lokal bestanden. Exportvergleiche M/L/H sind auf dem
Buildserver bestanden. Lokal: H maximal 0,000036 px, L maximal 0,001328 px
Abweichung vom nativen Modell; Float32-Implementierungen werden elementweise
mit rtol/atol 1e-4 verglichen und die tatsächlichen Pixelfehler protokolliert. GUI lokal in beiden Sprachen geprüft,
Sprachwechsel erhält Optionen/Pfade, Busy-Zustand und Eingabe-/Ausgabeabhängigkeiten.
Layout bei 100/125/150 % und kleinem Fenster bestanden. Texte werden beim Sprachwechsel
in bestehenden Widgets aktualisiert; das verhindert verwaiste CTk-Menücallbacks
bei anschließender DPI-Änderung.
Windows-Paketprüfung und DirectML-Lauf sind vor Bereitstellung zu prüfen.
Der erste Runtime-Build scheiterte an MSVC-2026-Warnung C4875 unter /WX im
unveränderten ORT-Code. Der Build verwendet nun die VS-2022-Umgebung. Physische
GPU-Leistung und Ergebnisqualität bleiben auf einem echten Desktop zu testen.

Die folgenden Angaben zu Test 1 dokumentieren den bisherigen Prüfstand.


Stand: 16. Oktober 2026. Erste portable Windows-Testversion **0.1 Test 1**;
keine freigegebene 1.0 und kein Installer.
Der vereinbarte Funktionsumfang steht in [PROJECT.md](PROJECT.md).

## Aktuelle Testversion

- Deutsche CustomTkinter-GUI nach dem gemeinsamen Standard; Datei-/Ordnerauswahl,
  relative Ausgabe-Unterordner, getrennte Dialogpfade, Fortschritt und Abbruch.
- LAS2-M als dynamisches ONNX, CPU explizit; dieselbe Sitzung für den ganzen Stapel.
  Entwicklerexport mit Autoren-Substitutionen, gepinnter Quelle und Checkpoint-Hash.
  Nativer Vergleich an zwei Größen: maximale ONNX-Abweichung unter 0,001 px.
- Full-/Half-SBS, L/R-Tausch, ICC-Konvertierung vor Trennung/Skalierung nach sRGB.
  Gewählte Ausgabegröße ist auch Berechnungsgröße; Lanczos, kein Beschnitt,
  keine Justage oder stille Verringerung. Kleinere Quellen werden nicht hochskaliert.
- Beidseitige signierte Disparitäten. Temporärer Suchversatz
  `min(128,max(1,round(64*Breite/960)))`, anschließend vollständig abgezogen.
  Fester LAS2-M-Suchbereich 192 px bleibt eine dokumentierte Grenze.
- Unveränderte RVS-CPU-Klassen, Precision 2, Multispectral 1/4 und RVS-Füllung.
  Float32-Bilder werden direkt aus dem Prozess gestreamt; keine großen Rohbildfolgen.
  Endansichten werden mit RVS gerendert wie im positiv beurteilten Vergleich.
- MP4 720/1080/2160, GIF 640/800/1024 lange Seite, PNG-Folgen 1080/2160;
  Bildraten und Zyklen nach PROJECT.md. Nur unterschiedliche Ansichten berechnen.
- Keine volle Export-Dekodierung oder Geometrieprüfung im normalen Ablauf.
  ORT-Telemetrie ist **vor Initialisierung** über `ORT_DISABLE_TELEMETRY=1` deaktiviert,
  zusätzlich API-Abschaltung; PyInstaller-Runtime-Hook setzt den Opt-out frühzeitig.
  Kein Modell-/Komponentendownload durch die Anwendung.
- Windows-Paket mit ONNX-Modell, nativem RVS-Backend, OpenCV, lokalem VC-Runtime,
  Python/Tk, FFmpeg, Lizenztexten, deutscher Anleitung und eigenem Quellstand.
  Build im Zweig `testversion-0.1`; bisher kein Wechsel des Default-Branches.

## Tatsächlich geprüft

18 schnelle Prüfungen für Geometrie, ICC/SBS-Eingabe, Pixelerhalt, Ordnerausschlüsse,
Windows-taugliches RVS-JSON, Exportzeiten/Abmessungen und Erhalt bestehender Ergebnisse.
Die erste komplette Windows-Paketprüfung bestand in
[diesem Build](https://github.com/muelli1975/Wigglinde/actions/runs/38935119491).
Sie startet die tatsächliche EXE, berechnet LAS2/RVS, exportiert MP4/GIF/PNG, prüft
Umlautpfade und Sitzungswiederverwendung und startet die mitgelieferte GUI.
Die volle MP4-Dekodierung gehört ausschließlich zu diesem Entwicklungstest.

Zusätzlich lokal: Gesamttest mit allen drei Formaten und GUI; Layout bei 100/125/150 %;
wirklicher Abbruch während ONNX-Inferenz nach rund 2,34 s einschließlich Modellladen,
vorherige fertige Datei unverändert. Straßenfoto aus Originaldatei auf bewusst
gewählte 1080×720 px pro Halbbild: MP4, 30 fps, 75 tatsächlich dekodierte Frames,
fünf 0,5-s-Zyklen; gesamte Pipeline einschließlich Modellladen rund 31,42 s.
Einzelmessung, keine allgemeine Geschwindigkeitszusage.

## Weiterhin offen

Windows 10/11 auf Christophs Desktop, weitere echte Fotostapel, größere Fotodurchläufe
bis 2160 und deren Speichergrenzen. Der Build-Test läuft auf Windows Server 2025.
GPU/OpenGL, umfangreiche Verdeckungstests und Lentikulardruck sind noch nicht Teil
dieses Testpakets. Keine automatische Modell-, Geräte- oder Präzisionsumschaltung.

Die Abschnitte darunter sind **historische Prototypversuche**, keine Beschreibung
der aktuellen GUI. Der RVS-Auswahlversuch steht in [RVS_COMPARISON.md](RVS_COMPARISON.md).

## Historischer Geometrie-Prototyp

- Vollständiger gemeinsamer Gestaltungsstandard als unveränderte Referenzkopie.
  Noch keine GUI; keine Änderungen an bestehenden Stereo-Tools.
- SplatTricias Wiggle-Optionen und Exportkern: MP4, GIF, PNG-Bildfolge mit derselben
  Größen-, Zeit-, Pendel- und Farbkonvertierungslogik.
- Full-/Half-SBS-Einlesen mit expliziter Layoutwahl und L/R-Tausch.
- Offline-Adapter für das gehashte dynamische C-FoundationStereo-S ONNX-Modell.
  Kein Download im Anwendungscode, keine Importabhängigkeit vom NVlabs-Forschungscode.
- Disparitäten in beiden Richtungen; Rückrichtung durch Tauschen UND Spiegeln.
  Einheitliche Vorzeichenkonvention `d = x_links - x_rechts`, auch für die rechte Karte.
- Diagnose-Renderer: beidseitige Subpixel-Projektion, Tiefenordnung, Konsistenzmasken,
  Zusammenführung im linearen sRGB-Raum; keine automatische Verkleinerung.
- PNG-Ansichten mit Alpha für nicht rekonstruierte Stellen, verlustfrei gespeicherte
  Ausgangsgeometrie und JSON-Bericht; Diagnoseprotokoll im Programmordner unter `logs`.

## Bewusst noch offen

- Das Modell läuft in kleinen Linux-/CPU- und Windows-/CPU-Versuchen; siehe unten.
  Das belegt noch keine Ergebnisse an Stereo-Fotos.
- Bildqualität auf realen Fotos, Speichernutzung und Laufzeiten bei Fotoauflösung.
- Desktop-Windows-Kompatibilität, CUDA-Betrieb, portable Paketierung und vollständige
  Fremdlizenzbeigaben. Der erste Windows-Modellversuch lief auf einem Testserver.
- Behandlung von ICC-Profilen. Eine Ausrichtung ist ausdrücklich nicht vorgesehen.
  Der Diagnosepfad
  interpretiert RGB derzeit als sRGB; Farbmanagement ist vor Fotovergleichen zu
  ergänzen. Quellen mit höherer Farbtiefe, CMYK oder Transparenz werden mit einer
  konkreten Prototyp-Grenze gemeldet und nicht still auf 8-Bit-RGB reduziert.
- Ein konsistentes mehrschichtiges Hintergrundmodell und saubere Füllung von Lücken.
  Der jetzige Renderer ist eine prüfbare geometrische Ausgangsbasis. Er benutzt
  geschätzte Disparitäten auch in inkonsistenten Bereichen mit reduziertem Gewicht;
  diese Gewichtung ist kein Ersatz für zuverlässige Verdeckungsrekonstruktion.
  Das Tiefenband von 0,5 px und das Gewicht 0,25 sind sichtbare Forschungsparameter,
  keine als optimal belegten Produktstandards.
- Lentikulardruck: derzeit nur gleichmäßig verteilte Ansichten, noch kein Interlacer
  oder Pitch-Test. Keine Behauptung druckfertiger Dateien.
- GUI, gespeicherte Bedienoptionen und Stapelverarbeitung.

## Schnelle Prüfungen

```sh
python -m pip install -e .
python -m unittest discover -s tests -v
python -m wigglinde --help
```

13 Prüfungen bestehen lokal unter Linux/Python 3.12: zurückgehaltene Ansichten
einer analytisch definierten Szene mit Vorder-/Hintergrund, Verdeckungen,
negative Disparitäten nach Konvergenzverschiebung, Originalansichten,
Konsistenzgrenzen, Padding und Pixelerhalt, SBS-Layout, transparente Lücken sowie
MP4/GIF/PNG-Ausgabe und Abbruch ohne Verlust eines vorherigen Ergebnisses.
MP4 wird tatsächlich kodiert und dekodiert: fünf Zyklen, korrekte Bildanzahl,
Padding ungerader Abmessungen. Keine Laufzeit-Modellprüfung in diesen schnellen Tests.

GitHub Actions hat denselben Kern auf Windows und Linux erfolgreich geprüft
([erster Lauf](https://github.com/muelli1975/Wigglinde/actions/runs/38898283423)).
Der Kerncheck ist kein Nachweis für portable Builds. Die Modellinferenz wurde
zusätzlich im separaten Windows-Versuch unten geprüft.

## Lokaler Modellversuch

Modellidentität, Lizenz und Eingabeformat: [models/README.md](../models/README.md).
Für eine explizit gewählte CPU-Laufzeit `python -m pip install -e .[cpu]`, für CUDA
stattdessen `python -m pip install -e .[cuda]`. Nicht beide Laufzeitpakete mischen.
Das sind Entwicklungsbefehle; Anwender sollen später nichts davon ausführen müssen.

```sh
python tools/check_model.py --model models/deployable_foundation_stereo_s_dynamic.onnx --provider cpu --report output/model-smoke.json
python -m wigglinde foto_sbs.jpg --model models/deployable_foundation_stereo_s_dynamic.onnx --provider cpu --output output/foto_diagnose
```

Bestehende Diagnoseordner werden durch diesen Prototyp nicht ersetzt. Eine gespeicherte
`scene.npz` kann ohne erneute Modellberechnung erneut gerendert werden:

```sh
python -m wigglinde output/foto_diagnose/scene.npz --scene --views 17 --output output/foto_17_ansichten
```

Der Modellversuch erzeugt eine bekannte Texturverschiebung von 8 px und misst
Disparitätsfehler und mittlere Ansicht. Es gibt keinen willkürlichen Qualitätsgrenzwert,
der Fotos sperrt. Dieser kleine Lauf beweist noch keine Fotoqualität.
Montierte Paare können einen expliziten `--matching-offset` benötigen, damit auch
negative Disparitäten im positiven Suchbereich liegen. Dieser Schritt fügt Padding
hinzu und wird rückgängig gemacht; er schätzt keine neue Scheinfensterlage und
beschneidet keine Quellpixel. Sein geeigneter Wert ist noch praktisch zu untersuchen.

### Tatsächlicher Modellteststand

Die offizielle ONNX-Datei wurde heruntergeladen und per SHA-256 bestätigt.
Graph und Schnittstelle wurden direkt gelesen. Ein erster ungepaddeter Versuch
mit 256 px Breite ergab eine leere Slice/Reshape-Operation. Die graphseitig
nachgewiesene Mindestbreite von 416 px wird nun durch Padding berücksichtigt.

Die Standardeinstellung zur Tensor-Speicherwiederverwendung führte bei diesem
großen Graphen zu sehr langer Initialisierung. Ohne Wiederverwendung und
Memory-Pattern laden und rechnen die tatsächlichen Modelle. Diese Änderung
betrifft Speicherplanung, nicht Modellpräzision oder Bildauflösung. Der höhere
Speicherbedarf muss noch an Fotoauflösungen gemessen werden.

Vollständiger Adapter-/Renderer-Versuch mit ONNX Runtime 1.31.0, Linux, Python 3.12,
explizit 4 CPU-Threads, 416 × 128 px pro Halbbild, bekannter Verschiebung von 8 px:

| Messung | Ergebnis |
| --- | --- |
| Modell laden | 40,6 s |
| Disparität links / rechts | 24,1 / 42,0 s |
| Median absoluter Disparitätsfehler links / rechts, Innenbereich | 0,00451 / 0,00382 px |
| Konsistenzanteil links / rechts, ganzes Bild | 97,87 / 98,08 % |
| Mittlere Ansicht: MAE im geprüften Innenbereich | 0,0 auf 8-Bit-RGB |
| Mittlere Ansicht: Abdeckung im geprüften Innenbereich | 100 % |

Dies ist nur eine künstliche, texturierte Ebene und kein Beleg für Verdeckungen
in echten Fotos. Laufzeiten sind einzelne Entwicklungs-Messungen, keine
Geschwindigkeitszusage; der Prototyp hat keine voreingestellte Threadbegrenzung.
Ein separater Modelllauf bei 736 × 320 px ergab im Innenbereich einen Median
von 8,01448 px bei vorgegebenen 8 px. Die CUDA-Modellinferenz bleibt offen.

Der [separate Windows-Modellversuch](https://github.com/muelli1975/Wigglinde/actions/runs/38899424940)
war ebenfalls erfolgreich: Windows Server 2025, Python 3.12.10, ONNX Runtime 1.31.0,
4 explizit gewählte CPU-Threads, dasselbe gehashte Modell und dieselbe 416 × 128 px
große künstliche Szene. Modell laden: 12,2 s; linke/rechte Disparität: 14,75 / 14,5 s.
Median absoluter Disparitätsfehler: 0,00451 / 0,00382 px; mittlere Ansicht im
Innenbereich: MAE 0,0, Abdeckung 100 %. Modell und Laufzeit wurden nur für diesen
ausdrücklich ausgelösten Entwicklungsversuch heruntergeladen. Der Anwendungscode
enthält weiterhin keine Downloads. Der große Modelllauf startet automatisch nur
bei Änderung seiner eigenen Workflowdatei; ansonsten ist er manuell auslösbar.

Die verschiedenen Rechner erlauben keinen direkten Geschwindigkeitsvergleich.
Windows 10/11 als Desktop-Ziel, GPU/CUDA, Fotoauflösung und portable Paketierung
sind damit noch nicht freigegeben. Nächste fachliche Etappe ist der Vergleich an
echten SBS-Fotos, bevor Hintergrundergänzung und Konverter-GUI finalisiert werden.

## Vergleich mit SplatTricia

1. Aus derselben PLY-Szene äußere Ansichten und zusätzliche Zwischenansichten direkt
   mit SplatTricias Renderer erzeugen. Nur die äußeren Bilder gehen an Wigglinde.
2. Berechnete Zwischenansichten mit den zurückgehaltenen Referenzen vergleichen;
   Konturen, sichtbare Lücken und Unterschiede zusätzlich zum Zahlenwert ansehen.
3. Dieselbe Pendelweite, Größe und Geschwindigkeit verwenden. Bei echten Stereo-
   Fotos besonders Haare, Äste, Gitter, Glas, Spiegelungen und große Tiefensprünge prüfen.
4. Erst nach diesem Vergleich die endgültige Verarbeitung und die GUI festlegen.

## Referenzstand übernommener eigener Komponenten

SplatTricia `6217bb40629fd2c6f06a4662850e14610919b9b7`:
`export_options.py`, `wiggle_export.py`, `theme.py`; im Export lediglich den Import
der Dateiersetzung auf den lokalen Helfer angepasst. Lizenz des Ursprungsprojekts
ist MIT, derselbe Rechteinhaber wie dieses Repository.
Der gemeinsame Standard ist bytegleich mit Git-Blob
`2a301acd4ebf4cfc79a82818b50e85e08a650db9` (Version 1.5).
