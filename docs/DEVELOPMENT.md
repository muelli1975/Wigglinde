# Entwicklungsstand und Qualitätsprüfung

## Rendererprüfung nach Test 3 (17. Oktober 2026)

Die Anwenderprotokolle mit RTX 3060 grenzen den Engpass ein: 1080p bei 1620×1080,
191,05 s gesamt, Modellladen 1,46 s, beide H-Tiefenkarten 1,61 s, 31 RVS-Ansichten
181,59 s (95 %), Kodierung/Kopieren 4,19 s. Die vollständige CPU-/GPU-Ausgabezeit
wird überwiegend vom CPU-Renderer bestimmt.
2160p bei 3239×2160 scheitert nach 10,23 s im linken DirectML-Aufruf, AveragePool_1,
mit 0x8007000E und wiederhergestellter Meldung zu fehlenden Speicherressourcen.
Abgetastete lokale DXGI-Prozessnutzung 26,16 GiB bei ca. 11 GiB Budget, kein Maß
für physisch vorhandenen VRAM. Verfügbare Commit-Reserve des aufrufenden Prozesses
zeitweise 64 MiB bei noch ca. 9,3 GiB verfügbarem physischem RAM. Speichermangel
bestätigt, ausschließlich physischer VRAM als Ursache damit nicht bewiesen.
Die `system_commit_*`-Feldnamen sind verkürzt: GlobalMemoryStatusEx liefert beim
Limit das kleinere System-/Prozesslimit und bei verfügbarer Zusicherung einen
prozessbezogenen Wert. Die Rohwerte werden hier entsprechend eingeordnet.

RVSVulkan-Quellcode und Apache-2.0-Lizenz tatsächlich abgerufen und geprüft.
Befund und konkrete Anschlussstellen: [RVSVULKAN_REVIEW.md](RVSVULKAN_REVIEW.md).
Noch keine Kompilierung oder GPU-/Qualitätsmessung, kein Rendererwechsel.

Auf Christophs Wunsch L/R-Tausch aus Oberfläche, Konverter-API und Übersetzungen
entfernt; Eingabe bleibt fest Full-SBS, links/rechts. Vorhandene Eingabeprüfung auf
feste Reihenfolge aktualisiert, GUI-Paketprüfung für den nächsten Build ergänzt.
27 lokale Prüfungen bestanden. Kein neuer Windows-Build; Test 3 bleibt das zuletzt
bereitgestellte Paket. Historische CLI-Vergleichswerkzeuge sind davon unabhängig.


## Test 3: H und Ressourcenmessung

LAS2-H fest, vier Iterationen, Float32; M/L und Modellmenü entfallen.
Full-SBS bleibt Voraussetzung. Ausgabesuffixe klein, Höhe mit `p` statt `h`.
5-MiB-Logrotation mit drei Backups je Typ, letzte Diagnose separat als
`logs/latest_run.json`. UTF-8-Fehler sichern ihre ursprünglichen Bytes samt als
Kandidat gekennzeichneter Windows-Codepage-Dekodierung. Kein behaupteter OOM-Fix.

Tiefentest für ein Einzelbild verwendet die Exportvorbereitung und beide Inferenzen,
startet RVS nicht und schreibt keine Bilder. Reguläre Exporte messen Vorbereitung,
Modellladen, links/rechts, RVS-Vorbereitung und Ausgabe. Der native RVS-Adapter
misst Eingabeladen, Rendering und Streamschreiben getrennt. Streamwartezeit und
Ansichtsmaterialisierung überlappen mit dem Renderprozess und dürfen nicht mit
der nativen Renderzeit addiert werden. Exportkodierung/Kopieren separat gemessen.

RAM/Commit und DXGI-Prozessspeicher/-budget werden alle 0,25 s und an Stufengrenzen
abgetastet. Peaks können kurze Spitzen verpassen. DXGI misst weder die gesamte
Adapterbelegung noch garantiert es die maximal mögliche Allokation. Fehlende
Zähler verhindern keine Bildberechnung. Keine neuen teuren Bildprüfungen.

### Rückmeldungen vom 17. Oktober

| Modell / FullHD | GPU | CPU |
| --- | --- | --- |
| H | 3:11 | 3:34 |
| M | 3:12, erneut 3:10 | 3:19 |

L zeigt auf GPU und CPU Fehler in Wolken und feinen Ästen; M besser als L,
H beste Qualität. H zeigt dennoch örtliche Störungen bei Übergängen. Ursache
zwischen Tiefenkarte und Rendering noch offen; GPU ist keine Qualitätskorrektur.
H 2160p GPU scheitert im linken ORT-Aufruf an UnicodeDecodeError mit Byte 0xfc.
1080p GPU funktioniert. 2160p CPU gelingt in 14:14 mit erstklassigem Ergebnis.
Grafikspeichermangel plausibel, ohne Ursprungsmeldung/Hardwaredaten nicht bewiesen.

27 lokale Prüfungen bestanden. Zusätzlich echter CPU-Tiefentest mit `bild032_cs.jpg`
bei 1620×1080 bestanden: 1,00 s Vorbereitung, 1,03 s Modellladen, 8,73/9,51 s
links/rechts, 20,29 s gesamt; abgetastete RSS-Spitze 6925 MiB. Nur Tiefenberechnung,
kein Vergleich der gesamten Exportzeit oder anderer Hardware. Lokale 3240×2160-
Probe im linken Aufruf durch den OOM-Killer beendet (Exit 137, cgroup `oom_kill=1`,
8-GiB-Grenze). Der letzte Bericht behält `status=running/current_stage=depth_left`;
ein vom Betriebssystem beendeter Prozess kann keinen Abschlussbericht schreiben.
Der erfolgreiche 2160p-CPU-Export beim Anwender bleibt davon unabhängig.
[Windows-Paketprüfung für Test 3](https://github.com/muelli1975/Wigglinde/actions/runs/39022540162)
bestanden, Quellstand `2a599766bb6a62ed0beb79b73482d1af9743d878`.
Tatsächliche EXE: H-CPU-Exporte MP4/GIF/PNG, Tiefentest ohne zusätzliche Ausgabe,
Sitzungswiederverwendung, Originalerhalt, alte Modell-/Layoutwerte entfernt,
beide Sprachen, gemalte Buttonfarben, stabile Bedienpositionen, 100/125/150 %,
unveränderte Icon-/Sounddateien. Native Windows-RAM-/Commit- und DXGI-Zähler
arbeiten; das bestätigt noch keine physische GPU-Inferenz. Microsoft Basic Render
Driver ist der einzige Adapter; dessen DirectML-Initialisierung scheitert wie zuvor.
Paket enthält ausschließlich H und keine Testlogs, Einstellungen oder temporären
Dateien. Archiv CRC-geprüft, 163853096 Bytes, SHA-256:
`aac87a01768827e393e4476e1170af2449a2578e71a8ddd9e3fb74e3cb1527c9`.
Die separate Prototype-Prüfung desselben Commits ist ebenfalls bestanden.


## Test 2a: Buttonfarben und Full-SBS

Der Startbutton übernimmt nun die vollständigen Normal-/Hover-/Deaktiviertfarben
aus SplatTricia `6217bb40629fd2c6f06a4662850e14610919b9b7`, einschließlich Fläche,
Text und Rahmen nach den internen CustomTkinter-Callbacks. Die vorherige reine
Textfarbenänderung konnte die Hoverfläche wieder dunkel zeichnen. Die Paketprüfung
kontrolliert deshalb die tatsächlich gezeichneten Farben nach Mausereignissen
auf Fläche und Beschriftung sowie beim Wechsel in den Verarbeitungszustand.
Sekundäre Buttons bleiben in der neutralen Palette; ihre Geometrie bleibt fest.

Die nicht abgesprochene Half-SBS-Erweiterung ist aus dem Konverter entfernt.
Wie die anderen Programme setzt er Full-SBS mit ungestauchten Einzelansichten
voraus. Kein Layoutmenü; alte gespeicherte Layoutwerte werden nicht angewendet.
Die Inputprüfung kontrolliert die unveränderten Full-SBS-Proportionen auch beim
L/R-Tausch. Modelle, Auflösungen und RVS-Einstellungen bleiben erhalten.
Windows-Paketprüfung von Test 2a bestanden (Run 39014737698); nicht separat bereitgestellt.

## Test 2: Rückmeldungen und Änderungen

Christoph bestätigt insgesamt gute Bildqualität und saubere RVS-Kanten; CPU ist zu langsam.
Weiterer konkreter Befund: Feine Aststrukturen erscheinen während der Animation
teilweise gedoppelt. Noch keine gesicherte Ursache; bidirektionale Disparität,
Verdeckung und beidseitiges Blending gezielt am betroffenen Foto vergleichen.
GPU-Beschleunigung allein ist keine Lösung dieses Qualitätsfehlers.
Reduzierte Eingabe mit Einzelbild-/Ordnerpfad statt Dateiliste, Deutsch/Englisch,
unveränderter SplatTricia-Sound. Geliefertes Wigglinde-Icon bytegetreu unter assets,
in der EXE und für das Programmfenster eingebunden; Originalhash im Pakettest geprüft.
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
bei anschließender DPI-Änderung. Wiederholte Wechsel von Format, Modell und
Berechnungsgerät einschließlich sehr langer Gerätebezeichnung verschieben lokal
keine Bedienelemente; derselbe Positionsvergleich ist Teil des Windows-Pakettests.
Die [Windows-Paketprüfung mit dem gelieferten Icon](https://github.com/muelli1975/Wigglinde/actions/runs/39012872811)
ist bestanden: tatsächliche EXE, CPU-Exporte MP4/GIF/PNG mit L sowie zusätzliche
Exporte mit M/H, Sitzungswiederverwendung, Originalerhalt, beide Sprachen,
Bedienpositionen und unveränderte Icon-/Sounddateien. Getesteter Quellstand:
`f2de006db1f1672a4bc3cbb25c3788fc94f54632`.
Der Server stellt nur den Microsoft Basic Render Driver bereit; die explizite
DirectML-Probe scheiterte an dessen Initialisierung. GPU-Inferenz und physische
GPU-Leistung sind damit noch nicht bestätigt und auf einem echten Desktop zu testen.
Das Archiv ist 302675387 Bytes groß; SHA-256:
`986f4f0eeec704cac718f6833ef518995f53bd2c0fad956ccf922a1d1c96a9a7`.
Der ORT-Build verwendet nach einem MSVC-2026-Warnungsfehler die VS-2022-Umgebung;
ein doppelter Wheel-Suffix wurde vor dem erfolgreichen Lauf entfernt.
Die Laufzeit ist mit deaktivierter Telemetrie kompiliert und für weitere Builds
zwischengespeichert. Reale Fotoqualität, 2160er Speichergrenzen und Desktop-GPU
bleiben getrennte Praxistests; das bekannte Ast-Doppelbild ist nicht als behoben belegt.

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
