# reportes/renderers.py
from rest_framework.renderers import BaseRenderer

class PDFRenderer(BaseRenderer):
    media_type = "application/pdf"
    format = "pdf"
    charset = None  # binario
    render_style = "binary"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        # data debe ser bytes
        return data

class XLSXRenderer(BaseRenderer):
    media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    format = "xlsx"
    charset = None  # binario
    render_style = "binary"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        # data debe ser bytes
        return data
