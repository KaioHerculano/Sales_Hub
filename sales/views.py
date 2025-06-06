from app import metrics
from django.db.models import Q
from rest_framework import generics
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, CreateView, DetailView
from products.models import Product
from outflows.models import Outflow
from clients.models import Client
from django.http import JsonResponse
from django.views import View
from decimal import Decimal
from . import models, forms, serializers
from io import BytesIO
from decimal import Decimal
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.views.generic import DetailView
from .models import Sale
from django.core.exceptions import PermissionDenied


class CompanyObjectMixin:
    """Garante que objetos pertençam à company do usuário."""
    def get_queryset(self):
        queryset = super().get_queryset()
        if hasattr(self.request.user, 'profile'):
            return queryset.filter(company=self.request.user.profile.company)
        raise PermissionDenied("Usuário não associado a uma company.")

class InvoicePDFView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, DetailView):
    model = Sale
    permission_required = 'sales.view_sale'

    def get(self, request, *args, **kwargs):
        sale = self.get_object()
        items = sale.items.all()

        company = request.user.profile.company

        emitente_nome = company.name
        emitente_cnpj = company.cnpj or "CNPJ não informado"
        emitente_ie = company.ie or "IE não informado"
        emitente_endereco = company.address or "Endereço não informado"
        emitente_email = company.email or "E-mail não informado"

        client = sale.client
        destinatario_nome = client.name
        destinatario_cpf = client.cpf or "Não informado"
        destinatario_rg = client.rg or "Não informado"
        destinatario_email = client.email or "Não informado"
        destinatario_nascimento = client.formatted_date_of_birth or "Não informado"
        destinatario_endereco = client.address or "Não informado"
        
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        margin = 30
        
        y = height - margin

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
        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="nota_fiscal_{sale.id}.pdf"'
        return response



class GetProductPriceView(View):
    def get(self, request):
        product_id = request.GET.get("product_id")
        try:
            product = Product.objects.get(pk=product_id)
            return JsonResponse({'price': str(product.selling_price)})
        except Product.DoesNotExist:
            return JsonResponse({'price': ''})


class SaleCreateView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, CreateView):
    model = Sale
    form_class = forms.SaleForm
    template_name = 'sale_create.html'
    success_url = reverse_lazy('sale_list')
    permission_required = 'sales.add_sale'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['items'] = forms.SaleItemFormSet(self.request.POST, user=self.request.user)
        else:
            context['items'] = forms.SaleItemFormSet(user=self.request.user)
        return context

    def form_valid(self, form):
        form.instance.company = self.request.user.profile.company
        context = self.get_context_data()
        items = context['items']
        for f in items.forms:
            if not f.has_changed():
                f.empty_permitted = True

        self.object = form.save(commit=False)
        if not self.object.cashier and self.request.user.is_authenticated:
            self.object.cashier = self.request.user
        self.object.save()

        if items.is_valid():
            items.instance = self.object
            items.save()

            subtotal = sum(item.unit_price * item.quantity for item in self.object.items.all())
            discount_factor = (Decimal("100.00") - self.object.discount) / Decimal("100.00")
            total = subtotal * discount_factor
            self.object.total = total.quantize(Decimal("0.01"))
            self.object.save(update_fields=["total"])

            if self.object.order_status == 'finalized':
                for item in self.object.items.all():
                    product = item.product
                    discounted_unit_price = (item.unit_price * discount_factor).quantize(Decimal("0.01"))
                    Outflow.objects.create(
                        product=product,
                        quantity=item.quantity,
                        company=self.request.user.profile.company,
                        sale_reference=f"Venda {self.object.id}",
                        description=f"Venda realizada no PDV (Venda {self.object.id}). Preço unitário com desconto: R$ {discounted_unit_price}"
                    )
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(self.get_success_url())
        else:
            print(items.errors)
            return self.form_invalid(form)



class SaleListView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, ListView):
    model = models.Sale
    template_name = 'sale_list.html'
    context_object_name = 'sales'
    paginate_by = 8
    permission_required = 'sales.view_sale'

    def get_queryset(self):
        queryset = super().get_queryset().filter(company=self.request.user.profile.company)
        client_id = self.request.GET.get("client")
        if client_id:
            queryset = queryset.filter(client__id=client_id)
        queryset = queryset.filter(
            Q(sale_type='quote') | 
            (Q(sale_type='order') & Q(order_status='finalized'))
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self.request.user.profile.company
        context['clients'] = Client.objects.filter(company=company)
        context['sales_metrics'] = metrics.get_sales_metrics(company) 
        return context


class SaleDetailView(LoginRequiredMixin, CompanyObjectMixin, DetailView):
    model = models.Sale
    template_name = "sale_detail.html"
    context_object_name = "sale"
    permission_required = 'sales.view_sale'

    def get_queryset(self):
        return super().get_queryset().filter(company=self.request.user.profile.company)


class SaleCreateListAPIView(generics.ListCreateAPIView):
    queryset = models.Sale.objects.all()
    serializer_class = serializers.SaleSerializer

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_queryset(self):
        return super().get_queryset().filter(company=self.request.user.profile.company)

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.profile.company)


class SaleRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Sale.objects.all()
    serializer_class = serializers.SaleSerializer

    def get_queryset(self):
        return models.Brand.objects.filter(company=self.request.user.profile.company)
