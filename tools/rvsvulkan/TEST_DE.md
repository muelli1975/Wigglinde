# Wigglinde – separater Vulkan-Test

Diese Testversion ergänzt die unveränderte 1.1-Basis um die Auswahl zwischen
RVS (CPU) und RVSVulkan (GPU). LAS2-H bleibt Standard, IGEV++ Middlebury bleibt
für schwierige Motive verfügbar. Die veröffentlichte 1.1 wird nicht ersetzt.

Der Renderer wird unten in den Optionen gewählt. Das bisherige Verarbeitungsgerät
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
Auslesen der fertigen Bilder. Sie fügt keine Filter oder Lückenfüllung hinzu.
RVSVulkan ist eine eigene RVS-Implementierung; pixelgleiche CPU-Ergebnisse sind
damit nicht zugesichert.

Einstellungen liegen getrennt in `settings-vulkan-test.json`.
Lokale Protokolle stehen wie bisher in `logs`. Der Test arbeitet nach dem
Entpacken offline und benötigt weder Headset noch Kamera-Schnittstellen.

Quelle: <https://gitlab.ulb.be/hovitron/hovitron-pipeline>
