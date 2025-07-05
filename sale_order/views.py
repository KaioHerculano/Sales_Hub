from decimal import Decimal
from io import BytesIO
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from companies.mixins import CompanyObjectMixin
from outflows.models import Outflow
from sales import forms
from sales.models import Sale


class OrderPDFView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, DetailView):
    model = Sale
    permission_required = 'sales.view_order'

    def get_queryset(self):
        return super().get_queryset().filter(company=self.request.user.profile.company)

    def get(self, request, *args, **kwargs):
        order = self.get_object()
        items = order.items.all()

        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        margin = 50
        y = height - margin

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

        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="pedido_venda_{order.id}.pdf"'
        return response


class OrderListView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, ListView):
    model = Sale
    template_name = 'order_list.html'
    context_object_name = 'orders'
    paginate_by = 8
    permission_required = 'sales.view_order'


class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Sale
    form_class = forms.OrderUpdateForm
    template_name = 'order_create.html'
    success_url = reverse_lazy('order_list')
    permission_required = 'sales.add_order'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['items'] = forms.SaleItemFormSet(self.request.POST, prefix="items", user=self.request.user)
        else:
            context['items'] = forms.SaleItemFormSet(prefix="items", user=self.request.user)
        return context
    
    def form_valid(self, form):
        form.instance.company = self.request.user.profile.company
        context = self.get_context_data()
        items = context['items']
        for f in items.forms:
            if not f.has_changed():
                f.empty_permitted = True

        self.object = form.save(commit=False)
        self.object.sale_type = 'order'
        if not self.object.order_status:
            self.object.order_status = 'pending'
        if self.request.user.is_authenticated:
            self.object.cashier = self.request.user
        self.object.save()
        
        if items.is_valid():
            items.instance = self.object
            items.save()

            subtotal = sum(item.unit_price * item.quantity for item in self.object.items.all())
            discount_amount = subtotal * (self.object.discount / Decimal("100.00"))
            total = subtotal - discount_amount
            self.object.total = total.quantize(Decimal("0.01"))
            self.object.save(update_fields=["total"])

            if self.object.order_status == 'finalized':
                for item in self.object.items.all():
                    product = item.product
                    discounted_unit_price = (item.unit_price - (item.unit_price * (self.object.discount / Decimal("100.00")))).quantize(Decimal("0.01"))
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


class OrderDetailView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, DetailView):
    model = Sale
    template_name = 'order_detail.html'
    context_object_name = 'order'
    permission_required = 'sales.view_order'


class OrderUpdateView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, UpdateView):
    model = Sale
    form_class = forms.OrderUpdateForm
    template_name = 'order_update.html'
    success_url = reverse_lazy('order_list')
    permission_required = 'sales.change_order'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        self.previous_status = obj.order_status
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sale = self.get_object()
        if self.request.POST:
            context['items'] = forms.SaleItemFormSet(self.request.POST, instance=sale, prefix="items")
        else:
            context['items'] = forms.SaleItemFormSet(instance=sale, prefix="items")
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        items = context.get('items')
        self.object = form.save(commit=False)
        previously_finalized = (self.previous_status == 'finalized')
        currently_finalized = (self.object.order_status == 'finalized')
        self.object.save()
        
        if items.is_valid():
            items.instance = self.object
            items.save()
            
            subtotal = sum(item.unit_price * item.quantity for item in self.object.items.all())
            discount_amount = subtotal * (self.object.discount / Decimal("100.00"))
            total = subtotal - discount_amount
            self.object.total = total.quantize(Decimal("0.01"))
            self.object.save(update_fields=["total"])
            
            if self.object.order_status == 'finalized':
                for item in self.object.items.all():
                    product = item.product
                    discounted_unit_price = (item.unit_price - (item.unit_price * (self.object.discount / Decimal("100.00")))).quantize(Decimal("0.01"))
                    Outflow.objects.create(
                        product=product,
                        quantity=item.quantity,
                        company=self.request.user.profile.company,
                        sale_reference=f"Venda {self.object.id}",
                        description=f"Venda realizada no PDV (Venda {self.object.id}). Preço unitário com desconto: R$ {discounted_unit_price}"
                    )
            return HttpResponseRedirect(self.get_success_url())
        else:
            print("Formset errors:", items.errors)
            return self.form_invalid(form)
