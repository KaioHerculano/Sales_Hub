from io import BytesIO
from decimal import Decimal
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def generate_invoice_pdf(sale):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin = 30
    y = height - margin

    items = sale.items.all()
    company = sale.company
    client = sale.client

    emitente_nome = company.name
    emitente_cnpj = company.cnpj or "CNPJ não informado"
    emitente_ie = company.ie or "IE não informado"
    emitente_endereco = company.address or "Endereço não informado"
    emitente_email = company.email or "E-mail não informado"

    destinatario_nome = client.name
    destinatario_cpf = client.cpf or "Não informado"
    destinatario_rg = client.rg or "Não informado"
    destinatario_email = client.email or "Não informado"
    destinatario_nascimento = client.formatted_date_of_birth or "Não informado"
    destinatario_endereco = client.address or "Não informado"

    p.setFillColorRGB(0.2, 0.5, 0.8)
    p.rect(margin, y - 40, width - 2*margin, 40, fill=True, stroke=False)
    p.setFillColorRGB(1, 1, 1)
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(width / 2, y - 28, "NOTA FISCAL ELETRÔNICA")
    p.setFillColorRGB(0, 0, 0)
    y -= 50

    p.setFont("Helvetica-Bold", 12)
    p.drawString(margin, y, "Emitente:")
    p.setFont("Helvetica", 10)
    y -= 14
    p.drawString(margin+10, y, emitente_nome)
    y -= 12
    p.drawString(margin+10, y, f"CNPJ: {emitente_cnpj}  |  IE: {emitente_ie}")
    y -= 12
    p.drawString(margin+10, y, f"Endereço: {emitente_endereco}")
    y -= 12
    p.drawString(margin+10, y, f"E-mail: {emitente_email}")
    y -= 25

    p.setFont("Helvetica-Bold", 12)
    p.drawString(margin, y, "Destinatário:")
    p.setFont("Helvetica", 10)
    y -= 14
    p.drawString(margin+10, y, f"Nome: {destinatario_nome}")
    y -= 12
    p.drawString(margin+10, y, f"CPF: {destinatario_cpf}    RG: {destinatario_rg}")
    y -= 12
    p.drawString(margin+10, y, f"E-mail: {destinatario_email}")
    y -= 12
    p.drawString(margin+10, y, f"Data Nasc.: {destinatario_nascimento}")
    y -= 12
    p.drawString(margin+10, y, f"End.: {destinatario_endereco}")
    y -= 25

    p.setFont("Helvetica-Bold", 12)
    p.drawString(margin, y, f"Venda Nº: {sale.id}")
    p.drawRightString(width - margin, y, f"Data: {sale.sale_date.strftime('%d/%m/%Y')}")
    y -= 25

    p.setFillColorRGB(0.9, 0.9, 0.9)
    p.rect(margin, y - 15, width - 2*margin, 20, fill=True, stroke=False)
    p.setFillColorRGB(0, 0, 0)
    p.setFont("Helvetica-Bold", 10)

    p.drawString(margin + 5, y - 10, "PRODUTO")
    p.drawString(margin + 340, y - 10, "QTD")
    p.drawString(margin + 400, y - 10, "VALOR UNIT.")
    p.drawRightString(width - margin - 5, y - 10, "TOTAL")
    y -= 25

    total_geral = Decimal("0.00")
    p.setFont("Helvetica", 10)
    for item in items:
        subtotal_item = item.quantity * item.unit_price
        total_geral += subtotal_item
        y -= 10
        p.drawString(margin + 5, y, str(item.product.title))
        p.drawString(margin + 340, y, str(item.quantity))
        p.drawString(margin + 400, y, f"R$ {item.unit_price:.2f}")
        p.drawRightString(width - margin - 5, y, f"R$ {subtotal_item:.2f}")
        y -= 10
        p.line(margin, y, width - margin, y)
        y -= 10

    discount = sale.discount or Decimal("0.00")
    discount_amount = total_geral * (discount / Decimal("100.00"))
    total_final = total_geral - discount_amount

    if discount > 0:
        y -= 10
        p.setFont("Helvetica", 10)
        p.drawRightString(width - margin - 5, y, f"Desconto ({discount:.2f}%): -R$ {discount_amount:.2f}")
        y -= 10

    p.setFont("Helvetica-Bold", 12)
    y -= 10
    p.drawRightString(width - margin - 5, y, f"TOTAL: R$ {total_final:.2f}")
    y -= 30

    p.setFont("Helvetica", 10)
    p.drawString(margin, y, "Observações: Emissão para fins de demonstração.")
    y -= 35

    p.setFont("Helvetica", 8)
    p.setFillColorRGB(0.5, 0.5, 0.5)
    p.drawCentredString(width / 2, 20, "Empresa XYZ Ltda. - Nota Fiscal Eletrônica (SEM VALIDADE FISCAL) | Contato: (65) 9 9999-9999")

    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()
    return pdf
