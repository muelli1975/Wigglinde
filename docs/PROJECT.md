# Freigegebener DEFOM-Test 1.2 Test 2 — 23. Oktober 2026

**Abgeschlossen und verworfen:** Christoph sieht nach dem Fernbereichsvergleich
auch bei DEFOM-S/RVC keinen ausreichenden Vorteil. Stabilen 1.1-Stand unverändert
behalten; keine weiteren Modelltests oder Übernahme dieses Zweigs. Alternative
Renderer dürfen unabhängig auf Verfügbarkeit, Geschwindigkeit und mindestens
gleiche Qualität geprüft werden. Die folgenden Abschnitte sind Testhistorie.

Nach dem praktischen GREAT-/VWS-Vergleich beide aus dem nächsten separaten
Windows-Testpaket nehmen. LAS2-H als Standard, IGEV++ Middlebury und unveränderten
CPU-RVS behalten. Zuerst DEFOM-S/RVC und DEFOM-L/Middlebury intern mit denselben
Fotos vergleichen; nur bei nutzbaren Ergebnissen Export/Mischpräzision/DirectML
und einen getrennten Testbuild prüfen. Large mit sichtbarem `(CC-BY-NC-4.0)`
ausdrücklich autorisiert; Attributions- und Lizenztexte erhalten. Keine stabile
Veröffentlichung ersetzen. Weitere Entscheidungen nach persönlichem Bildvergleich,
Lentikular bleibt nachgeordnet.

# Freigegebenes Export-Update 1.1 — 23. Oktober 2026

Animationsausgabe als MP4, GIF, AVIF oder PNG-Bildfolge. AVIF bleibt bei Qualität 60,
4:2:0 und Geschwindigkeit 6, mit 720/1080/2160 Pixel Bildhöhe und 30/60 fps.
Standard 720p/30 fps in Wigglinde und 1080p/30 fps in SplatTricia.
Bestehende 1.1-Pakete aktualisieren; Modelle, Renderer, Geometrie und die übrigen
Ausgabeparameter erhalten. Vorhandene Einstellungen der übrigen Formate erhalten.
MP4-Zyklusanzahl als positive ganze Zahl, Standard 5; unveränderte Ansichten und
verlustfreie Wiederholung des einmal kodierten Zyklus. Größe und Bildrate pro
Format sowie MP4-Zyklusanzahl über Formatwechsel und Neustarts speichern.
Zyklusdauer bleibt gemeinsam für alle Formate (Standard 2 s). Kein APNG.

# Freigegebene Version 1.1 — 18. Oktober 2026

Christoph beauftragt die Fertigstellung nach den praktischen Vergleichen.
Nur LAS2-H (Standard, vier Iterationen) und IGEV++ Middlebury (16 Iterationen).
Kein ETH3D, S/M/L, Selective oder RT im Paket. CPU Float32, Windows-GPU-Mischpräzision,
bisheriger CPU-RVS und sämtliche Geometrie-/Exportstandards erhalten. Feste
Modellzusätze las2-h / igev-middlebury in allen Ergebnisnamen; Modell, Iterationen,
Präzision und Gerät zusätzlich in Tiefenkarten-JSON. Vier bisherige Plattformen
für 1.1 bauen; 1.0 als historischen Release erhalten. Middlebury-2160p auf RTX 3060
12 GB vom Anwender erfolgreich bestätigt. Keine weitere Foto-Testserie als Freigabeschritt.

Die folgenden Abschnitte dokumentieren frühere Vereinbarungen und Teststände.

# Aktueller Testauftrag 1.1 Test 4

Zusätzlich IGEV++ Middlebury in die Modellwahl integrieren und benötigte Komponenten
prüfen. LAS2-S/M/L/H bleiben, H bleibt Standard. IGEV++16 feste Iterationen;
CPU-Float32/GPU-Mischpräzision wie vereinbart. Bestehende CPU-RVS-/Export-/Geometrie-
regeln erhalten. Keine Installation von torch/timm/CUDA für Anwender. Separate
Windows-Testversion; main/v1.0 und frühere Testbranches bleiben erhalten.

# Wigglinde: vereinbarter Projektumfang


## Festgelegter Standard nach Bildvergleich

Christoph entscheidet am 17. Oktober 2026: Version 1.0 mit festem RVS-Simple-Blending, Faktor 5, neu bauen. Multispectral bringt bei den meisten seiner Bilder keinen Vorteil; Simple 5 liefert ruhigere Details. Keine Blending-Regler in 1.0. Die separate Testversion bleibt erhalten. Berechnungsauflösung weiter an Ausgabe gekoppelt; kein neues Modell, keine zusätzlichen Iterationen oder Filter. Alle bestehenden Plattformpakete erhalten denselben Standard.

Stand: 17. Oktober 2026. Diese Datei beschreibt das Ziel, nicht vorhandene Funktionen.

Wigglinde soll vorhandene stereoskopische SBS-Fotos in hochwertige Zwischenansichten
umwandeln und daraus Wiggle-Animationen und Vorlagen für Lentikularbilder erzeugen.
Ein portables Windows-Programm, nach Einrichtung lokal und offline; kostenlos
nutzbar, auch außerhalb von Forschung. Eigener Code unter MIT, Fremdkomponenten
unter ihren eigenen geprüften Bedingungen. Qualität ist wichtiger als Geschwindigkeit.

Wigglinde soll auf normalen PCs sinnvoll nutzbar sein. Speicher- und Laufzeitmessungen
gehören zur Auswahl des Kerns; keine automatische Qualitäts-/Auflösungsreduktion.
Stapelverarbeitung ohne zusätzliche teure Qualitätsprüfungen pro Datei oder Frame.
Modellsitzungen und bereits berechnete Ansichten wiederverwenden. Entwicklungs-
vergleiche und vollständige Probe-Dekodierungen gehören nicht in den normalen Ablauf.

## Oberfläche

Eine nüchterne, reduzierte Konverter-GUI, Bedienlogik ähnlich SplatTricia.
Eingabe, Ausgabe, wenige fachliche Optionen, Start, Abbrechen, Status und Fortschritt.
Farben und Steuerelemente nach dem unveränderten gemeinsamen Gestaltungsstandard.
Keine ungefragten Stereo-Regler, große Editoroberfläche oder zusätzliche Formate.
Einzelbild und Bildordner mit Pfadfeldern wie SplatTricia, ohne Dateiliste.
Deutsch/Englisch, unveränderter Fertigstellungssound und geliefertes Wigglinde-Icon.
Einzelbilder und Stapelverarbeitung sind vorgesehen. Eingabe und Ausgabe haben
getrennte Dialoggedächtnisse. Der SplatTricia-Standard für das Ausgabeziel ist
`<Eingabeordner>/output` bzw. ein bewusst gewählter eigener Ordner.

## Wiggle: verbindliche Referenz SplatTricia

| Ausgabe | Größenwahl | Bildrate | Ablauf |
| --- | --- | --- | --- |
| MP4 | maximale Höhe 720 / 1080 / 2160 px | 30 / 60 fps | fünf Pendelzyklen |
| GIF | maximale lange Seite 640 / 800 / 1024 px | 10 / 15 / 20 / 25 fps | Endlosschleife |
| PNG-Bildfolge | maximale Höhe 1080 / 2160 px | 30 / 60 fps | ein Pendelzyklus |

Zyklusdauer 0,5 bis 30 s, Standard 2 s. Ganze Bildanzahl, sinusförmige Bewegung,
identische Ansichten auf dem Rückweg, kein doppeltes Schlussbild. Seitenverhältnis
erhalten; kleine Quellen nicht hochskalieren. MP4: H.264 CRF 18/slow mit derselben
sRGB/Rec.709-Behandlung. GIF: gemeinsame Palette für den gesamten Zyklus.
Standards: MP4, 720 px Höhe, 30 fps; GIF 800 px, 15 fps; PNG 1080 px, 30 fps.

## Geometrie und Qualitätsziel

Gewählter Modellansatz: Lite Any Stereo V2. Nach praktischem Vergleich wird für
Test 5 ausschließlich LAS2-H verwendet, mit vier Iterationen und Float32.
Berechnungsgerät CPU/DirectML bleibt ausdrücklich wählbar, ohne automatische Umschaltung. Die erste Testversion
verwendet LAS2-M als ONNX und RVS auf der CPU. Der frühere native Forschungsversuch
und RVS-Vergleich stehen in `RVS_COMPARISON.md`. Der CLI-Adapter für
C-FoundationStereo-S bleibt ausschließlich als historischer Entwicklungsvergleich.
Nach positivem Sichtvergleich ist RVS die bevorzugte Richtung für die Rendererarbeit.
Die gemessene CPU-Laufzeit soll gezielt verbessert werden, bei gleicher Renderqualität.

Eingaben sind fertig justierte Full-SBS-Stereopaare mit ungestauchten Einzelansichten,
linke Ansicht links, rechte rechts. Kein L/R-Tausch im Konverter.
Keine Half-SBS-Option oder automatische Formaterkennung. Keine automatische oder manuelle Justage,
kein Beschnitt und keine Änderung der vorhandenen Scheinfensterlage. Ein temporärer
Suchversatz des Modells wird nach der Inferenz vollständig rückgängig gemacht.

Korrespondenzen in beiden Richtungen, Konsistenz und Verdeckungen berücksichtigen;
Zwischenansichten direkt aus einer gemeinsamen Darstellung erzeugen. Vorder- und
Hintergrund an Tiefensprüngen trennen. Hintergrundergänzungen sollen über die
gesamte Bewegung konsistent bleiben. Größere Lücken und montierte Paare mit
Scheinfenster-Verschiebungen brauchen eigene praktische Prüfung.
Keine stille Farbkorrektur oder generative Bildänderung.

Ziel sind Ergebnisse auf dem Niveau der SplatTricia-Wiggles. Das ist erst anhand
echter Fotos und zurückgehaltener gerenderter Zwischenansichten zu belegen.
SplatTricia kann zwei Außenansichten und zusätzliche Referenzansichten aus derselben
Szene liefern; Wigglinde darf für diesen Vergleich nur die Außenansichten sehen.

## Lentikular

Gleichmäßig verteilte Blickpositionen unabhängig vom Wiggle-Zeitverlauf. Zunächst
verlustfreie nummerierte Ansichten; später Streifenverschachtelung mit Druckgröße,
Ausgabeauflösung, gemessenem Pitch und druckbarem Pitch-Test. Die eigentliche
Druckvorbereitung wird erst nach bestandenem Ansichtsvergleich umgesetzt.

Ein professioneller Anwender kann später freiwillig testen. Zunächst benötigt er
verlustfreie Ansichtsserien für seinen bestehenden Druckworkflow. Fachliche
Referenzen für den späteren Interlacer: Triaxes 3DMasterKit, 3DZ und DP Lenticular.
Exakte Druckmaße, PPI getrennt von Drucker-DPI, gemessener Pitch mit Nachkommastellen,
Linsenrichtung, Betrachtungsabstand, Grob-/Fein-Pitchtest, Montage-/Schnittmarken,
Phasenlage, Reihenfolge/Spiegelung, TIFF/BigTIFF und ICC-/RIP-Übergabe sowie
reproduzierbare Material-/Druckprofile sind vor Implementierung zu spezifizieren.
Keine Behauptung professioneller Druckeignung ohne reale, kalibrierte Testdrucke.
Diese Funktionen gehören noch nicht zum Test-5-Paket.

## Nächster freigegebener Schritt: Diagnoseversion

Christoph hat am 17. Oktober die Umsetzung gestartet. Begrenzte Logrotation:
5 MiB, drei ältere Dateien je Typ. Laufzeitstufen und stichprobenartige RAM-/GPU-
Speicherwerte protokollieren; ursprüngliche Runtime-Fehlerbytes sichern. Einzelbild-
Tiefentest mit identischer Berechnung und gewählter Auflösung, ohne Renderer.
Kein automatischer CPU-/Auflösungswechsel. Zunächst messen, danach Optimierungen
entscheiden. CUDA, Cache, Tiling und Tiefenkartenexport werden hier nicht ergänzt.
H liefert die beste Qualität im Anwendervergleich; Übergangsstörungen bleiben offen.

## Freigegebene RVS-Beschleunigung (17. Oktober)

Unabhängige Zwischenansichten parallel auf CPU berechnen. Gleiche RVS-Mathematik:
Precision 2, RGB, Multispectral 1/4, bestehende Füllung. Parallelität nach CPU und
verfügbarem RAM/Commit begrenzen; kein zusätzlicher Regler, keine Qualitätsreduktion.
Lentikularoptionen bleiben vorerst zurückgestellt. Kein Wechsel zu Open3D, Vulkan
oder einem eigenen Renderer als Teil dieses Schrittes.

## Freigegebene Testversion 5 (17. Oktober)

Precision 1 fest als einzige Änderung an der Bildberechnung gegenüber Test 4.
H, vier Iterationen, Float32, Multispectral 1/4, bisherige Linearisierung und
Suchversatz bleiben für diese Version erhalten. Kein neues Menü und keine weiteren
Fotovergleiche vor diesem Paket. Die bisherige konservative Speicherplanung bleibt
unverändert; deren Schätzbasis Precision 2 ist kein aktiver Renderparameter.

## Freigegebene Version 1.0 (17. Oktober)

LAS2-H, vier Iterationen, Float32, Precision 1, RGB und Multispectral 1/4 bleiben.
Standard MP4 720p / CPU; höhere Größen und DirectML bleiben wählbar. Zusätzliche
sRGB-Linearisierung und Rückwandlung entfallen, ICC-Umrechnung nach sRGB bleibt.
Suchversatz bleibt unverändert. Speicherplanung an Precision 1 anpassen,
Systemreserve erhalten. Bisherige PNG-Kompression bleibt erhalten. Sprache, Gerät,
letzte Eingabepfade, Ausgabemodus/-ordner, Tiefenkartenoption und Wiggle-Einstellungen
wie bei SplatTricia speichern; kein automatischer Verarbeitungsstart.

Wiggles unter wiggle, optionale linke/rechte 16-Bit-PNG-Tiefenkarten unter depth_maps.
Gemeinsame lineare Min/Max-Normierung, Weiß nah / Schwarz fern, relative Disparität
statt Meter; JSON mit Skala und Rückrechnung. Speicheroption anfangs aus.
Christophs ausdrückliche Korrektur: nur Bilder direkt im gewählten Eingabeordner
verarbeiten. Keine Rekursion, keine Unterordnerpfade oder Präfixe im Dateinamen.
Dies ersetzt die zuvor vorgeschlagene Nachbildung von SplatTricias Pfadpräfixen.
Lentikular bleibt zurückgestellt. Frühere Abschnitte dokumentieren frühere Schritte.

## Aktualisierung 1.0: GPU Mixed Precision und Repository

Am 17. Oktober um 16:21 freigegeben: vorhandenen Release 1.0 direkt mit einer
GPU-Mixed-Precision-Fassung aktualisieren. CPU behält Float32; gleicher H-Checkpoint,
vier Iterationen, Ausgabegröße und Renderer. ONNX-Konvertierung mit FP32-Inseln,
keine Behauptung exakter CUDA-AMP-Gleichheit oder garantierter GPU-2160p-Fähigkeit.
Keine zusätzliche Benutzer-Testserie als Voraussetzung. Verfügbare Modell- und
Paketprüfungen durchführen, Einschränkung des Hosted-GPU-Tests offen benennen.
Repository an die bestehenden Programme angleichen: README.md auf Englisch,
README_DE.md auf Deutsch, Download/Bedienung/Anforderungen/Ausgabe/Quellcode und
langfristige Nutzung/Lizenz; Build- und Fremdkomponentenhinweise separat.
