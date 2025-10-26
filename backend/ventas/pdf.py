import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors

def generar_comprobante_pdf(venta):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Título
    c.setFont("Helvetica-Bold", 16)
    c.drawString(inch, height - inch, "Comprobante de Venta")

    # Información de la empresa (puedes personalizarla)
    c.setFont("Helvetica", 10)
    c.drawString(inch, height - 1.3 * inch, "SmartSales365")
    c.drawString(inch, height - 1.5 * inch, "Calle Ficticia 123, La Paz, Bolivia")

    # Línea divisoria
    c.line(inch, height - 1.7 * inch, width - inch, height - 1.7 * inch)

    # Datos de la Venta y Cliente
    c.setFont("Helvetica-Bold", 12)
    c.drawString(inch, height - 2.0 * inch, f"Folio: {venta.folio}")
    c.drawString(width / 2, height - 2.0 * inch, f"Fecha: {venta.creado_en.strftime('%d/%m/%Y %H:%M')}")

    c.setFont("Helvetica", 11)
    cliente = venta.cliente
    c.drawString(inch, height - 2.3 * inch, f"Cliente: {cliente.nombre}")
    if cliente.documento:
        c.drawString(inch, height - 2.5 * inch, f"Documento (CI/NIT): {cliente.documento}")
    if cliente.email:
        c.drawString(width / 2, height - 2.3 * inch, f"Email: {cliente.email}")

    # Tabla de Items
    styles = getSampleStyleSheet()
    style_body = styles['BodyText']
    style_body.fontSize = 10

    data = [
        [Paragraph("<b>Cant.</b>", style_body), Paragraph("<b>Producto</b>", style_body), Paragraph("<b>P.U.</b>", style_body), Paragraph("<b>Subtotal</b>", style_body)],
    ]

    for item in venta.items.all():
        data.append([
            item.cantidad,
            Paragraph(item.producto.nombre, style_body),
            f"Bs. {item.precio_unit:.2f}",
            f"Bs. {item.subtotal:.2f}"
        ])

    # Fila del Total
    data.append(['', '', Paragraph("<b>TOTAL</b>", style_body), Paragraph(f"<b>Bs. {venta.total:.2f}</b>", style_body)])

    table = Table(data, colWidths=[0.5 * inch, 4 * inch, 1 * inch, 1.2 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (1, 1), (1, -1), 'LEFT'), # Alinear nombre de producto a la izquierda
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('GRID', (0, 0), (-1, -2), 1, colors.black),
        # Estilos para la fila del total
        ('GRID', (2, -1), (-1, -1), 1, colors.black),
        ('BACKGROUND', (2, -1), (-1, -1), colors.lightgrey),
    ]))

    table.wrapOn(c, width, height)
    table.drawOn(c, inch, height - 2.8 * inch - len(data) * 0.25 * inch)

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer