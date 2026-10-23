# RVSVulkan: Prüfung der Übernehmbarkeit

Nachtrag 23. Oktober: Der hier beschriebene Kandidat wird auf Christophs Wunsch
erstmals als separater Test gebaut. Aktueller Stand in DEVELOPMENT.md.
Die unten genannte Multispectral-Konfiguration beschreibt den historischen
Prüfzeitpunkt; die stabile heutige Referenz ist CPU-RVS P1/Simple5.

Stand: 17. Oktober 2026. Quellprüfung, noch kein Build oder GPU-Benchmark.

## Ergebnis

Quellcode und Lizenz sind öffentlich abrufbar. Der vorhandene Vulkan-Renderer
ist eine konkrete Grundlage für einen Entwicklungsvergleich mit LAS2-H.
Ein sofort einsetzbarer Renderer für unseren Stapel-Dateiexport ist er noch nicht:
der ausführbare Headless-Modus fehlt, und die Bildzusammenführung entspricht nicht
unserem CPU-RVS mit Multispectral 1/4. Geschwindigkeit und Fotoqualität sind offen.

## Tatsächlich abgerufener Stand

- Repository: <https://gitlab.ulb.be/hovitron/hovitron-pipeline>
- Abruf über Git erfolgreich, keine Anmeldung erforderlich.
- Commit: `e0f00f9c67dfd868d2b1489051e9118158b6de03`, 24. April 2023.
- Projekt enthält 735 versionierte Dateien; keine generierten Projektseiten als
  Ersatz für fehlenden Quellcode verwendet. Upstream bleibt unverändert.
- Root-`LICENSE`: Apache License 2.0; eigene C++-Kernklassen tragen entsprechende
  Header. Das ist kein abschließender Lizenznachweis sämtlicher Abhängigkeiten.
  Deren Notices und genaue Versionen gehören vor einer Verteilung geprüft.
- Dokumentierte Lizenz: <https://hovitron.gitlab-pages.ulb.be/html/md__l_i_c_e_n_s_e.html>
- Die alte Clone-Adresse in der README zeigt auf eine andere Domain; die aktuelle
  Quelle wurde über die öffentliche Gruppen-API der ULB gefunden.

Alle folgenden Quellpfade beziehen sich auf diesen Commit.

## Build und Eingaben

Buildwurzel ist `RVSVulkan/CMakeLists.txt`, nicht das Repository-Wurzelverzeichnis.
Der eigentliche Renderer liegt unter `RVSVulkan/RVSVulkan`.
Er benötigt C++20, Vulkan, GLFW, GLM und nlohmann/json. Der SampleStreamer benötigt
zusätzlich OpenCV. CUDA wird vom untersuchten Rendererkern nicht benötigt;
optionale Kameramodule dürfen nicht ungefragt mitgebaut werden.

Für einen Desktopversuch explizit `OpenXR=OFF`, `HVT_BUILD_ACQKIRT=OFF`,
`HVT_BUILD_RAYTRIX_STREAMER=OFF` und `HVT_UDP_CONTROL=OFF` setzen. Die tatsächlichen
CMake-Defaults für OpenXR und UDP stehen auf ON/TRUE, entgegen der README-Tabelle.
Ein SampleStreamer oder eigener statischer InputProvider wird zusätzlich benötigt.

`SourcesVulkan/InputProvider.h` und `HvtStreamingAPI.h` definieren Bilder,
Tiefenformate, Kameraparameter und Extrinsik. `BuffersControllerWarping.cpp`
behandelt R32Sfloat explizit als lineare Tiefe. Vorhandene LAS2-Disparitäten können
also mit derselben kontrollierten Geometrieumrechnung wie beim CPU-Vergleich
eingespeist werden; eine Punktwolke oder neue Tiefenschätzung ist nicht nötig.
Dass ein Format im API-Enum steht, beweist noch nicht dessen vollständige
Unterstützung durch den jeweiligen Streamer.

## Noch erforderliche Exportanbindung

`RVSVulkan.cpp` lehnt `--headless` ausdrücklich ab. Aktive Oberflächen sind GLFW
und optional OpenXR. Headset-freier Bildschirmbetrieb ist daher vorhanden,
automatischer Dateiexport ohne Oberfläche jedoch noch nicht.

`VulkanDrawing.cpp` enthält bereits einen Pfad für `copyImageToBuffer` über
`WindowAbstract::getRenderingDestination()`. Die Basismethode wirft aber
`not implemented`; eine vollständige konkrete Headless-Implementierung fehlt.
Das sind brauchbare Anschlussstellen, kein getesteter PNG-/Frameexport.

Für unseren Vergleich werden statische Eingaben, exakt vorgegebene virtuelle
Kameras und Auflösung, GPU-Lesezugriff auf das fertige Bild sowie deterministisches
Ende nach den angeforderten Ansichten gebraucht. Geometrie, Sichtbarkeit und
Rasterung sollen dabei aus dem vorhandenen Renderer übernommen werden.

## Qualitäts- und Hardwaregrenzen

Die Fragmentshader kombinieren Beiträge mit Qualitäts-/Tiefengewichten und einem
Blending-Exponenten. Sie enthalten nicht die CPU-Multispectral-Zusammenführung
mit getrennten niedrigen/hohen Frequenzen (1/4). Auch die CPU-Füllung ist damit
nicht als übernommen belegt. Gleichwertige Kanten, Löcher und Übergänge müssen an
Fotos geprüft werden; eine schnellere Ausgabe ist kein Qualitätsnachweis.

`VulkanContext.cpp` verlangt unter anderem Geometry Shader, anisotrope Sampler
und YCbCr-Sampler-Konvertierung. Bei der Geräteerzeugung wird außerdem
`VK_EXT_shader_image_atomic_int64` angefordert. Allgemeine Vulkan-Unterstützung
allein beweist deshalb keine Kompatibilität mit jedem Adapter.
Kein stiller Gerätewechsel und keine automatische Qualitätsreduktion vorsehen.

## Begrenzter nächster Versuch

1. Separaten Entwicklungsadapter für feste RGB-D-Paare und Bildausgabe bauen;
   keinen Austausch des Produkt-Renderers vorwegnehmen.
2. Exakt dieselben H-Tiefenkarten und Blickpositionen wie CPU-RVS verwenden.
3. Wenige Positionen und einen kurzen Wiggle auf einer echten GPU vergleichen:
   Renderzeit, Speicher, vollständige Ränder, Farbtreue, Äste und Doppelkonturen.
4. Erst nach Sichtvergleich über Integration entscheiden. CPU bleibt verfügbar.

In dieser Prüfung wurde kein Vulkan-Build gestartet. Die aktuelle Linux-
Arbeitsumgebung stellt weder ein Vulkan-SDK noch einen Vulkan-Treiber bereit.
Windows-Kompilierbarkeit und RTX-3060-Laufzeit sind somit nicht bestätigt.

## Offizielle Dokumentation

- <https://hovitron.gitlab-pages.ulb.be/html/index.html>
- <https://hovitron.gitlab-pages.ulb.be/RVSVulkan/RVSVulkan/>
- <https://hovitron.gitlab-pages.ulb.be/RVSVulkan/RVSVulkan/README_how/>
