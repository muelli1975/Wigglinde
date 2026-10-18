# 1.1 Test 3: LAS2-Modellvergleich

## Paketprüfung abgeschlossen

Build: https://github.com/muelli1975/Wigglinde/actions/runs/39120123438
Paketquellstand: `fd9a801b7968161e0db312ee3cf60cb4a79e1c44`.
40 Quelltests auf Linux/Windows bestanden. S/M/L native/ONNX-Vergleiche und
Mischgraph-Prüfungen abgeschlossen; S-Toleranzüberschreitung ausdrücklich
protokolliert, keine Zusage allgemeiner Foto-Parität. H-Graphen unverändert
wiederverwendet. CPU-RVS entspricht dem stabilen Quellpfad; serieller/paralleler
Vergleich bitgleich. Die tatsächlich gepackte Windows-EXE führt alle vier
Modelle aus; MP4/GIF/PNG, Tiefenkarten, Sitzungswiederverwendung, Deutsch/Englisch,
Modellwahl-Speicherung, alte Renderer-/Iterations-Einstellungen, Busy-Farben und
Geometrie bei 100/125/150 Prozent geprüft. Windows-Screenshot visuell kontrolliert.
Hosted DirectML konnte nicht initialisiert werden; keine physische GPU-Prüfung.

`Wigglinde_1.1_Test3_Windows_x64.zip`: 427226713 Byte, SHA-256
`427e48270bbcbcd190c055025ba4b7e1bdb78fd3b47ed699155fdd05551d882d`.
Heruntergeladenes Archiv CRC-/hashgeprüft, acht Modelle samt Hashes/Metadaten,
Quellidentität (plattformbedingte Zeilenenden berücksichtigt) und Bereinigung
bestätigt. Keine Logs, Einstellungen, GL-EXE/-Lizenzen oder iter8-Modelle.
Dieser Prüfvermerk entstand nach dem Build und gehört nicht zum Quell-Snapshot
im ZIP. IGEV++-Untersuchung: [IGEV_REVIEW.md](IGEV_REVIEW.md).

18. Oktober 2026, auf ausdrücklichen Wunsch von Christoph: OpenGL und die
Iterationsauswahl aus dem Testbuild entfernen und auf den unveränderten
RVS-CPU-Pfad der stabilen 1.0 zurückgehen. Simple 5, Precision 1, Bildgeometrie,
Größen, Export und Suchversatz bleiben erhalten. LAS2-S/M/L/H sind ausdrücklich
wählbar, Standard H. H bleibt bei vier Iterationen und seiner bisherigen
CPU-Float32-/DirectML-Mischpräzision. Auf ausdrücklichen Wunsch verwenden auch
S/M/L dieselbe CPU-Float32-/DirectML-Mischpräzisionsrichtlinie. S überschreitet die
kleine numerische H-Vergleichstoleranz (bis 1,3421 px); das wird als Messbefund
protokolliert, nicht als genereller Beweis sichtbarer Qualitätsverluste gewertet.
M/L bestehen den kleinen Vergleich; auch das belegt keine allgemeine Fotoparität.
Kein stilles
Modell-, Geräte- oder Auflösungs-Fallback. Keine automatische Modellinstallation.

Separate Branch `test-models-1.1`, keine Änderung an main oder Release 1.0.
Modellwahl wird gespeichert und pro Auftrag eingefroren. Alte Einstellungen für
Renderer/Iterationen werden entfernt. Keine OpenGL-Bibliotheken, GL-Backend-EXE
oder Acht-Iterationen-Graphen im neuen Paket. Stabile H-Graphen aus geprüftem
Run 39041230523 werden bytegleich wiederverwendet; S/M/L aus denselben gepinnten
LAS2-Quellen und Gewichtsrevisionen nativ/ONNX verglichen. Die Modellnamen
sind Vergleichsoptionen, keine Zusage einer Qualitätsrangfolge.

Praxisrückmeldung Test 2: OpenGL etwa doppelt so schnell, aber erheblich schlechtere
Kanten mit hellen Säumen. Acht Iterationen bringen am Problemfoto keinen sichtbaren
Vorteil; CPU/vier ist die Qualitätsreferenz. Beschleunigung rechtfertigt hier
keinen Qualitätsverlust. `bild054_cs.jpg` zeigt bereits in der H-Tiefenkarte
fehlende Trennung vieler Gitteröffnungen vom Vordergrund. Das ist ein Befund am
vorliegenden Foto, kein allgemeiner Modellvergleich. IGEV++ wird separat auf
Lizenz, CPU/ONNX/DirectML und das Foto geprüft und noch nicht mitgeliefert.

Die frühere Test-2-Implementierung ist nur historische Dokumentation:

# 1.1 Test 2: OpenGL und vier/acht Iterationen

Auftrag vom 18. Oktober 2026, separate Branch test-opengl-iterations-1.1 auf
Basis main b0985bc. Zwei unabhängige Auswahlen CPU/OpenGL und 4/8 Iterationen.
Gleicher H-Checkpoint und gleiche signierte Geometrie; Precision 1, Simple 5,
RGB und Exportgrößen unverändert. Kein automatischer Rendererwechsel.
OpenGL läuft in einem getrennten Backend-Prozess mit verborgenem GLFW-Kontext,
seriellen GPU-Ansichten und bisheriger CPU-Füllung. Treiberadapter/GL-Version
werden protokolliert; die DirectML-Gerätewahl betrifft nur die Tiefenberechnung.
Quell-Anpassungen sind unter THIRD_PARTY.md und im reproduzierbaren Skript benannt.
Acht Iterationen werden in eigene dynamische ONNX-Graphen exportiert, jeweils
Float32 und die bisherige Float16/Float32-Richtlinie. Modellmetadaten/Hashes
und die gewählte Iterationszahl werden vor Sitzungsstart geprüft.

Lokaler nativer Acht-Iterationen-/ONNX-Vergleich bei 416x128 und 448x160:
maximal 0,00003565 / 0,00003219 Pixel Unterschied. 40 schnelle Tests bestanden.
Dies belegt keine Verbesserung des Problemgitters und keine physische GPU.
OpenGL lokal mit Mesa llvmpipe ausgeführt: zwei analytische Szenen, positive und
negative Disparität, fünf Blickpositionen, gerade/ungerade Bildgrößen. Farben und
Verschiebungsrichtung stimmen im geprüften Innenbereich auf 8 Bit exakt, wiederholte
Frames identisch, Abbruch beendet den Backend-Prozess. Dies ist Software-OpenGL,
kein Beleg für Hardwareleistung. Die GL-Eingabesicht normalisiert Tiefen anhand
des tatsächlichen Kartenmaximums für den GPU-Tiefenpuffer; die Weltkoordinaten
werden durch die gepaarte Upstream-Umrechnung unverändert wiederhergestellt.
## Abgeschlossene Paketprüfung

Build: https://github.com/muelli1975/Wigglinde/actions/runs/39116665350
Quellstand im Paket: 166d0a5cdf2dc2457329a56577e97b43c0a0b593.
Linux: 40 Quellcodeprüfungen, seriell/paralleler CPU-Vergleich bitgleich,
OpenGL-Farben/Geometrie für positive und negative Disparitäten, Wiederholung
und Abbruch bestanden. Mesa llvmpipe, keine physische GPU.
Windows: beide nativen Backends gebaut, Quellprüfungen und seriell/paralleler
CPU-Vergleich bestanden. Tatsächlich gepackte EXE mit MP4/GIF/PNG (vier
Iterationen) und zusätzlicher PNG-Ausgabe mit acht Iterationen ausgeführt.
Alle vier Modelldateien samt Metadaten/Hash geprüft. GUI Deutsch/Englisch,
Busy-Zustand, Buttonfarben, Geometrie und Speicherung/Neustart geprüft;
Windows-Screenshot visuell kontrolliert. OpenGL und DirectML auf dem Hosted-
Windows-Treiber ausdrücklich nicht verfügbar; kein physischer GPU-Test.
Lokal außerdem vollständige Exporte aller vier Kombinationen CPU/OpenGL ×
4/8 ausgeführt; GUI bei 100/125/150 Prozent geprüft.

Wigglinde_1.1_Test2_Windows_x64.zip: 250103169 Byte, SHA-256
544397a18a780f2c4afd403ca6bb1033323a0ac793c732f699a85011eda9fd64.
Heruntergeladenes Archiv CRC- und hashgeprüft; Quellstand und Modelle
abgeglichen. Keine Logs, Settings oder Temp-Dateien im Paket.
Dieser Prüfvermerk liegt nach dem Build und ist daher nicht Teil des
Quell-Snapshots im Archiv. Fotoqualität/Gitter und reale GPU-Leistung offen.

# Entwicklungsstand und Qualitätsprüfung


## 1.0 neu mit Simple 5

Auftrag vom 17. Oktober 2026: auf dem freigegebenen main-Stand 19d1970 aufbauen. Nur festen Blender von Multi 1/4 auf native BlendedViewSimple(5.f) und passende RVS-Konfiguration/Diagnostik ändern. App-Oberfläche, Version 1.0, H vier Iterationen, CPU Float32/Windows DirectML Mixed Precision, Precision 1, RGB, Suchversatz, Auflösung, Export, Dateinamen und Einstellungen bleiben erhalten. Experimentelle Blending-Regler werden nicht übernommen. Modelle und private DirectML-Laufzeit aus geprüftem Run 39041230523 erneut verwenden. Build und Pakettests für Windows, Linux, Apple Silicon und Intel-Mac vor gemeinsamer Aktualisierung der Releaseassets und des Tags; Erfolgreicher Build und gemeinsame Veröffentlichung:
https://github.com/muelli1975/Wigglinde/actions/runs/39057394985
Quellcodeprüfungen unter Windows/Linux:
https://github.com/muelli1975/Wigglinde/actions/runs/39057394938

Alle vier Pakete enthalten Quellstand db215d8460eb798b4f4b4e914cab0ef6e3a2194f;
Tag v1.0 und Release-Ziel wurden nach erfolgreichen Paketprüfungen auf diesen
Quellstand gesetzt. Die experimentelle Branch test-blending-1.1 bleibt separat.
Je Plattform 38 Quellcodeprüfungen, nativer serieller/paralleler RVS-Vergleich
bitgleich, Abbruch-/Fehlerbehandlung und tatsächliche Paket-Ausgabe mit CPU
bestanden. MP4/GIF/PNG, optionale gemeinsame 16-Bit-Disparitätskarten samt JSON,
Deutsch/Englisch, Farben, stabile Bediengeometrie, Originalicon/-sound,
Einstellungswiederherstellung und Temp-Bereinigung geprüft. Native Unix-Pakete
nach Entpacken getestet; Mac-Ad-hoc-Signaturen geprüft. Keine neue Fototestserie.
Windows-Modelle und DirectML-Laufzeit aus geprüftem Run wiederverwendet; keine
neue physische GPU-Ausführung auf gehosteten Runnern belegt.

| Archiv | Byte | SHA-256 |
| --- | ---: | --- |
| Wigglinde_1.0_Windows_x64.zip | 185408673 | 13cd863e25fa1890641a602490b0b6d05460ed730976a0f68e4790c40d3ab446 |
| Wigglinde_1.0_Linux_x64.tar.gz | 150296373 | 810e1eade79f50e2596445fc7b91806cd771b8c2bae6e26e565ac14bea704e98 |
| Wigglinde_1.0_macOS_AppleSilicon.zip | 114215202 | ba1d0874422e1ddb5db620bd2816e64af99028197526d872a9a9aa04dcdfdac5 |
| Wigglinde_1.0_macOS_Intel.zip | 124813847 | 9d3376767e46bf44ff1f8f5276ffb63929090ce000af0580dfdfe6461b6dbdaf |

Alle vier veröffentlichten Asset-Digests und Größen mit den erfolgreichen
Build-Berichten abgeglichen; exakt vier endgültige Pakete, keine Staging-Assets.
Depth-Map-JSON bleibt nach Rückfrage ausdrücklich erhalten: Zuordnung,
gemeinsame Normierung und Rekonstruktion der Disparität in Verarbeitungspixeln.
Christoph meldet: Problemgitter in 2160p nur minimal besser; Simple 5 bei vielen
Bildern ruhiger als Multispectral. Keine allgemeine Behebung von Gitterfehlern
behauptet, höhere Berechnungsauflösung/weitere Modelle vorerst nicht übernommen.

## Einheitlicher Windows-Archivname

Am 17. Oktober 2026 wird das bestehende Windows-Release-Asset in
`Wigglinde_1.0_Windows_x64.zip` umbenannt. Inhalt, Build-Quellstand und Prüfsumme
bleiben identisch; es erfolgt kein erneuter Build. Die früheren Build-Vermerke
unten behalten ihre damaligen Archiv-/Artifact-Namen. Aktuelle Anleitungen und
zukünftige Windows-Builds verwenden den Namen mit x64.

## Native Pakete 1.0: Linux und macOS

Am 17. Oktober 2026 gebaut, geprüft und zur vorhandenen Veröffentlichung v1.0
ergänzt: Linux x64 (Buildhost Ubuntu 22.04), macOS 15 Apple Silicon und macOS 15
Intel. H mit vier Iterationen und unverändertem Float32-Modell; RVS Precision 1,
RGB und Multispectral 1/4. Kein weiterer GPU-Provider oder Rendererwechsel.

Quellstand aller drei Pakete: a27d7e527c54e4816faa54a0c06b694705fb0bb3.
Erfolgreicher Build einschließlich Veröffentlichung:
https://github.com/muelli1975/Wigglinde/actions/runs/39043747070
Quellcodeprüfungen unter Windows/Linux:
https://github.com/muelli1975/Wigglinde/actions/runs/39043747106

Je Zielsystem 38 Quellcodeprüfungen bestanden. Nativer serieller/paralleler
RVS-Vergleich bitgleich einschließlich Abbruch und Fehlerbehandlung. Die jeweils
entpackte Anwendung mit enthaltenem H-Modell und FFmpeg erzeugt MP4, GIF und
PNG-Bildfolgen sowie optionale gemeinsame 16-Bit-Tiefenkarten. Zusätzlich geprüft:
Deutsch/Englisch, stabile Bediengeometrie, Buttonfarben, Einstellungswiederherstellung,
Modellsitzungswiederverwendung, Temp-Bereinigung, unveränderte Eingabe und Original-
Icon/-Sound. Unter macOS ist die Ad-hoc-Signatur vor und nach dem Pakettest gültig;
portable Einstellungen und Modelle liegen außerhalb des signierten App-Bundles.
Keine Apple-Notarisierung. Linux-Sound nutzt vorhandenes paplay/aplay.

CPU ONNX Runtime 1.24.4 auf Linux/Apple Silicon; für 1.24.4 gibt es keine
offiziellen Intel-Mac-Wheels, daher dort 1.23.2. Gleiche ONNX-Datei mit SHA-256
ba2260dcc0aaff33a9fc1c41f729f727eb58eb034dfaec022713b3848ff5af76.
OpenCV 4.10 statisch; RVS und dessen OpenMP-Laufzeit nativ paketiert. Unbenutzte
OpenCV-Protobuf-/ADE-/Flatbuffers-Komponenten werden im Build abgeschaltet.
macOS-RAM-Messung über psutil; Original-ICO für das Mac-Bundle in ICNS umgewandelt.

| Archiv | Byte | SHA-256 |
| --- | ---: | --- |
| Wigglinde_1.0_Linux_x64.tar.gz | 150344875 | 84da918be4efdb67bd7abe42869d6bd116d1730ad1876220f6c7306bccae30b9 |
| Wigglinde_1.0_macOS_AppleSilicon.zip | 114242530 | e000d95cf1ef6298868b09669dad158b70a7976e2eeea40761f9fe688360cc96 |
| Wigglinde_1.0_macOS_Intel.zip | 124853788 | dd57e47626cdc26a368ba9c86edc09256bde37a4a667e904e0498fdbc8c39570 |

Die veröffentlichten Asset-Digests stimmen mit den lokal geprüften Archiven
überein. Das Windows-Archiv und der bestehende Tag v1.0 bleiben unverändert.
Die nativen Pakete enthalten jeweils ihren exakten Quellstand und Lizenzhinweise.
Diese Build-Prüfungen belegen keine allgemeine Fotoqualität, Laufzeit oder maximale
Auflösung auf beliebiger Benutzerhardware; keine zusätzliche Fototestserie.


## Kandidat RVS-CUDA: nur geprüft, nicht übernommen

Christoph verweist am 17. Oktober auf https://github.com/EnzoN7/RVS-CUDA.
README und CUDA-Code geprüft: GPU-Kernels für Projektion, Dreiecksrasterisierung,
Blending und Lückenfüllung sind vorhanden. Die veröffentlichte Pipeline verarbeitet
YUV420 und equirektangulare Eingaben; ihr Blender bietet nur Simple. Das passt noch
nicht zu Wigglindes perspektivischen RGB-Stereopaaren mit Multispectral 1/4.
Die README nennt 274-fache Beschleunigung auf ClassroomVideo gegenüber RVS 4.0,
die Repository-Kurzbeschreibung 100-fache; CUDA-Zeit-/Qualitätstabellen enthalten
noch Platzhalter. Keine entsprechende Beschleunigungs- oder Qualitätszusage für
Wigglinde. Sinnvoller späterer Schritt: Aufwand für perspektivische Eingaben, RGB
und Multispectral prüfen; gegebenenfalls Vergleich mit vorhandenen Tiefenkarten.
Kein Rendererwechsel oder neuer CUDA-Build im Rahmen der nativen 1.0-Pakete.

## Praxisrückmeldung 1.0 und Repository-Screenshot

Am 17. Oktober 2026 bestätigt Christoph: 2160p funktioniert mit der aktuellen
Mixed-Precision-Fassung auf seiner GPU. Dies ergänzt die unten dokumentierten
Build-Prüfungen um eine erfolgreiche Anwendung auf physischer Hardware.
Grafikkartenmodell, VRAM-Spitze und Laufzeit wurden für diesen Durchlauf nicht
genannt; daraus folgt keine allgemeine Speicherzusage für jede Grafikkarte.

Der von Christoph gelieferte Screenshot liegt unverändert unter
`docs/screenshots/Wigglinde.png` und ist in beiden READMEs eingebunden.
Linux-/macOS-Pakete sind möglich, bisher aber nicht gebaut oder geprüft;
Voraussetzungen und noch offene Plattformanpassungen stehen in `BUILD.md`.
Die bestehende Windows-Veröffentlichung bleibt davon unberührt.

## Aktualisierung 1.0: GPU Mixed Precision

Freigegeben am 17. Oktober 2026, 16:21: GPU verwendet separaten ONNX-Graphen mit
Float16/Float32, CPU weiterhin unveränderten Float32-Graphen. Gleiche H-Gewichte,
vier Iterationen, Bildgröße und RVS. Ein-/Ausgabe Float32. Konvertierung über
onnxruntime.transformers.float16 (1.24.4), Standard-Blockliste ergänzt um
BatchNormalization, InstanceNormalization, Softmax, ReduceSum, GridSample und Resize.
Dies ist eine dokumentierte ONNX-Mischpräzisionsrichtlinie; keine Zusage identischer
Operationstypen gegenüber dem CUDA-Autocast des Autoren-Geschwindigkeitstests.

Der ORT-Konverter bewahrt FP32-Initialisierer, wenn diese nur FP32-Knoten versorgen.
Das ist insbesondere für model.cost_agg.conv5.1.running_var nötig (bis 187539,8),
außerhalb Float16. Kein Abschneiden auf 10000 oder 65504. Der unveränderte ORT-Konverter erstellt die Mischpräzisionsgrenzen; ORT sortiert
topologisch, ONNX prüft Typen/Graph vollständig.
Zwei kleine Konvertierungsvergleiche mit CPU-Provider sind Build-Prüfungen,
kein Nachweis physischer GPU-Ausführung oder wahrnehmbarer Gleichheit.

Modellwahl ausdrücklich durch Gerät; falsche Modellpräzision wird zurückgewiesen.
Protokolle nennen mixed_float16_float32 bzw. float32. Keine stille Ersatzberechnung.
Repository-Struktur und EN/DE-README folgen den bestehenden Programmen; Hinweise
zu Quellcode, langfristiger Nutzung und Fremdlizenzen ergänzt.

Prüfung bestanden: 36 lokale Tests (0,22 s), 36 Windows-Tests (0,53 s),
serieller/paralleler RVS-Vergleich bitgleich. Tatsächliche EXE mit MP4/GIF/PNG,
Tiefenkarten, Einstellungswiederherstellung, DE/EN, stabiler Geometrie, Originalassets
und Prüfung der enthaltenen Mixed-Modelldatei. Hosted-DirectML nicht initialisierbar;
keine Bestätigung einer physischen GPU oder von 2160p-Grafikspeicherbedarf.
Konvertierter Graph: 299 Float16- und 20 Float32-Initialisierer, keine Warnungen,
23820828 Byte, SHA-256 e30ad144e626a61ef316d3943e4f0adc38313e9180e439194dc8dcea2177978d.
Kleine CPU-Konvertierungsprüfungen 416x128 / 448x160: maximale Differenzen
0,010935 / 0,013891 Pixel, Mittel 0,002036 / 0,002614, p99 0,006813 / 0,008528.
Dies sind Konvertierungsprüfungen, keine allgemeine Fotoqualitätsgarantie.

Gebauter Quellstand 642773fd642d28e30959a4df554829e4d56493da.
Windows-Workflow https://github.com/muelli1975/Wigglinde/actions/runs/39041230523
Source checks https://github.com/muelli1975/Wigglinde/actions/runs/39041230562
Artifact 12103952117. Wigglinde_1.0_Windows.zip: 185371902 Byte,
SHA-256 f8275d65b5a1691f03e2f0c520afc4276e82180ebdc942dddc6349fc4934c5ea.
ZIP CRC-geprüft; beide H-Fassungen mit passenden Hashes, keine Logs/settings/_temp,
Originalicon/-sound bytegleich. Relative Links der enthaltenen EN/DE-README und
Build-Anleitung geprüft. Der Quellstand im Paket ist der exakt gebaute Stand;
dieser spätere Prüfvermerk gehört nicht dazu. Die folgenden Abschnitte betreffen ältere Stände.


## Version 1.0: Umsetzung und Paketprüfung

Freigegeben am 17. Oktober 2026: MP4-Standard 720p / CPU; H, vier Iterationen,
Float32, Precision 1, RGB, Multispectral 1/4. Wegfall der zusätzlichen Gamma-
Linearisierung vor RVS und ihrer Rückwandlung danach; normalisiertes codiertes
sRGB entsprechend dem ursprünglichen RGB-Lader. ICC nach sRGB bleibt erhalten.

Suchversatz unverändert: min(128, max(1, round(64 * Breite / 960))). Dies ist
Wigglindes Heuristik für signierte Disparitäten, keine LAS2-Autorenempfehlung.
Temporärer Versatz wird nach der Inferenz abgezogen. Keine Änderung der Geometrie.
Die Speicherplanung wird auf Precision 1 angepasst: Pixelterm von 1024 auf 256 Byte
pro Ausgabepixel, da Precision 1 gegenüber 2 ein Viertel der Arbeitspixel benötigt.
Feste 64 MiB je Aufgabe und Reserve max(1 GiB, 10 % des physischen RAMs) bleiben.
Die drei vorhandenen 1620x1080-Vergleiche erreichten mit drei P1-Aufgaben 0,83–0,85 GiB
nativen RSS; die neue Schätzung reserviert dafür 1,44 GiB. Dies ist eine konservative
Schätzung, keine Speichergarantie. Verfügbaren RAM/Commit nach der Inferenz messen.
CPU-/Ansichtszahl bleibt Obergrenze; unbekannter/knapper Speicher bleibt seriell.
Policy precision1_memory_bounded_v1. Kein Qualitäts- oder Auflösungswechsel.
Temporäre und fertige PNGs behalten ihre bisherige Kompression. Level 0 wurde
nicht übernommen: reine Kodierersparnis belegt keinen schnelleren Gesamtlauf.
Sprache, Gerät, letzte Eingabepfade, Ausgabemodus/-ordner, Tiefenkartenoption und
Wiggle-Einstellungen bleiben wie bei SplatTricia erhalten. Eingabepfade anzeigen,
kein automatischer Verarbeitungsstart. settings.json atomar über .partial ersetzen;
bei unvollständiger Zahleneingabe die letzte gültige Wiggle-Konfiguration erhalten.

Wiggle-Ausgabe unter wiggle, optional beide vorhandenen Disparitätskarten unter
depth_maps; 16-Bit-PNG, gemeinsame lineare Min/Max-Normierung über beide Karten,
keine Perzentilbeschneidung. Weiß nah / Schwarz fern. JSON dokumentiert die
ursprünglichen signierten Pixelwerte und Rückrechnung, keine metrische Tiefe.
Karten entsprechen den jeweiligen vorverarbeiteten Halbbildern, nicht einer
neuen Mittelansicht. Konstante Karten ergeben Null ohne Division durch Null.
Keine zusätzliche Inferenz oder Prüfung pro Renderframe. Erst vollständige PNGs
im temporären Arbeitsordner schreiben, danach fertige Kartendateien ersetzen.

Christophs ausdrückliche Korrektur vor dem fertigen Paket: Ordnerverarbeitung nur
für direkt enthaltene Bilder, ohne Rekursion. Keine Unterordnerpfade im Dateinamen.
Die zuvor untersuchte SplatTricia-Pfadpräfixregel wird hier nicht übernommen.

Paketprüfung bestanden: 34 lokale Prüfungen (0,22 s), 34 Windows-Prüfungen (0,53 s),
serieller/paralleler nativer RVS-Vergleich bitgleich bei zwei Bildgrößen. Tatsächliche
EXE mit MP4/GIF/PNG, optionalen beidseitigen 16-Bit-Karten, Tiefendiagnose,
Sitzungswiederverwendung, unveränderter Quelle, Temp-Bereinigung, DE/EN,
Einstellungswiederherstellung, Ordnerverarbeitung ohne Unterordner, stabiler
Bediengeometrie bei 100/125/150 %, gezeichneten Buttonfarben und Originalassets.
GPU auf dem Hosted-Basic-Render-Driver nicht initialisierbar; keine neue Bestätigung
für physische GPUs. Die vorhandenen Praxisbeobachtungen ersetzen keine GPU-Prüfung
jedes neuen Builds. Zusätzlich drei echte RVS-Ansichten aus einer vorhandenen
1620x1080-H-Tiefenberechnung erfolgreich erzeugt; keine neue Inferenz nötig.

Gebauter Quellstand: 0c8aefa15f2060b4eb5b4aab806b0cd005c174aa.
Windows-Workflow: https://github.com/muelli1975/Wigglinde/actions/runs/39039085146
Allgemeine Prüfungen: https://github.com/muelli1975/Wigglinde/actions/runs/39039085143
Artifact 12103840135, Wigglinde-1.0-Windows. Inneres ZIP Wigglinde_1.0_Windows.zip:
163894574 Byte, SHA-256 3615a7c05892da2e418a052b69cb5e12264e2456f4f2535ffa15f7df8ee5e036.
ZIP CRC-geprüft, nur H als Anwendungsmodell, keine Logs/Einstellungen/_temp,
Originalicon/-sound bytegleich, gebündelte Quelloptionen geprüft. Archiv enthält
den exakt gebauten Quellstand; dieser spätere Dokumentationsnachtrag gehört nicht
dazu. Die folgenden Testversionen sind historische Prüfstände.


## Test 5: Precision 1

Christoph hat den Bau der nächsten Testversion freigegeben. Einzige Änderung
an der Bildberechnung: RVS Precision 1 statt 2. Modell, vier Iterationen, Float32,
Multispectral 1/4, Linearisierung, Suchversatz und Export bleiben erhalten.
Die konservative Speicherplanung bleibt numerisch unverändert und verwendet
weiterhin die Schätzung der bisherigen Precision-2-Konfiguration.
Kein neuer Schalter und keine weitere Foto-Vergleichsserie. Bestehende schnelle
Prüfungen und Prüfung der gepackten Windows-EXE laufen im Build.
[Windows-Paketprüfung](https://github.com/muelli1975/Wigglinde/actions/runs/39033497358)
bestanden, Quellstand `563e51e62f0e68f2e52f487d4db26477a51c1314`. Fertige EXE:
H-CPU-Exporte MP4/GIF/PNG mit Precision 1, paralleler RVS-Ausgabe, Tiefentest,
Temporärbereinigung und Sitzungswiederverwendung bestätigt. DE/EN, Buttonfarben,
stabile Geometrie, unverändertes Icon/Sound bestätigt; Screenshot angesehen.
Native serielle/parallele Ausgaben bitgleich. Physische DirectML-Inferenz bleibt
auf dem gehosteten Basic Render Driver nicht prüfbar. Separate Prototype-Prüfungen
bestanden. Keine weitere Foto-Vergleichsserie für diesen Build.
ZIP CRC-geprüft, nur H, keine Testlogs/Einstellungen/temporären Dateien,
163888175 Bytes, SHA-256:
`bb3884dbba1ee66bd2a0750707c3ef5bbd799d51c65eca419c73f69f65949de1`.

## Neuer Fotoversuch: Precision 1 / 2

Drei Motive mit denselben H-Karten verglichen: Precision 1 spart lokal 40–43 %
Renderzeit und ca. 70 % Renderer-RAM, zeigt jedoch härtere, stärker abgestufte Kanten.
Vollständige Wiggles und synchrone Detailvergleiche erstellt; alle neun MP4s
vollständig dekodiert. Produktstandard bleibt Precision 2.
Vorgehen, Messwerte und Grenzen: [RVS_PRECISION_COMPARISON.md](RVS_PRECISION_COMPARISON.md).

## Test 4: parallele RVS-Ansichten (17. Oktober 2026)

Freigegeben ist die Beschleunigung der bestehenden Methode. Unabhängige Ansichten
werden in einem begrenzten Fenster parallel berechnet, in ursprünglicher Reihenfolge
ausgegeben und wie zuvor für Rückweg/Zyklen wiederverwendet. Beide Eingangsbilder
werden nur einmal geladen und gemeinsam schreibgeschützt verwendet. RVS-Quellstand
und Bildmathematik bleiben unverändert: CPU, Precision 2, RGB, Multispectral 1/4,
bestehende Füllung und Verkleinerung. L/R-Tausch entfällt ebenfalls im Paket. Der äußere `_temp`-Ordner wird nach
Abschluss, Abbruch oder Fehler entfernt, sofern er leer ist; fremde Inhalte bleiben
erhalten. Erfolg/Fehler und Erhalt fremder Dateien separat lokal geprüft.

Automatische Planung pro Bild: höchstens verfügbare CPU-Kapazität, Ansichtsanzahl
und Speicherbudget. Das Budget verwendet den kleineren verfügbaren RAM-/Commit-Wert
mit Reserve max(1 GiB, 10 % RAM). Konservative Arbeitsschätzung pro gleichzeitig
berechneter Ansicht: Breite × Höhe × 1024 Bytes + 64 MiB; keine Allokationsgarantie.
Bei unbekanntem oder knappem Speicher bleibt eine Ansicht möglich wie zuvor.
Unter Linux werden cgroup-Grenzen berücksichtigt. OpenCV nutzt bei parallelen
Ansichten einen Thread; OpenMP erhält je Ansicht floor(CPU/Ansichten) Threads,
wenigstens einen. So entstehen keine unbeschränkten verschachtelten Threadpools.
Kein neuer Oberflächenregler, keine Reduktion von Auflösung oder Modellqualität.
Andere Programme können später Speicher belegen; eine automatische OOM-Reparatur
oder Qualitäts-/Geräteumschaltung ist weiterhin nicht implementiert.

`rvs_schedule` protokolliert Entscheidung und Ressourcenwerte. Native Messung Schema 2:
`render_work_seconds` summiert überlappende Berechnungen und ist keine Ablaufzeit;
`render_pipeline_seconds` misst den parallelen Ablauf einschließlich Streamwartezeit.
Beide Werte dürfen weder untereinander noch zur Exportzeit addiert werden.

31 schnelle lokale Prüfungen bestanden. Separater nativer Entwicklungstest mit
320×160 und 323×161, Tiefensprüngen und negativen Disparitäten: alle sieben Ansichten
mit zwei und vier Arbeitern sowie Wiederholung bitgenau gleich zum alten seriellen
Aufruf. Reihenfolge und Float32-Werte identisch; Abbruch beendet alle Arbeiter,
fehlende Konfiguration führt ohne blockierte Pipe zum Fehler. Diese Vergleiche
laufen ausdrücklich außerhalb der normalen Bildverarbeitung.

Fotoversuch mit `bild032_cs.jpg`, denselben einmal berechneten LAS2-H-Karten,
1620×1080, sieben Positionen: seriell 29,40 s, drei parallele Ansichten 12,62 s
(Faktor 2,33), komplette Float32-Ausgabe bitgenau identisch (SHA-256 gleich).
Renderer-RSS-Spitze 1017,7 / 2860,0 MiB. Linux, OpenCV 4.6, acht CPU-Kapazitäten,
8 GiB cgroup; jeweils ein Lauf, keine End-to-End- oder Anwender-Hardware-Zusage.
Die Speicherschätzung von 1772,6 MiB je Arbeiter liegt über diesem beobachteten
Bedarf. Größere Auflösungen und andere Motive können anders ausfallen.

[Windows-Build und Paketprüfung](https://github.com/muelli1975/Wigglinde/actions/runs/39029996378)
bestanden, Quellstand `851063a0101d56ef1b5c8038d795269d9b9c3b4c`.
31 schnelle Windows-Prüfungen und separater nativer Vergleich mit zwei/vier Arbeitern
sowie Wiederholung bestanden, alle Float32-Daten bitgleich; Abbruch 0,000662 s.
Tatsächliche EXE: H-CPU-Exporte MP4/GIF/PNG mit vier parallelen Ansichten, leeres
`_temp` nach jedem Export entfernt, Tiefentest ohne Bildausgabe, Sitzungswiederverwendung,
Originalerhalt, DE/EN, Buttonfarben, stabile Geometrie bei 100/125/150 %, geliefertes
Icon und Sound bestätigt. Screenshot angesehen. Gehosteter Basic Render Driver
erlaubt keine reale DirectML-Inferenz; physische GPU-Geschwindigkeit weiter offen.
ZIP CRC-geprüft, nur H, keine Testlogs/Einstellungen/temporären Dateien, 163881756 Bytes,
SHA-256 `864ad4a2dbbc43fd3448daa080b62ed1c83114cb39503097c3bcf60ed60b5ecc`.
Die separaten Prototype-Prüfungen desselben Commits sind ebenfalls bestanden. Lentikular,
Open3D, ein eigener Renderer und Vulkan sind nicht Teil dieser Umsetzung.

### Neue Anwenderbeobachtung: GIF-Schleifenwechsel

Christoph beobachtet in IrfanView Flackern am Zyklusende bei SplatTricia-GIFs,
bei Wigglinde-GIFs nicht. Aktuellen SplatTricia-main-Export und Wigglinde tatsächlich
verglichen: gleicher GIF-Pfad mit gemeinsamer Palette, gespiegelter Bildfolge,
Zeitverteilung, loop=0, disposal=2, optimize=False. Damit ist ein grundsätzlicher
Unterschied im aktuellen Exportcode keine belegte Erklärung. Verwendete ältere
Paketversionen, konkrete GIF-Metadaten/Teilbildrechtecke und Wiedergabeverhalten
sind ohne betroffene Originaldateien noch nicht verglichen. Kein Fix behauptet
und kein Eingriff in SplatTricia erfolgt.

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
