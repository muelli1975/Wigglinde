# Integration update — 18 October 2026

Test4 now integrates Middlebury under its MIT project notice with explicit
checkpoint provenance. Further primary-source review found no contradictory
weight rule; absence of an extra LICENSE is not treated as a new prohibition.
The author's predecessor-project commercial-use reply confirms MIT:
https://github.com/gangweiX/IGEV/issues/6 . This supports the project-license
reading; it is not a PTH-specific grant. Actual technical verification and current
limitations are tracked in DEVELOPMENT.md. The original isolated findings below
record the earlier investigation, before integration.

# IGEV++: isolierter Qualitäts- und Integrationsversuch

Stand 18. Oktober 2026. Noch kein Bestandteil des Test-3-Pakets.

## Ergebnis am Problemfoto

Offizieller Middlebury-Checkpoint trennt viele dünne Geländerstäbe und die
fernen Zwischenräume deutlich besser als LAS2-H/vier oder IGEV++/SceneFlow.
Mit denselben beiden Eingaben und demselben CPU-RVS/P1/Simple-5-Renderer bleibt
der Vorteil in der mittleren Ansicht sichtbar. Restfehler bleiben; kein
allgemeines Qualitätsurteil und kein Vergleich mit einer echten Mittelaufnahme.

Unveränderte 1024×682 je Auge, sRGB-Umrechnung wie LAS2, Float32, acht Threads,
16 Autoren-Iterationen, max_disp 768, reversibler Suchversatz 68 (anschließend
entfernt). Rechte Karte mit getauschten und horizontal gespiegelten Eingaben.
Keine Justage, Skalierung, Konvergenz- oder Originaländerung. Fünf RVS-Ansichten.
CPU läuft nach isolierter Geräteanpassung ohne CUDA-Extension. Vollständiges
Checkpoint-Laden mit strict=True; timm 0.5.4 isoliert, kein ImageNet-Download.
Prozess-RSS etwa 2,6 GiB. Einzelaugenläufe 18–54 s bei wechselnder CPU-Konkurrenz;
kein belastbarer Geschwindigkeitsvergleich und keine 2160p-Speicherzusage.

## Noch vor einer Aufnahme ins Paket zu klären

- Code MIT; Geltung für separat gehostete Gewichte nicht ausdrücklich bestätigt.
  Keine Forschungsbeschränkung gefunden. Der offizielle Drive-Ordner enthält
  PTH-Dateien ohne eigene Lizenz-/Modelldatei. MIT-Tags fremder HF-Kopien reichen
  als Autorenbestätigung nicht aus.
- Kein offizieller ONNX-/DirectML-Pfad. Entwicklungsprobe mit einer Iteration
  funktioniert bei Breiten 832/864; bei 416 und Suchweite 768 scheitert ORT an
  einem Reshape. Volle 16 Iterationen, beliebige gepolsterte Bildgrößen,
  Foto-Parität, Abbruch und Windows-/DirectML-Speicher sind noch zu prüfen.
- Weitere Fotos und vollständige Bewegung statt nur mittlerer Ansicht vergleichen.

## Primärquellen und Identität

- [Offizielles Repository](https://github.com/gangweiX/IGEV-plusplus), Commit
  `099dec97989780d151700459c682df1cc2c18e88`.
- [MIT-Code-Lizenz](https://github.com/gangweiX/IGEV-plusplus/blob/main/LICENSE).
- [Autorenbestätigung zum Download](https://github.com/gangweiX/IGEV-plusplus/issues/2).
- [Offizieller Gewichtsordner](https://drive.google.com/drive/folders/19WA5WeoSQGFxxyzq7ZhJFeptz4zwBNuq).
- Middlebury SHA-256: `eecddfa4549dc6180ce96e7ed8bf24a0bb0d702d5e747623eac54abed1fd7579`.
- SceneFlow SHA-256: `550227fb7b73cbe038149ab2c86884866e68af51db7e438e2485da7da3cff433`.

Quellen, Gewichte und private Fotodiagnostik wurden isoliert untersucht;
keine IGEV++-Quellen, Gewichte oder Nutzerfotos in die Anwendung übernommen.
