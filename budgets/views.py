from reportlab.lib.pagesizes import A4
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from sales.models import Budget
from sales import forms
from decimal import Decimal
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from io import BytesIO


class BudgetListView(ListView):
    model = Budget
    template_name = 'budget_list.html'
    context_object_name = 'budgets'

    def get_queryset(self):
        return Budget.objects.exclude(order_status__in=['converted', 'finalized'])

class BudgetPDFView(DetailView):
    model = Budget
    
    def get(self, request, *args, **kwargs):
        budget = self.get_object()
        items = budget.items.all()

        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        margin = 50
        y = height - margin

        p.setFont("Helvetica-Bold", 20)
        p.setFillColorRGB(0.2, 0.5, 0.8)
        p.drawCentredString(width/2, y - 30, "SALES HUB")
        p.setFillColorRGB(0, 0, 0)
        
        p.line(margin, y - 45, width - margin, y - 45)
        
        p.setFont("Helvetica-Bold", 16)
        p.drawString(margin, y - 80, f"ORÇAMENTO #{budget.id}")
        
        p.setFont("Helvetica", 12)
        p.drawString(margin, y - 110, f"Cliente: {budget.client}")
        p.drawString(margin, y - 130, f"Data: {budget.sale_date.strftime('%d/%m/%Y')}")
        y -= 170

        p.setFont("Helvetica-Bold", 12)
        p.setFillColorRGB(0.9, 0.9, 0.9)
        p.rect(margin, y - 10, width - 2*margin, 25, fill=True, stroke=False)
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
        
        discount = budget.discount or Decimal("0.00")
        discount_amount = total_geral * (discount / Decimal("100.00"))
        total_final = total_geral - discount_amount
        
        if discount > 0:
            y -= 15
            p.line(margin, y, width - margin, y)
            y -= 20
            p.setFont("Helvetica", 12)
            p.drawRightString(width - margin - 10, y, f"DESCONTO ({discount:.2f}%): -R$ {discount_amount:.2f}")
            y -= 25
        
        y -= 15
        p.line(margin, y, width - margin, y)
        y -= 20
        p.setFont("Helvetica-Bold", 14)
        p.drawRightString(width - margin - 10, y, f"TOTAL GERAL: R$ {total_final:.2f}")
        p.setFont("Helvetica", 8)
        p.setFillColorRGB(0.5, 0.5, 0.5)
        footer_text = "SALES HUB - Sistema de Gestão Comercial | Contato: (65) 9 9999-9999"
        p.drawCentredString(width/2, 30, footer_text)
        
        p.showPage()
        p.save()
        
        pdf = buffer.getvalue()
        buffer.close()
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="orcamento_{budget.id}.pdf"'
        return response


class BudgetDetailView(DetailView):
    model = Budget
    template_name = 'budget_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.all()
        return context

class BudgetCreateView(CreateView):
    model = Budget
    form_class = forms.BudgetForm
    template_name = 'budget_create.html'
    success_url = reverse_lazy('budget_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = forms.SaleItemFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = forms.SaleItemFormSet(instance=self.object)
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        form.instance.sale_type = 'quote'
        
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            self.object.calculate_total()
            return redirect(self.get_success_url())
        
        return super().form_invalid(form)

class BudgetUpdateView(UpdateView):
    model = Budget
    form_class = forms.BudgetForm
    template_name = 'budget_update.html'
    success_url = reverse_lazy('budget_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.POST:
            context['formset'] = forms.SaleItemFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = forms.SaleItemFormSet(instance=self.object)

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']

        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            self.object.calculate_total()
            return super().form_valid(form)

        return self.form_invalid(form)

class BudgetDeleteView(DeleteView):
    model = Budget
    template_name = 'budget_delete.html'
    success_url = reverse_lazy('budget_list')

class ConvertToOrderView(View):
    def get(self, request, pk):
        budget = get_object_or_404(Budget, pk=pk)
        return render(request, 'budget_convert.html', {'budget': budget})

    def post(self, request, pk):
        budget = get_object_or_404(Budget, pk=pk)
        order = budget.convert_to_order()
        return redirect('order_detail', pk=order.pk)
