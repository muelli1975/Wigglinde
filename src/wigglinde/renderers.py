"""Explicit renderer identities for the isolated 1.2 experiment."""
RENDERERS = ('RVS', 'VWS')
DEFAULT_RENDERER = 'RVS'
RENDERER_LABELS = {'RVS': 'RVS (CPU)', 'VWS': 'VWS (CPU)'}


def renderer_description(name):
    if name not in RENDERERS:
        raise ValueError('Unbekannter Renderer / unknown renderer: ' + str(name))
    return 'RVS CPU Precision 1 Simple 5' if name == 'RVS' else 'TMIV VWS CPU'
