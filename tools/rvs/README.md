# Begrenzter RVS-Vergleich, 16. Oktober 2026

Entwicklungsversuch unter Linux/CPU, kein neuer Produkt-Renderer und kein portables
Windows-Paket. Originalfotos, Gewichtedateien, Szenen und Videos gehören nicht ins Git.
Aktueller Befund und nächste Schritte: `docs/RVS_COMPARISON.md`.

## Identität und Abhängigkeiten

- RVS: https://gitlab.com/mpeg-i-visual/rvs,
  `d757a353c7f84d228ac30c179d6ff9de356c6101`. Quellcode unverändert.
  Seine BSD-Lizenz enthält einen zusätzlichen Vorbehalt zu Patent-/Drittrechten;
  die originale Datei `LICENSE` muss bei einer späteren Distribution erhalten bleiben.
- OpenCV 4.6.0, nur core/imgproc/photo zum Linken; libtbb12, g++.
- Python: NumPy, Pillow; für optionale native Neuberechnung torch/torchvision/timm.
- FFmpeg mit libx264 und zscale für Vergleichsvideos.
- LAS2: https://github.com/TomTomTommi/LiteAnyStereo,
  `8c97bd4c4da3712c2ac60003a23201dfdb5935f4`, MIT.
- Gewichte: https://huggingface.co/tomtomtommi/LiteAnyStereoV2,
  Revision `17788d91618646fa781a14462e2926a034b9f49d`, LAS2_M.pth.
  SHA-256 `c41b61efce9b36e6b8b38b580421cd20cc9e84a47f0f45361767281938f69696`.

## Anbindung

Die Umrechnung steht in `prepare.py`: virtuelle Basis 1, Brennweite in Pixeln gleich
Bildbreite, Hauptpunkt links `w/2`, rechts `w/2+64`, Tiefe `Z=w/(d+64)`.
Bei Position t liegen Kamera und Hauptpunkt jeweils linear zwischen den Eingaben.
Dies ergibt exakt `xL-t*dL` beziehungsweise `xR+(1-t)*dR` einschließlich negativer
Disparitäten. Keine Justage, kein Beschnitt, keine Änderung der Scheinfensterlage.
Der Runner prüft diese Abbildung zusätzlich mit RVS' tatsächlichen Projektionsklassen.
Die Wahl +64 ist explizit für diese gespeicherte Szene und keine allgemeine Eingaberegel.

RGB wird für beide Renderer identisch in lineares sRGB umgerechnet; rohe Float32-
Matrizen umgehen Dateiformat-/Gamma-Konvertierungen. Einheiten der virtuellen Tiefe
sind keine gemessenen Meter. Die Verarbeitung nutzt die unveränderten RVS-Klassen
für Dreiecke, Multispectral-Blending (1/4), Füllung und anschließende Verkleinerung
der zweifach abgetasteten Ansicht. Das Eingabebild bleibt 960×640.

## Reproduktion

RVS und lokale OpenCV-Entwicklungsdateien zuerst bereitstellen. Alle Pfade bewusst
wählen; die Skripte laden nichts herunter. Vom Wigglinde-Repository aus:

```sh
python tools/rvs/build.py /path/to/rvs /path/to/opencv/usr /path/to/work/rvs-check/runner
python tools/rvs/prepare.py /path/to/work/rvs-check/scene.npz /path/to/work/rvs-check/probe
```

Der Runner nimmt `config.json`, einen Ausgabeprefix und `multi` oder `simple`.
Die zusätzliche Projektionsprüfung läuft ausschließlich bei ausdrücklich
angehängtem `--verify-projection`. Sie ist ein Entwicklungstest, keine normale
Stapelprüfung. Stufenzeiten werden separat protokolliert, ohne erneut zu rendern.
Bei lokal entpackten OpenCV-Paketen muss deren Bibliotheksordner auch über
`LD_LIBRARY_PATH` erreichbar sein. `OMP_NUM_THREADS=8` setzen. Geprüfter Umfang:
zwei Eingaben, identische Größe, ausschließlich CPU. Aufrufbeispiel:

```sh
LD_LIBRARY_PATH=/path/to/opencv/usr/lib/x86_64-linux-gnu OMP_NUM_THREADS=8 /path/to/work/rvs-check/runner /path/to/work/rvs-check/probe/config.json /path/to/work/rvs-check/probe/rvs multi
```

Für den Clip `prepare.prepare(...)` mit Precision 2 und 31 Positionen
`(1-cos(2*pi*i/60))/2`, i=0..30, in `rvs-check/animation` aufrufen; denselben Runner
nutzen. `baseline.py SCENE.npz BASELINE_FOLDER positions.json` berechnet den
unveränderten Vergleichsrenderer separat. `finish.py WORK_ROOT` erwartet genau
diese Verzeichnisstruktur plus Probe mit Precision 1 und erzeugt die Clips und JSON.
Alle Rückwege verwenden dieselben Ansichten, fünf Zyklen à zwei Sekunden, 30 fps.

Falls die gespeicherte Szene fehlt, kann `infer_native.py` sie aus den beiden
gesicherten Endansichten und den geprüften lokalen LAS2-M-Gewichten wiederherstellen.
Das verwendet bewusst das native FP32-Modell, nicht den inzwischen verlorenen
lokalen ONNX-Export. Beide Renderer erhalten immer dieselbe `scene.npz`.

Wichtig: RVS rendert seine Endansichten selbst. Ein Ersetzen durch Originale würde
in dieser Konfiguration wieder Sprünge verursachen. Der Clip versteckt diesen
Unterschied nicht durch Überblendungen oder zusätzliche zeitliche Filter.
