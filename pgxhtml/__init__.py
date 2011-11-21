from plasTeX.Renderers.XHTML import Renderer as BaseRenderer

class pgXHTMLRenderer(BaseRenderer):
    """ Renderer for plain text documents for upload to Project Gutenberg"""
    pass

Renderer = pgXHTMLRenderer
