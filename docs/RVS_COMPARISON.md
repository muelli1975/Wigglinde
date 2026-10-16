# RVS: Ein-Bild-Vergleich am 16. Oktober 2026

## Ergebnis und Entscheidung

RVS ist als CPU-Spezialrenderer ausführbar und lässt sich ohne Justage an unsere
montierte Stereo-Geometrie anbinden. In der geprüften Konfiguration beruhigt es
die zuvor nachgewiesenen abrupten Kantenwechsel, macht das Bild aber sichtbar
weicher und verändert die beiden Endansichten. Deshalb **kein direkter Wechsel
des Produkt-Renderers** aufgrund dieses Versuchs. Die NumPy-Implementierung bleibt
eine Diagnosebasis mit bekanntem Verdeckungsfehler, ebenfalls kein fertiger Renderer.

Der nächste fachliche Entscheidungspunkt ist die Originaltreue an den Endpositionen
und die Konturschärfe. RVS mit Original-Endansichten zu kombinieren wäre in der
geprüften Form unzureichend: Der Übergang zu den anders berechneten Innenansichten
würde erneut sichtbare Sprünge erzeugen. Keine weitere Modellsuche oder GUI-Arbeit
ist nötig, um diese Rendererfrage zu klären.

## Tatsächlich ausgeführt

- Ein bereitgestelltes Straßenmotiv, bild032_cs.jpg; 960×640 pro Halbbild.
  Verwendet wurden die bereits gesicherten, farbverwalteten Vorschau-Endansichten.
  Keine weitere Verkleinerung, kein Beschnitt, keine Änderung der Scheinfensterlage.
- Nach Zurücksetzen der temporären Arbeitsumgebung fehlten die lokal gespeicherten
  Disparitäten und der unveröffentlichte LAS2-ONNX-Adapter. Daher Neuberechnung
  mit demselben gehashten LAS2-M-Checkpoint und gepinntem nativen FP32-Modell,
  internem Suchversatz 64 und Rückrechnung; Rückrichtung durch Tauschen UND Spiegeln.
  Native Inferenz: 6,00 / 2,57 s; keine Leistungsbewertung gegenüber den früheren
  ONNX-Zeiten, da Implementierung/Laufzeit verschieden sind.
- Kontrollierte mittlere Ansicht gegenüber gesichertem früherem ONNX-Ergebnis:
  mittlere absolute RGB-Differenz 0,00006348 auf 0..255, maximal 3; nur 2 von
  614400 Pixeln hatten eine Kanalabweichung größer 1. Die Karten selbst sind nach
  Verlust des ursprünglichen Caches nicht mehr direkt vergleichbar.
- Beide Vergleichsrenderer nutzen exakt dieselbe neue `scene.npz`.
- RVS `d757a353c7f84d228ac30c179d6ff9de356c6101`, unveränderte CPU-Klassen.
  Ein dünner Adapter stellt Float32-Farben/Tiefen im Speicher bereit, ruft
  SynthesizedView/BlendedView/inpaint auf und schreibt rohe Ergebnisse.
  Kein Ersatz der Rasterung oder Blending-Mathematik durch eigenen Code.
- RVS Precision 2: 1920×1280 interne Rasterung, Ausgabe wieder 960×640;
  Multispectral-Blending mit niedrigen/hohen Exponenten 1/4. Originale RVS-Füllung.
  Beide Renderer arbeiten mit denselben linearen sRGB-Farben.
- Virtuelle Kameras bilden einschließlich negativer Disparitäten dieselben
  Verschiebungen wie unser Renderer ab. Mit RVS-Projektionsklassen über alle
  Bildpunkte/Positionen geprüft: maximal 0,000166 px Abweichung.
- 31 verschiedene Blickpositionen; Rückweg nutzt identische Frames. Beide MP4s:
  fünf sinusförmige Zwei-Sekunden-Zyklen, 30 fps, 300 Frames, CRF18/slow,
  sRGB→Rec.709. Vollständig dekodiert und Abmessungen/Framezahl geprüft.
- Im Vergleich links bisheriger Renderer, rechts RVS. Der rechte Clip verwendet
  RVS' selbst gerenderte Endansichten; sie werden ausdrücklich nicht durch die
  Originale ersetzt. Keine zusätzliche zeitliche Glättung oder Überblendung.

## Ressourcen

Linux, 8 CPU-Threads; getrennte Rendererprozesse. Einzelmessung, keine Zusage für
andere Rechner oder vollständige Produktlaufzeiten. Modelle werden hier nicht geladen.

| 31 Ansichten | Zeit | Prozess-Spitzenbedarf |
| --- | --- | --- |
| NumPy-Diagnose-Renderer | 29,99 s reine Renderzeit | 72,95 MiB |
| RVS CPU, Precision 2, Multispectral | 71,91 s | 381,74 MiB |

RVS-Zeit enthält Adapter-Projektionsprüfung und rohe Ausgabedateien; NumPy-Zeit
schließt PNG-Speicherung aus. Der Vergleich ist deshalb kein exakter Benchmark des
reinen Rasterkerns. Modellinferenz, Entwicklungs-Build und MP4-Kodierung sind in
beiden Zeilen ausgeschlossen.

## Konturdiagnose und Grenzen

Eine Positionsänderung 0→0,000001 bewegt die Geometrie höchstens 0,0000271 px.
Der bisherige Renderer produziert dabei schon große Farbsprünge; RVS ändert in
derselben Probe seine eigene Ausgabe um höchstens eine RGB-Stufe. Dieser Befund
belegt die bessere Stetigkeit an dieser Position, keine allgemeine Fehlerfreiheit.
Ein separater Versuch mit analytisch perfekter Vorder-/Hintergrund-Geometrie hatte
den harten Sprung des bisherigen Renderers bereits unabhängig von LAS2 belegt.

RVS' Endansichten weichen jedoch sichtbar von den Quellbildern ab. Auch Precision 1
behebt diese Abweichung nicht vollständig (Probe ohne weiteren Clip). Die weichere
Darstellung und Bildverschmelzung dürfen nicht als reine Qualitätsverbesserung
bezeichnet werden. Ein einzelnes Foto belegt weder allgemeine Fotoqualität noch
die Lösung schwieriger Verdeckungen, Glas, Spiegelungen oder dünner Strukturen.

Keine Windows-, GPU-, Originalauflösungs- oder portable Paketprüfung. RVS' BSD-Lizenz
enthält einen Vorbehalt zu Patent-/Drittrechten; keine pauschale Patentfreigabe behauptet.
Die Originalquellen und Abhängigkeiten behalten ihre jeweiligen Lizenztexte.

## Fortsetzen ohne erneute Diskussion

1. Gesichertes Vergleichspaket mit `scene.npz`, Clips, mittlerer Ansicht und
   `Messwerte.json` verwenden; LAS2 nicht erneut rechnen, solange die Szene vorhanden ist.
2. Forschungsanbindung unter `tools/rvs/`; dort stehen gepinnte Quellen,
   Checkpoint-Hash, Umrechnungsformel und Reproduktionsbefehle.
3. Der vorhandene Produktcode wurde nicht auf RVS umgestellt. Vor jeder Übernahme
   Originaltreue und die sichtbare Glättung gemeinsam beurteilen.
