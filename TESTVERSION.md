# Wigglinde 1.2 Test 1

Separate Windows test package for comparing stereo models and renderers.
This is an experiment for a possible 1.2. The published 1.1 stays unchanged.

- Models: LAS2-H (default, 4 iterations), IGEV++ Middlebury (16), and
  GREAT-IGEV Middlebury (32).
- Renderers: RVS (CPU, default) and TMIV/VWS (CPU), selected independently.
- CPU stereo uses Float32; Windows GPU uses DirectML mixed Float16/Float32.
- VWS uses unchanged official TMIV code and MPEG best-reference parameters,
  including the original 10-bit internal geometry and YUV 4:2:0 transport.
- Existing output formats, resolution/FPS choices, cycle controls and colors
  remain. Animation names add `_rvs` or `_vws` to keep comparisons separate.
- No lenticular functions. Their development follows the quality evaluation.

Extract into a separate folder and start `Wigglinde.exe`. Test settings use
`settings-test-1.2.json`; there is no change to the stable application's settings.
All models are included; no PyTorch/CUDA installation or runtime download.

For a useful comparison, first keep Middlebury selected and compare RVS/VWS.
Then keep RVS selected and compare Middlebury/GREAT-IGEV. Use the same image,
resolution and animation settings. Finally try GREAT-IGEV with VWS.

GREAT is heavier than Middlebury and model loading can take noticeably longer.
The local full-photo checks and mixed-graph CPU checks do not establish physical
DirectML performance or a 2160p memory guarantee. The test build attempts DirectML
on its Windows runner and records whether it is available. Detailed diagnostics
are in `logs/latest_run.json`.

## Deutsch

Separate Windows-Testversion für den Vergleich von Stereomodellen und Renderern.
Eine mögliche 1.2 hängt vom praktischen Qualitätsgewinn ab; die veröffentlichte
1.1 bleibt unverändert.

LAS2-H bleibt Standard. Hinzu kommen GREAT-IGEV Middlebury und die unabhängige
Rendererwahl RVS/VWS. VWS verwendet unveränderten offiziellen TMIV-Code und die
MPEG-Standardparameter einschließlich interner 10-Bit-Tiefe und 4:2:0-Verarbeitung.
Die übrigen Ausgabeoptionen bleiben erhalten. Rendererzusätze in Animationsnamen
verhindern gegenseitiges Überschreiben der Vergleichsergebnisse.

In einen eigenen Ordner entpacken und `Wigglinde.exe` starten. Die Testversion
speichert ihre Einstellungen separat. Zuerst bei Middlebury RVS/VWS vergleichen,
danach bei RVS Middlebury/GREAT – jeweils bei identischen Ausgabeparametern.
GREAT benötigt mehr Ressourcen und kann länger zum Laden brauchen. GPU-Leistung
und große Auflösungen sind auf der eigenen Hardware zu beurteilen.
Lentikular-Funktionen folgen erst nach dieser Auswertung.
