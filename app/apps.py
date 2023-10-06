from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'
    verbose_name = 'Quản lý'

    def ready(self):
        import app.system_tasks
        app.system_tasks.start()
