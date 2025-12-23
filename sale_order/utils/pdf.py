from io import BytesIO
from decimal import Decimal
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def generate_order_pdf(order):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin = 50
    y = height - margin

    items = order.items.all()

    p.setFont("Helvetica-Bold", 20)
    p.setFillColorRGB(0.2, 0.5, 0.8)
    p.drawCentredString(width / 2, y - 30, "SALES HUB")
    p.setFillColorRGB(0, 0, 0)

    p.line(margin, y - 45, width - margin, y - 45)

    p.setFont("Helvetica-Bold", 16)
    p.drawString(margin, y - 80, f"PEDIDO DE VENDA #{order.id}")

    p.setFont("Helvetica", 12)
    p.drawString(margin, y - 110, f"Cliente: {order.client}")
    p.drawString(margin, y - 130, f"Data: {order.sale_date.strftime('%d/%m/%Y')}")
    y -= 170

    p.setFont("Helvetica-Bold", 12)
    p.setFillColorRGB(0.9, 0.9, 0.9)
    p.rect(margin, y - 10, width - 2 * margin, 25, fill=True, stroke=False)
    p.setFillColorRGB(0, 0, 0)
    p.drawString(margin + 10, y, "PRODUTO")
    p.drawString(250, y, "QTD")
    p.drawString(320, y, "PREÇO UNITÁRIO")
    p.drawRightString(width - margin - 10, y, "TOTAL")
    p.setFont("Helvetica", 10)
    y -= 35

    total_geral = Decimal("0.00")
    for item in items:
        subtotal_item = item.quantity * item.unit_price
        total_geral += subtotal_item
        p.drawString(margin + 10, y, str(item.product.title))
        p.drawString(250, y, str(item.quantity))
        p.drawString(320, y, f"R$ {item.unit_price:.2f}")
        p.drawRightString(width - margin - 10, y, f"R$ {subtotal_item:.2f}")
        p.line(margin, y - 10, width - margin, y - 10)
        y -= 25

    discount = order.discount or Decimal("0.00")
    discount_amount = total_geral * (discount / Decimal("100.00"))
    total_final = total_geral - discount_amount

    if discount > 0:
        y -= 15
        p.line(margin, y, width - margin, y)
        y -= 20
        p.setFont("Helvetica", 12)
        p.drawRightString(width - margin - 10, y, f"DESCONTO ({discount:.2f}%): -R$ {discount_amount:.2f}")
        y -= 25

    y -= 10
    p.setFont("Helvetica-Bold", 14)
    p.drawRightString(width - margin - 10, y, f"TOTAL GERAL: R$ {total_final:.2f}")

    y -= 60
    p.line(margin + 100, y, width - margin - 100, y)
    y -= 20
    p.setFont("Helvetica", 12)
    p.drawCentredString(width / 2, y, "Assinatura do Cliente:")

    p.setFont("Helvetica", 8)
    p.setFillColorRGB(0.5, 0.5, 0.5)
    footer_text = "SALES HUB - Sistema de Gestão Comercial | Contato: (65) 9 9999-9999"
    p.drawCentredString(width / 2, 30, footer_text)

    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()
    return pdf
