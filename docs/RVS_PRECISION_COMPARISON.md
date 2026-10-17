# RVS Precision 1 / 2: Fotoversuch, 17. Oktober 2026

Christoph hat den Vergleich freigegeben. Keine Änderung von Produktstandard,
GUI, LAS2 oder RVS-Quellcode. Nur der vorhandene Precision-Parameter wird variiert.

## Vorgehen

Drei zuvor gelieferte Full-SBS-Fotos: Straße mit Laub/Fahrrädern, Lkw mit Wolken und
Bäumen, Museumshalle mit Seilen/Geländern. Jeweils 1620×1080 px pro Ansicht,
LAS2-H, vier Iterationen, Float32, gleicher Matching-Offset wie im Programm.
Die beiden H-Karten werden pro Foto einmal berechnet, gespeichert und für beide
Varianten bytegleich wiederverwendet. Präzisionsparameter betrifft nur RVS.

31 identische sinusförmige Kamerapositionen, drei parallele Ansichten, je zwei
OpenMP-Threads und ein OpenCV-Thread, Multispectral 1/4, bestehende Füllung und
Verkleinerung. P2 rastert in 3240×2160, P1 direkt in 1620×1080. Beide Ausgaben sind
1620×1080. Linux/OpenCV 4.6, acht CPU-Kapazitäten, 8-GiB-cgroup. Modellprozess ist
vor Rendering beendet; die native RSS-Spitze enthält kein H-Modell.

Entwicklungswerkzeug: `tools/rvs/compare_precision.py`. Szene-NPZ enthält `left`,
`right`, `dl`, `dr`, `offset`; nichts wird heruntergeladen. `--workers 3
--threads-per-view 2` ist eine bewusste Testbegrenzung, keine Produktänderung.
Clips entstehen aus denselben verlustfreien Ansichten: 30 fps, zwei Sekunden pro
Pendelzyklus, fünf Zyklen, H.264 CRF 18/slow und sRGB→Rec.709 wie im Programm.
Zusätzlich synchroner Detailvergleich P1 links/P2 rechts ohne Skalierung, CRF 12.

## Messung

Native `render_pipeline_seconds`: Rendering einschließlich Datenübergabe und
Wartezeiten, während Python die verlustfreien PNGs schreibt. Keine H-Inferenz oder
abschließende MP4-Kodierung. Die Summe `render_work_seconds` überlappt und wird
nicht als Ablaufzeit angegeben. RSS ist die native Linux-Prozessspitze aus getrusage.
Je Variante ein ausgewerteter Lauf; beim Lkw wurde P1 ohne parallel laufende
Zusatzarbeit wiederholt und dieser zweite Lauf verwendet. Keine Aussage über die
Gesamtzeit auf Christophs Windows-/RTX-3060-System.

| Motiv | Precision 2 | Precision 1 | Faktor | Renderer-RSS P2 / P1 |
| --- | ---: | ---: | ---: | ---: |
| bild032_cs | 52.05 s | 29.55 s | 1.76 | 2.81 / 0.84 GiB |
| bild115_cs | 49.07 s | 29.42 s | 1.67 | 2.69 / 0.83 GiB |
| bild138_cs | 49.85 s | 30.10 s | 1.66 | 2.78 / 0.85 GiB |

Precision 1 spart hier ungefähr 40–43 % Ablaufzeit und 69–70 % Renderer-RAM.
Die viermal kleinere Rasterfläche macht den Gesamtablauf nicht viermal schneller:
Quellprojektion, Dreiecke und Ausgabe verschwinden dadurch nicht.

## Sichtprüfung und Grenzen

Verlustfreie Mittelansichten mit Ausschnitten bei 100 % und vier aufeinanderfolgende
Bewegungsphasen angesehen. P1 ist sichtbar härter/schärfer; an Fahrradspeichen,
Seilen und Geländern sind stärker abgestufte Kanten erkennbar. P2 ist glatter und
weicher. Statische Ausschnitte belegen keine subjektive Gleichwertigkeit in Bewegung.
Die synchronen Videos sind für die direkte Anwendersichtung beigefügt. Keine
Referenz-Zwischenansichten vorhanden; MAE-Werte im Bericht sind Abweichungen, keine
Qualitätsbewertung. Keine Behauptung, Flimmerfreiheit sei für P1 bestätigt.

Alle neun MP4s vollständig dekodiert: je 300 Frames, volle Wiggles 1620×1080,
Detailvergleiche 900×330. Vergleichsarchiv CRC-geprüft. Fotos, Tiefenkarten,
Vergleichsbilder und Videos bleiben außerhalb des öffentlichen Repositorys.
Ein unvollständiges lokales Zwischen-PNG im ersten Straßenlauf wurde aus denselben
Karten neu gerendert; eine zusätzliche Kontrollansicht war bytegleich. Der finale
Clip wurde neu kodiert und vollständig dekodiert. Neue Testausgaben schreiben PNGs
über einen Speicherpuffer, damit die Dateischreibung vollständig kontrolliert wird.

Precision 2 bleibt der Produktstandard. Dieser Versuch baut keine neue Windows-
Version und fügt keine automatische Qualitäts-/Auflösungsreduktion hinzu.

## Neue Anwenderwerte für Test 4

Christoph meldet 1080p H: CPU ca. 60 s, GPU ca. 42 s, Ergebnisse weiterhin gleich gut.
Ein anschließend gelieferter GPU-Lauf: 39,274 s gesamt; H 1,534 s, Ansichtsmaterialisierung
31,068 s, Kodierung/Kopieren 3,864 s; zwölf parallele Ansichten bei zwölf CPU-Kapazitäten.
Renderer-RSS-Spitze 10,004 GiB, noch ca. 17,174 GiB physischer RAM verfügbar. In diesem
Lauf begrenzt CPU-Kapazität die Parallelität, nicht die Speicherschätzung. Diese
Messung ist unabhängig von den lokalen Precision-Vergleichszeiten oben.
