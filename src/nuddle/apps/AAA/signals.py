from django.apps import apps
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from .models import User


#@receiver(post_migrate)
def create_user_groups(sender, **kwargs):
    if sender.name != 'AAA':
        return
    Group.objects.get_or_create(name='Admin')
    Group.objects.get_or_create(name='Moderator')
    Group.objects.get_or_create(name='Free User')
    Group.objects.get_or_create(name='Plus Subscriber')
    Group.objects.get_or_create(name='Gold Subscriber')
    Group.objects.get_or_create(name='VIP Subscriber')

    print('User groups created or verified.')



def my_callback(sender, **kwargs):
    print('Request Finished')


# @receiver(post_save, sender=User)
def handle_new_user(sender, instance, created, **kwargs):
    if created:
        # Example: Automatically adding new users to the "Free User" group
        free_user_group, _ = Group.objects.get_or_create(name='Free User')
        instance.groups.add(free_user_group)
        print(f'NEW USER CREATED and added to {free_user_group.name}:', instance)


# @receiver(post_save, sender=User)
def assign_admin_group(sender, instance, **kwargs):
    if instance.is_superuser:
        admin_group, _ = Group.objects.get_or_create(name='Admin')
        admin_group.user_set.add(instance)
        print(f'Admin group added to {instance}:', instance)


# @receiver(post_save, sender=User)
def assign_moderator_group(sender, instance, **kwargs):
    if instance.is_staff:
        moderator_group, _ = Group.objects.get_or_create(name='Moderator')
        moderator_group.user_set.add(instance)
        print(f'Moderator group added to {instance}:', instance)


# @receiver(post_save, sender=User)
def update_user(sender, instance, **kwargs):
    # This function no longer checks for 'created' because it's meant to handle updates
    print('USER UPDATED:', instance)
