# Entwicklungsstand und Qualitätsprüfung

Stand: 16. Oktober 2026. Es gibt noch keinen freigegebenen Konverter oder Installer.
Der vereinbarte Funktionsumfang steht in [PROJECT.md](PROJECT.md).

## Implementiert

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

- Der echte Modelllauf muss praktisch belegt werden; siehe Modellprüfung unten.
- Bildqualität auf realen Fotos, Speichernutzung und Laufzeiten bei Fotoauflösung.
- Windows-/CUDA-Betrieb, portable Paketierung und vollständige Fremdlizenzbeigaben.
- Automatische Ausrichtung, Behandlung von ICC-Profilen und Quellen mit mehr als
  8 Bit pro Farbkanal. Der Diagnosepfad arbeitet derzeit mit 8-Bit-RGB als sRGB.
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

GitHub Actions prüft denselben Kern auf Windows und Linux. Ein erfolgreicher
Windows-Kerncheck ist kein Nachweis für Windows-Modellinferenz oder portable Builds.

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
Graph und Schnittstelle wurden direkt gelesen. Der erste CPU-Test zeigt eine
ungewöhnlich lange ONNX-Sitzungsinitialisierung. Bis ein echter Inferenzlauf
vollständig abgeschlossen und ausgewertet ist, gilt der Adapter als unbestätigt.
Weder Modellqualität noch GPU-/Windows-Funktion werden aus den Kerntests abgeleitet.

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
