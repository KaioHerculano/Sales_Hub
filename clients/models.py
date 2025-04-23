import re
from django.db import models
from django.core.exceptions import ValidationError
from companies.models import Company

def validate_phone(value):
    numbers = re.sub(r'\D', '', value)
    if len(numbers) != 11:
        raise ValidationError("Número deve ter 11 dígitos (ex: 65999999999).")


def validate_cpf(value):
    numbers = re.sub(r'\D', '', value)

    if len(numbers) != 11:
        raise ValidationError("CPF deve ter 11 dígitos.")

    if len(set(numbers)) == 1:
        raise ValidationError("CPF inválido.")

    def digit_calculation(digits, peso_inicial):
        sum_total = 0
        for i, num in enumerate(digits):
            sum_total += int(num) * (peso_inicial - i)
        resto = sum_total % 11
        return '0' if resto < 2 else str(11 - resto)

    first_digit = digit_calculation(numbers[:9], 10)
    second_digit = digit_calculation(numbers[:10], 11)

    if numbers[-2:] != first_digit + second_digit:
        raise ValidationError("CPF inválido (dígitos verificadores incorretos).")


def validate_rg(value):
    numbers = re.sub(r'\D', '', value)
    if len(numbers) not in (7, 8):
        raise ValidationError("RG deve conter 7 ou 8 dígitos numéricos (ex: 1234567 ou 12345678).")


class Client(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    neighborhood = models.CharField(max_length=50, blank=True, null=True)
    complement = models.TextField(blank=True, null=True)
    telephone = models.CharField(max_length=17, validators=[validate_phone])
    email = models.EmailField(max_length=254, blank=True, null=True)
    cpf = models.CharField(max_length=14, blank=True, null=True, validators=[validate_cpf], unique=True)
    rg = models.CharField(max_length=9, blank=True, null=True, validators=[validate_rg], unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def formatted_date_of_birth(self):
        if self.date_of_birth:
            return self.date_of_birth.strftime("%d/%m/%Y")
        return ""

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.telephone:
            numbers = re.sub(r'\D', '', self.telephone)

            if len(numbers) == 11:
                self.telephone = f'({numbers[:2]}) {numbers[2:7]}-{numbers[7:]}'
            else:
                raise ValidationError("Número inválido! Deve conter 11 dígitos.")

        if self.cpf:
            cpf_numbers = re.sub(r'\D', '', self.cpf)
            if len(cpf_numbers) == 11:
                self.cpf = f"{cpf_numbers[:3]}.{cpf_numbers[3:6]}.{cpf_numbers[6:9]}-{cpf_numbers[9:]}"
            else:
                raise ValidationError("CPF inválido!")

        if self.rg:
            numbers = re.sub(r'\D', '', self.rg)
            if len(numbers) not in (7, 8):
                raise ValidationError("RG inválido! Deve conter 7 ou 8 dígitos.")
            if len(numbers) == 8:
                self.rg = f"{numbers[:7]}-{numbers[7:]}"
            else:  # 7 dígitos
                self.rg = f"{numbers[:6]}-{numbers[6:]}"

        super().save(*args, **kwargs)
