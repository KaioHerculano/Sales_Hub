from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from companies.mixins import CompanyObjectMixin
from sales import forms
from sales.models import Budget
from .utils.pdf import generate_budget_pdf


class BudgetListView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, ListView):
    model = Budget
    template_name = 'budget_list.html'
    context_object_name = 'budgets'
    permission_required = 'sales.view_budget'

    def get_queryset(self):
        return Budget.objects.exclude(order_status__in=['converted', 'finalized']).filter(company=self.request.user.profile.company)

class BudgetPDFView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, DetailView):
    model = Budget
    permission_required = 'sales.view_budget'

    def get(self, request, *args, **kwargs):
        budget = self.get_object()
        pdf = generate_budget_pdf(budget)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="orcamento_{budget.id}.pdf"'
        return response


class BudgetDetailView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, DetailView):
    model = Budget
    template_name = 'budget_detail.html'
    permission_required = 'sales.view_budget'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.all()
        return context

class BudgetCreateView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, CreateView):
    model = Budget
    form_class = forms.BudgetForm
    template_name = 'budget_create.html'
    success_url = reverse_lazy('budget_list')
    permission_required = 'sales.add_budget'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = forms.SaleItemFormSet(self.request.POST, instance=self.object, user=self.request.user)
        else:
            context['formset'] = forms.SaleItemFormSet(instance=self.object, user=self.request.user)
        return context
    
    def form_valid(self, form):
        form.instance.company = self.request.user.profile.company
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

class BudgetUpdateView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, UpdateView):
    model = Budget
    form_class = forms.BudgetForm
    template_name = 'budget_update.html'
    success_url = reverse_lazy('budget_list')
    permission_required = 'sales.change_budget'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.POST:
            context['formset'] = forms.SaleItemFormSet(self.request.POST, instance=self.object, user=self.request.user)
        else:
            context['formset'] = forms.SaleItemFormSet(instance=self.object, user=self.request.user)

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

class BudgetDeleteView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, DeleteView):
    model = Budget
    template_name = 'budget_delete.html'
    success_url = reverse_lazy('budget_list')
    permission_required = 'sales.delete_budget'

class ConvertToOrderView(View):

    def get_queryset(self):
        return super().get_queryset().filter(company=self.request.user.profile.company)
    
    def get(self, request, pk):
        budget = get_object_or_404(Budget, pk=pk)
        return render(request, 'budget_convert.html', {'budget': budget})

    def post(self, request, pk):
        budget = get_object_or_404(Budget, pk=pk)
        order = budget.convert_to_order()
        return redirect('order_detail', pk=order.pk)
