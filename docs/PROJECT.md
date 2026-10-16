# Wigglinde: vereinbarter Projektumfang

Stand: 16. Oktober 2026. Diese Datei beschreibt das Ziel, nicht vorhandene Funktionen.

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
Standards: MP4, 1080 px Höhe, 30 fps; GIF 800 px, 15 fps; PNG 1080 px, 30 fps.

## Geometrie und Qualitätsziel

Gewählter Modellansatz: Lite Any Stereo V2, zunächst LAS2-M. Der aktuelle native
Linux/CPU-Forschungsversuch und RVS-Vergleich stehen in `RVS_COMPARISON.md`.
Der vorhandene CLI-Adapter für C-FoundationStereo-S ist ein früherer Entwicklungsstand;
die vollständige LAS2-Anbindung und portable Auslieferung sind noch offen.
Nach positivem Sichtvergleich ist RVS die bevorzugte Richtung für die Rendererarbeit.
Die gemessene CPU-Laufzeit soll gezielt verbessert werden, bei gleicher Renderqualität.

Eingaben sind fertig justierte Stereopaare. Keine automatische oder manuelle Justage,
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
