from django.apps import AppConfig


class StockMovimentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stockmoviment'

    def ready(self):
        import stockmoviment.signals