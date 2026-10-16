# Wigglinde

Aus stereoskopischen SBS-Fotos sollen hochwertige Zwischenansichten für
Wiggle-Animationen und Lentikularbilder entstehen. Ziel ist ein kostenlos
nutzbares, portables Windows-Programm, das nach Einrichtung lokal und offline arbeitet.

**Entwicklungsstand:** erster Kommandozeilen-Diagnoseprototyp. Noch keine fertige
Windows-Anwendung und kein Nachweis der angestrebten Fotoqualität.

Der Prototyp kann lokal vorhandene Geometrie verarbeiten, Zwischenansichten als
PNG mit sichtbaren Lücken ausgeben und mit einem lokalen ONNX-Modell verbunden
werden. Die Wiggle-Einstellungen und der Exportkern sind aus SplatTricia übernommen.
Der tatsächliche Modell- und Prüfstand steht in den [Entwicklungsnotizen](docs/DEVELOPMENT.md).

Die geplante Oberfläche bleibt ein schlichter Konverter im Gestaltungsstandard
der anderen Stereo-Tools. Wiggle-Optionen entsprechen SplatTricia.

Eigener Quellcode: [MIT](LICENSE). Modelle und Bibliotheken unter ihren jeweiligen
Lizenzen; Modellgewichte sind nicht Teil dieses Repositorys. Die spätere Anwendung
soll alle benötigten Komponenten lokal mitbringen und keine Downloads auslösen.
