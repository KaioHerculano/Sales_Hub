# Generated by Django 5.1.6 on 2025-04-05 02:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0005_alter_budget_options_alter_order_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='budget_status',
            field=models.CharField(blank=True, choices=[('draft', 'Rascunho'), ('pending', 'Pendente'), ('waiting', 'Aguardando pagamento'), ('canceled', 'Cancelado'), ('approved', 'Aprovado'), ('rejected', 'Rejeitado')], default='draft', max_length=20, null=True, verbose_name='Status'),
        ),
    ]
