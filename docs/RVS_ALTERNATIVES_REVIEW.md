# Renderer alternatives: VVS and TMIV/VWS — 23 October 2026

Source review only. No renderer has been replaced, packaged or compared on the
private photo by this investigation. Quality has priority over speed.

## VVS is not simply RVS's direct successor

MPEG's [N18994 activity summary](https://www.multimedia.edu.pl/publications/N18994-Summary-on-MPEG-I-Visual-Activities.pdf),
section 9.3, describes two successors to older VSRS in different activities:
RVS for 3DoF+ and VVS for 6DoF. Both accept two or more reference views with depth,
and both support perspective and ERP projections. ERP support alone therefore
does not establish an advantage over RVS for Wigglinde's two perspective photos.

Orange Labs' [July 2019 MPEG workshop presentation](https://mpeg.chiariglione.org/sites/default/files/events/6.%20Workshop%20MPEG-July2019%20-%20JJung.pdf)
describes quality-aware reference selection, safe warping around object borders,
conditional depth merging, spatio-temporal inpainting and edge filtering. Its
reported gain is versus VSRS under the stated common test conditions. It does
not prove better results than Wigglinde's CPU RVS on a two-photo railing scene.

The historical official source URL is
`http://mpegx.int-evry.fr/software/MPEG/Explorations/6DoF/VVS.git`.
An unauthenticated read-only `git ls-remote` attempt returned HTTP 503 here.
Current source availability and the applicable VVS license remain unverified;
there is no basis to classify it as a ready drop-in component.

## VWS is a distinct renderer within TMIV

MPEG's approved [TMIV 17 description, N0376](https://www.multimedia.edu.pl/publications/N0376-Test-model-17-for-MPEG-immersive-video.pdf),
section 5.4, documents both an RVS-based synthesizer (called AdditiveSynthesizer
in the code) and the View Weighting Synthesizer. VWS is therefore not a separate
stereo-depth estimator or a prerequisite to a codec migration.

VWS uses splat-based geometry rasterization rather than RVS triangulation.
It forms a target visibility map through weighted voting and median filtering,
then shades using visibility consistency and per-view weights. Input contours
are discarded to reduce ghosting; depth-edge areas are blurred. These operations
are plausible candidates for the bright/double edge problem, but filtering and
blur may also weaken fine railings. No quality improvement is assumed.

The [2024 common test conditions, N0495](https://www.multimedia.edu.pl/publications/N0495-Common-test-conditions-for-MPEG-immersive-video.pdf)
explicitly use a best-reference path that renders the complete source material
with TMIV/VWS without coding. A renderer comparison therefore does not require
MIV encoding, VVC/HEVC integration or replacement of Wigglinde's export formats.

## Actual source inspection

Official repository: https://gitlab.com/mpeg-i-visual/tmiv

Inspected revision: `8faacbe722f0e2fc1dc6f8247eb2da166a0297c6`.

- `doc/running.md`: separate best-reference renderer path.
- `source/Renderer/app/Renderer_main.cpp`: `TmivRenderer` loads multiview color,
  depth and camera configuration directly, constructs the render input and emits
  target viewports. It does not need an encoded MIV bitstream in this path.
- `source/Renderer/src/ViewWeightingSynthesizer.cpp`: visibility filtering,
  splat parameters, shading and depth-edge blur are implemented.
- `config/ctc/best_reference/R_1_TMIV_render.json`: VWS with explicit parameters,
  including one visibility median-filter pass and edge blur block size 5.
- CMake 3.22+, C++17 or newer, conventional Windows/Linux compiler paths. There
  are configurable application/library build subsets. A renderer-only build
  should be checked before adding codec dependencies listed for the full suite.
- `LICENSE`: BSD three-clause conditions, copyright ISO/IEC 2019–2025. It
  explicitly does not grant other contributor/third-party rights, including
  patent rights. This is a source-license observation, not a blanket clearance
  for every MPEG codec or standard component.

This checkout was inspected only; no native build, CPU/RAM benchmark or photo
render has been run. It has no demonstrated dependence on our rejected OpenGL
render path; selecting a different rendering algorithm is a separate experiment.

## Useful comparison design

Prioritize TMIV/VWS over the older, currently inaccessible VVS source. Keep the
stereo model and both disparity maps fixed, initially using released Middlebury.
Use the exact same two source photos, camera geometry and target positions. Map
signed disparity, near/far normalization and camera conventions explicitly;
record depth quantization and RGB/YUV conversion. Select full-chroma I/O where
available, so color subsampling is not confused with renderer quality. Compare
lossless PNG views before animated export. Do not crop or align the originals.

Include railings, hair, foliage and sky/foreground edges, record runtime/RAM,
and inspect both motion and static close-ups. A separate GREAT-IGEV comparison
must continue using CPU RVS so a model change and renderer change are not mixed
in the same attribution. Only then decide whether a product renderer option or
replacement earns its added integration and maintenance cost.
