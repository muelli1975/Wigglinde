"""German and English UI text; paths, format identifiers and logs stay unchanged."""
import re

TEXT = {
    'version': ('Vulkan-Test', 'Vulkan test'),
    'save_depth': ('Tiefenkarten zusätzlich speichern', 'Also save depth maps'),
    'diagnose': ('Tiefenberechnung testen', 'Test depth estimation'),
    'diagnosed': ('Tiefentest abgeschlossen.', 'Depth test completed.'),
    'diagnosis_result': ('Tiefentest: {model} · {device}\nBildgröße: {size}\nModell laden: {load} s\nTiefenberechnung: {depth} s\nGemessene RAM-Spitze (Programm): {ram}\nGemessene lokale GPU-Speicherspitze (Programm): {gpu}\n\nVollständiger Bericht: logs/latest_run.json',
                         'Depth test: {model} · {device}\nImage size: {size}\nModel loading: {load} s\nDepth estimation: {depth} s\nSampled peak RAM (application): {ram}\nSampled peak local GPU memory (application): {gpu}\n\nFull report: logs/latest_run.json'),
    'single': ('Einzelbild', 'Single image'),
    'folder': ('Bildordner', 'Image folder'),
    'choose': ('Auswählen', 'Choose'),
    'standard': ('Unterordner im Eingabeordner verwenden', 'Use subfolder in input folder'),
    'own': ('Eigener Ausgabeordner', 'Custom output folder'),
    'target': ('Ausgabeziel: {path}', 'Output destination: {path}'),
    'after_input': ('Nach der Eingabeauswahl', 'After selecting the input'),
    'format': ('Format', 'Format'),
    'png': ('PNG-Bildfolge', 'PNG sequence'),
    'size': ('Größe', 'Size'),
    'height': ('px Höhe', 'px height'),
    'long_side': ('px lange Seite', 'px long side'),
    'duration': ('Zyklusdauer (s)', 'Cycle duration (s)'),
    'cycles': ('Anzahl der Zyklen', 'Number of cycles'),
    'model': ('Modell', 'Model'),
    'unavailable': ('nicht verfügbar', 'unavailable'),
    'device': ('Berechnung', 'Compute'),
    'worker_failed': ('Die Berechnung wurde unerwartet beendet (Exit {code}).', 'Processing ended unexpectedly (exit {code}).'),
    'render_method': ('Renderer', 'Renderer'),
    'ready': ('Bereit.', 'Ready.'),
    'start': ('Start', 'Start'),
    'cancel': ('Abbrechen', 'Cancel'),
    'file_dialog': ('SBS-Bild auswählen', 'Choose SBS image'),
    'folder_dialog': ('Eingabeordner auswählen', 'Choose input folder'),
    'output_dialog': ('Ausgabeordner auswählen', 'Choose output folder'),
    'images': ('Bilder', 'Images'),
    'choose_output': ('Bitte einen eigenen Ausgabeordner auswählen.', 'Please choose a custom output folder.'),
    'choose_input': ('Bitte ein Einzelbild oder einen Bildordner auswählen.', 'Please choose a single image or an image folder.'),
    'bad_file': ('Die Eingabedatei fehlt oder ist kein unterstütztes Bild.', 'The input file is missing or is not a supported image.'),
    'bad_folder': ('Der Eingabeordner ist nicht vorhanden.', 'The input folder does not exist.'),
    'empty': ('Keine unterstützten Bilder im Eingabeordner gefunden.', 'No supported images found in the input folder.'),
    'selected': ('{count} Bild(er) ausgewählt.', '{count} image(s) selected.'),
    'starting': ('Verarbeitung startet …', 'Starting processing …'),
    'cancelling': ('Abbruch wird ausgeführt …', 'Cancelling …'),
    'finished': ('Fertig: {count} Ausgaben', 'Finished: {count} outputs'),
    'cancelled': ('Abgebrochen: {count} Ausgaben', 'Cancelled: {count} outputs'),
    'errors': (' · {count} Fehler', ' · {count} errors'),
    'details': ('Details: logs/latest_run.json und logs/errors.log', 'Details: logs/latest_run.json and logs/errors.log'),
    'elapsed': ('Verstrichen: {minutes:02d}:{seconds:02d}', 'Elapsed: {minutes:02d}:{seconds:02d}'),
    'numbers': ('Bitte gültige Zahlen für Größe, Bildrate und Zyklusdauer eingeben.', 'Please enter valid numbers for size, frame rate and cycle duration.'),
    'memory': ('Der Arbeitsspeicher oder Grafikspeicher reicht für diese Berechnungsgröße nicht aus. Bitte eine kleinere Größe wählen.', 'There is not enough RAM or GPU memory for this processing size. Please choose a smaller size.'),
    'gpu_failed': ('Die gewählte Grafikkarte konnte nicht verwendet werden. Bitte Treiber prüfen oder CPU wählen. Details: {error}', 'The selected GPU could not be used. Please check the driver or select CPU. Details: {error}'),
}

# The pipeline also remains usable from development tools without a UI locale.
MESSAGES = {
    'Tiefenkarten speichern': 'Saving depth maps',
    'Bild vorbereiten': 'Preparing image',
    'Tiefenkarte links berechnen': 'Estimating left depth map',
    'Tiefenkarte rechts berechnen': 'Estimating right depth map', 'Fertig': 'Finished',
    'Wigglinde benötigt deckende RGB-/Graustufenbilder mit 8 Bit pro Kanal.': 'Wigglinde requires opaque RGB/grayscale images with 8 bits per channel.',
    'Das SBS-Bild muss zwei gleich breite Halbbilder enthalten.': 'The SBS image must contain two equally wide half images.',
    'Die LAS2-Modelldatei ist beschädigt. Bitte das Programmpaket erneut entpacken.': 'The LAS2 model file is damaged. Please extract the application package again.',
    'MP4: 720, 1080 oder 2160 Pixel Bildhöhe wählen.': 'MP4: choose a height of 720, 1080 or 2160 pixels.',
    'PNG: 1080 oder 2160 Pixel Bildhöhe wählen.': 'PNG: choose a height of 1080 or 2160 pixels.',
    'GIF: Lange Bildseite von 64 bis 2160 Pixeln wählen.': 'GIF: choose a long side between 64 and 2160 pixels.',
}

def tr(locale, key, **values):
    return TEXT[key][1 if locale == 'en' else 0].format(**values)

def message(locale, text):
    if locale != 'en':
        return text.split(' / ', 1)[0] if ' / ' in text else text
    if text in MESSAGES:
        return MESSAGES[text]
    if ' / ' in text:
        return text.split(' / ', 1)[1]
    for prefix, translation in [('Die Modelldatei fehlt: ', 'The model file is missing: '), ('Der RVS-Renderer fehlt: ', 'The RVS renderer is missing: ')]:
        if text.startswith(prefix):return translation + text[len(prefix):]
    if re.fullmatch(r'LAS2-[MLH] laden',text):return 'Loading '+text.split()[0]
    if text.startswith('Zwischenansicht '):return 'Rendering view ' + text[len('Zwischenansicht '):]
    if re.fullmatch(r'(MP4|GIF|PNG) speichern', text):return 'Saving ' + text.split()[0]
    return text
