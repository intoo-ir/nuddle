from django.apps import AppConfig
from django.core.signals import request_finished
from django.db.models.signals import post_save, post_migrate


class AaaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'nuddle.apps.AAA'

    def ready(self):
        from . import signals
        from . import models
        request_finished.connect(signals.my_callback)
        post_save.connect(signals.handle_new_user, sender=models.User)
        post_save.connect(signals.update_user, sender=models.User)
        post_save.connect(signals.assign_moderator_group, sender=models.User)
        post_save.connect(signals.assign_admin_group, sender=models.User)
        post_migrate.connect(signals.create_user_groups, sender=self)

