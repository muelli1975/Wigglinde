# Lokale Modelle

Test 2 bietet **LAS2-M, LAS2-L und LAS2-H**. Beim ersten Start ist **L** vorausgewählt,
danach wird die letzte Wahl gespeichert. Alle drei Modelle werden mitgeliefert;
keine Downloads oder automatische Modellumschaltung im Anwendungscode.

- Code: TomTomTommi/LiteAnyStereo, Revision `8c97bd4c4da3712c2ac60003a23201dfdb5935f4`.
- Gewichte: tomtomtommi/LiteAnyStereoV2, Revision `17788d91618646fa781a14462e2926a034b9f49d`.
- M: 41925933 Byte, SHA-256 `c41b61efce9b36e6b8b38b580421cd20cc9e84a47f0f45361767281938f69696`.
- L: 109270797 Byte, SHA-256 `12f86f758b0aa6cd59c11d40f41e7d954121d7626e4719eff71d9dd22da36539`.
- H: 46698761 Byte, SHA-256 `758585a25c3a332711f92a28ad1437e08080fb714ad1146de7cf2c01ce8479f4`.
- Code und veröffentlichte Gewichte: MIT; Lizenztext im Paket.
- Dynamische ONNX-Exporte: `models/las2/LAS2_{M,L,H}_dynamic.onnx`, jeweils
  mit JSON-Metadaten und tatsächlichem ONNX-Hash.
- Export nach offiziellen Ersetzungen; Vergleich mit nativem Modell an zwei
  Bildgrößen. H behält die vier Iterationen des veröffentlichten Modells.
- RGB float32 0..255, Normalisierung im Modell, Edge-Padding auf Vielfache von 32.
  Temporärer Suchversatz wird vollständig entfernt. Keine Justage oder Crop.
- Suchbereich 192 Pixel; beidseitige Berechnung.
- Windows: eigener ONNX-Runtime-DirectML-Build mit `onnxruntime_USE_TELEMETRY=OFF`.

## Historischer Qualitätsprototyp: C-FoundationStereo-S

Die Anwendung lädt ausschließlich eine bereits vorhandene Datei. Sie enthält
keine Downloadfunktion und benötigt weder Token noch externen Modell-Cache.
Modellgewichte werden nicht in Git eingecheckt.

Erster Kandidat ist die separat freigegebene NVIDIA-Fassung **C-FoundationStereo-S**,
nicht der nur für Forschung freigegebene NVlabs-Quellcode.

- Anbieter: https://huggingface.co/nvidia/c-foundationstereo-s
- Geprüfte Datei: `onnx/deployable_foundation_stereo_s_dynamic.onnx`
- Revision: `ee0de5e` (Hugging Face commit, dynamischer Export v2.0)
- Dateigröße: 346531163 Byte
- SHA-256: `a001a7bc0512a0bc3b3218194e924784e58b20656c6f1ea2c151024e555cfd64`
- Lizenz: https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-open-model-license/

Die Modelllizenz erlaubt Nutzung und Weitergabe einschließlich kommerzieller
Nutzung unter ihren Bedingungen. Vor einem gebündelten Release müssen der genaue
Lizenztext, der geforderte NOTICE-Hinweis und weitere Komponentenhinweise beigelegt
werden. Die MIT-Lizenz unseres Codes ersetzt diese Modelllizenz nicht.

## Inspektierte Schnittstelle

Zwei `float32`-Eingaben `left_image`, `right_image`, jeweils `[1, 3, H, W]`.
Eine `float32`-Ausgabe `disparity`, `[1, 1, H, W]`; Disparität in Pixeln.
Opset 17, keine benutzerdefinierten ONNX-Operatoren, 53448 Graphknoten.

RGB nach [0, 1], dann ImageNet-Mittelwerte `[0.485, 0.456, 0.406]` und
Standardabweichungen `[0.229, 0.224, 0.225]`. Symmetrisches Edge-Padding auf ein
Vielfaches von 32 und mindestens 416 px Breite, anschließend ausschließlich dieses
Padding entfernen. Die Mindestbreite folgt aus den 104 Suchpositionen bei 1/4 Größe
im tatsächlich inspektierten Graphen; kleinere ungepaddete Eingaben laufen dort
in eine leere Slice/Reshape-Operation. Kleine Fotos werden nicht hochskaliert.
Keine automatische Verkleinerung, keine Ableitung von Fotoqualität aus der Dateiform.

Der große dynamische Graph zeigte hier eine sehr langsame Speicherplanung bei
Standardeinstellungen. Der Diagnoseadapter deaktiviert die Wiederverwendung von
Tensorzuweisungen und das Memory-Pattern. Das ändert keine Modellpräzision oder
Auflösung, kann aber mehr Speicher benötigen. Der Bedarf bei Fotoauflösung ist
vor einer Produktentscheidung zu messen. Es gibt keine voreingestellte Threadbegrenzung.

Schnittstellenreferenzen (nur gelesen; kein TAO-/NVlabs-Code übernommen):
- https://github.com/NVIDIA-TAO/tao-pytorch/blob/main/nvidia_tao_pytorch/cv/depth_net/dataloader/transforms.py
- https://github.com/NVIDIA-TAO/tao-pytorch/blob/main/nvidia_tao_pytorch/config/depth_net/dataset.py
- https://github.com/NVIDIA-TAO/tao-pytorch/blob/main/nvidia_tao_pytorch/cv/depth_net/model/stereo_depth/pl_stereo_model.py

Der Adapter prüft die gewählte CPU-/CUDA-Laufzeit. Ein fehlendes oder nicht
initialisierbares CUDA-Gerät führt nicht zu einem vollständigen CPU-Ersatzlauf.
Übliche CPU-Hilfsoperationen innerhalb einer CUDA-Sitzung sind damit nicht ausgeschlossen.

Ein kleiner CPU-Modellversuch unter Windows Server 2025 war erfolgreich.
Desktop-Windows-/CUDA-Betrieb, Speicherbedarf großer Fotos und Fotoqualität sind noch offen.
Aktuellen tatsächlichen Teststand in `docs/DEVELOPMENT.md` beachten.
