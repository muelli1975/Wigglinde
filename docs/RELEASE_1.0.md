# Wigglinde 1.0

Create wiggle animations from already aligned Full-SBS stereo photographs.

- Export MP4, looping GIF or PNG frame sequences.
- Estimate depth with LAS2-H and render intermediate views with MPEG-I RVS.
- Optionally save left/right 16-bit depth maps with scale metadata.
- Process individual images or folders, with cancellation and saved settings.
- German and English interface.

## Installation

Extract the complete package for your system and keep the application folder together. Models and runtimes are included; processing works offline.

- Windows 10/11 x64: start `Wigglinde.exe`. Compatible DirectX 12 graphics cards can accelerate depth estimation through DirectML.
- Linux x64: Ubuntu 22.04 or newer; start `Wigglinde`. Processing uses the CPU.
- macOS 15 or newer: choose Apple Silicon or Intel and open `Wigglinde.app`. Processing uses the CPU. The apps are ad-hoc signed and not Apple-notarized.

Keep `settings.json` when updating. Fine structures and occlusions can produce artifacts; large images need more memory.
