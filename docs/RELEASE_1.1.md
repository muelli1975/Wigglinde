# Wigglinde 1.1

- Add IGEV++ Middlebury as an alternative depth model for difficult image structures. LAS2-H remains the default.
- Add animated AVIF export alongside MP4, GIF and PNG sequences.
- Identify the selected model in output filenames and depth-map metadata.
- Remember the model selection between sessions.
- Add an adjustable MP4 cycle count (default: 5).
- Reduce animated AVIF file sizes.
- Remember animation size and frame rate separately for each format.

## Installation

Extract the complete package for your system and keep the application folder together. Models and runtimes are included; processing works offline.

- Windows 10/11 x64: start `Wigglinde.exe`. Compatible DirectX 12 graphics cards can accelerate depth estimation through DirectML.
- Linux x64: Ubuntu 22.04 or newer; start `Wigglinde`. Processing uses the CPU.
- macOS 15 or newer: choose Apple Silicon or Intel and open `Wigglinde.app`. Processing uses the CPU. The apps are ad-hoc signed and not Apple-notarized.

Keep `settings.json` when updating. Difficult structures, occlusions and reflections can still produce artifacts; large images need more memory.
