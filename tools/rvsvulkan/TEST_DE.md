# Wigglinde – separater Vulkan-Test

Diese Testversion ergänzt die unveränderte 1.1-Basis um die Auswahl zwischen
RVS (CPU) und RVSVulkan (GPU). LAS2-H bleibt Standard, IGEV++ Middlebury bleibt
für schwierige Motive verfügbar. Die veröffentlichte 1.1 wird nicht ersetzt.

Modell, Berechnung und Renderer stehen gemeinsam in einer Auswahlzeile.
Das unter Berechnung gewählte Gerät
CPU/GPU steuert weiterhin die Tiefenschätzung. RVSVulkan rendert unabhängig davon
auf einer von seiner ursprünglichen Geräteauswahl bestimmten Vulkan-GPU.
Die tatsächliche GPU steht anschließend im lokalen Laufprotokoll.
Es gibt keinen automatischen Wechsel zum CPU-Renderer.

Bitte zunächst dasselbe Bild, Modell, dieselbe Größe und dieselben Ausgabeoptionen
einmal mit RVS (CPU) und einmal mit RVSVulkan (GPU) ausgeben. Die Vulkan-Ergebnisse
tragen zusätzlich `_rvsvulkan`, sodass die CPU-Referenz erhalten bleibt.
Für die Sichtprüfung sind PNG-Bildfolgen besonders hilfreich, weil zusätzliche
Kompression als Ursache entfällt. Ein Wiggle zeigt ergänzend das Verhalten in
Bewegung. Gitterstreben, Konturen, Fernbereich und Wendepunkte vergleichen.

Benötigt wird ein geeigneter Vulkan-Treiber. Die ursprünglichen
Hardwareanforderungen von RVSVulkan wurden nicht gelockert. Diese
Entwicklungsumgebung kann die Funktion auf einer RTX 3060 nicht bestätigen.
Ein Kompilierungs- oder GUI-Test belegt noch keine Fotoqualität oder Beschleunigung.

Verwendet wird HoviTron RVSVulkan, Commit
`e0f00f9c67dfd868d2b1489051e9118158b6de03`, mit ursprünglicher Rasterpipeline,
Blending-Faktor 5, Dreiecksschwelle 30, linearen Tiefen und unveränderten Shadern.
Die Anbindung ergänzt feste Bildeingaben, passende Kameraparameter und das
Auslesen der fertigen Bilder. Der gemeinsame Tiefenbereich wird aus den tatsächlich
übergebenen Float-Tiefenkarten ermittelt; deren Werte werden nicht verändert.
Eine fehlerhafte Verzweigung im ursprünglichen Ausgabe-Code ist korrigiert:
Ohne Bildschirm wird direkt in den Exportpuffer kopiert. Rasterung, Blending und
Shader bleiben erhalten. Die Anbindung fügt keine Filter oder Lückenfüllung hinzu.
RVSVulkan ist eine eigene RVS-Implementierung; pixelgleiche CPU-Ergebnisse sind
damit nicht zugesichert.

Einstellungen liegen getrennt in `settings-vulkan-test.json`.
GIF bietet zusätzlich512Pixel an der langen Seite; Standard bleibt800.
Die Verarbeitung läuft in einem eigenen Arbeitsprozess, damit die Oberfläche
auch beim nativen Modellstart reagiert. Bei Abbruch kann eine bereits laufende
Modellinitialisierung noch zu Ende laufen. Die Modellsitzung wird im Stapel
wiederverwendet; an Bildberechnung und Qualitätsparametern ändert sich nichts.
Lokale Protokolle stehen wie bisher in `logs`. Der Test arbeitet nach dem
Entpacken offline und benötigt weder Headset noch Kamera-Schnittstellen.

Quelle: <https://gitlab.ulb.be/hovitron/hovitron-pipeline>

## Korrektur der Bildübertragung (23. Oktober 2026)

Die ursprüngliche C-Meldung `Real number of elements …` wurde im bisherigen
Adapter in denselben stdout-Kanal wie die Float-Bilddaten geschrieben.
Die vorhandene cout-Umleitung erfasste printf nicht. Bei 1080×720 entstehen
32 zusätzliche Bytes (verschobene Farbkanäle), bei 1620×1080 33 Bytes
(zerstörte Float-Ausrichtung). Die Diagnoseausgaben werden jetzt einschließlich
C-stdio in stderr geführt; die Bilddaten benutzen einen zuvor duplizierten,
eigenständigen Binärkanal. Tests erkennen ausdrücklich auch den alten Fehler.

Die Anwendung überträgt beim Vulkan-Renderer die bereits vorliegenden RGB8-Werte
jetzt direkt als RGB24. Die bisherige Umwandlung RGBA8 → RGB-Float32 → RGB8
entfällt. Pro Bild sind damit ein Viertel der bisherigen Pipe-Bytes erforderlich;
alle 256 Kanalwerte bleiben unverändert. CPU-RVS behält seinen Float32-Pfad.
Die bewährten Raster-, Tiefen-, Blending-, Gamma- und Shaderoperationen werden
durch diese Korrektur nicht verändert. Der Native-Test prüft beide Transportformate
mit C- und C++-Meldungen vor und zwischen Bildern, ohne eine GPU vorauszusetzen.

Das Laufprotokoll ergänzt `stream_format`, `stream_bytes` und
`pixel_pack_seconds`. `stream_write_seconds` kann Wartezeit auf den
Bildexport enthalten; es ist keine isolierte GPU-Zeit. Der geringere Datentransport
ist kein Nachweis einer entsprechenden Beschleunigung des gesamten Exports.
Ein neuer Laufzeitvergleich auf Christophs RTX 3060 bleibt erforderlich.
