import pytest
from model_bakery import baker
from brands.models import Brand

@pytest.mark.django_db
def test_brand_str():
    brand = baker.make(Brand, name="Nike")
    assert str(brand) == "Nike"

@pytest.mark.django_db
def test_brand_ordering():
    # Meta ordering is ['name']
    brand_b = baker.make(Brand, name="B")
    brand_a = baker.make(Brand, name="A")
    
    brands = Brand.objects.all()
    assert list(brands) == [brand_a, brand_b]
