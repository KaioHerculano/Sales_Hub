from io import BytesIO
from decimal import Decimal
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors


def generate_budget_pdf(budget):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin = 50
    y = height - margin

    items = budget.items.all()

    # Colunas reposicionadas
    col1_x = margin + 10              # PRODUTO
    col2_x = margin + 280             # QTD
    col3_x = margin + 350             # PREÇO UNIT.
    col4_x = width - margin - 10      # TOTAL (direita)

    # Cabeçalho principal
    p.setFont("Helvetica-Bold", 22)
    p.setFillColorRGB(0.15, 0.4, 0.7)
    p.drawCentredString(width / 2, y - 20, "SALES HUB")
    p.setFillColorRGB(0, 0, 0)
    y -= 50

    p.setStrokeColorRGB(0.7, 0.7, 0.7)
    p.setLineWidth(1)
    p.line(margin, y, width - margin, y)
    y -= 30

    p.setFont("Helvetica-Bold", 16)
    p.drawString(margin, y, f"ORÇAMENTO Nº {budget.id}")
    y -= 25

    p.setFont("Helvetica", 12)
    p.drawString(margin, y, f"Cliente: {budget.client}")
    y -= 18
    p.drawString(margin, y, f"Data: {budget.sale_date.strftime('%d/%m/%Y')}")
    y -= 35

    # Cabeçalho da tabela
    p.setFillColorRGB(0.9, 0.9, 0.9)
    p.rect(margin, y, width - 2 * margin, 20, fill=True, stroke=False)
    p.setFillColorRGB(0, 0, 0)
    p.setFont("Helvetica-Bold", 11)
    p.drawString(col1_x, y + 5, "PRODUTO")
    p.drawString(col2_x, y + 5, "QTD")
    p.drawString(col3_x, y + 5, "PREÇO UNIT.")
    p.drawRightString(col4_x, y + 5, "TOTAL")
    y -= 25

    # Conteúdo da tabela
    p.setFont("Helvetica", 10)
    total_geral = Decimal("0.00")
    for item in items:
        subtotal_item = item.quantity * item.unit_price
        total_geral += subtotal_item

        p.drawString(col1_x, y, str(item.product.title))
        p.drawRightString(col2_x + 20, y, str(item.quantity))
        p.drawRightString(col3_x + 60, y, f"R$ {item.unit_price:.2f}")
        p.drawRightString(col4_x, y, f"R$ {subtotal_item:.2f}")

        y -= 10  # diminui menos para dar espaço
        p.setStrokeColorRGB(0.9, 0.9, 0.9)
        p.line(margin, y, width - margin, y)
        y -= 15   # desce mais para o próximo item

    # Totais e descontos
    discount = budget.discount or Decimal("0.00")
    discount_amount = total_geral * (discount / Decimal("100.00"))
    total_final = total_geral - discount_amount

    y -= 10
    if discount > 0:
        p.setFont("Helvetica", 10)
        p.drawRightString(col4_x, y, f"Desconto ({discount:.2f}%): -R$ {discount_amount:.2f}")
        y -= 20

    p.setFont("Helvetica-Bold", 12)
    p.drawRightString(col4_x, y, f"TOTAL GERAL: R$ {total_final:.2f}")
    y -= 30

    # Observações
    p.setFont("Helvetica-Oblique", 9)
    p.setFillColorRGB(0.3, 0.3, 0.3)
    p.drawString(margin, y, "Observações: Documento gerado para fins de orçamento.")
    y -= 20

    # Rodapé
    p.setFont("Helvetica", 8)
    p.setFillColor(colors.grey)
    footer_text = "SALES HUB - Sistema de Gestão Comercial | Contato: (65) 9 9999-9999"
    p.drawCentredString(width / 2, 30, footer_text)

    # Finaliza PDF
    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()
    return pdf
