import logging

from django.contrib.auth.models import Group
from django.core.signals import got_request_exception
from django.db.models.signals import post_save, pre_delete, m2m_changed
from django.dispatch import receiver

from siteweather.models import CityBlock, CustomUser


logger = logging.getLogger('django')


@receiver(post_save, sender=CityBlock)
def city_block_changes(sender, instance, created, **kwargs):
    if created:
        logger.info(f'City block {instance} has been created')
    else:
        time = instance.timestamp.strftime('%Y-%m-%d (%H:%m)')
        logger.info(f'City block {instance}({instance.pk}), which was created on {time} has been updated')


@receiver(post_save, sender=CustomUser)
def custom_user_changes(sender, instance, created, **kwargs):
    if created:
        logger.info(f'New user {instance} has been created')
    else:
        logger.info(f'User {instance} has been updated')


@receiver(pre_delete, sender=CityBlock)
def city_block_deleted(sender, instance, **kwargs):
    time = instance.timestamp.strftime('%Y-%m-%d (%H:%m)')
    logger.warning(f'City block {instance}({instance.pk}), which was created on {time} is deleting')


@receiver(pre_delete, sender=CustomUser)
def custom_user_delete(sender, instance, **kwargs):
    logger.warning(f'User {instance} (pk={instance.pk}) is deleting')


@receiver(got_request_exception)
def signal_request_exception(request, **kwargs):
    logger.error(request)


@receiver(m2m_changed, sender='siteweather.CustomUser_groups')
def group_interaction(instance, action, pk_set, **kwargs):
    if action == 'pre_add':
        for pk in pk_set:
            user = CustomUser.objects.get(pk=pk)
            group = Group.objects.get(pk=instance.pk)
            permissions = group.permissions.all()
            for permission in permissions:
                user.user_permissions.add(permission.id)
    elif action == 'pre_remove':
        for pk in pk_set:
            user = CustomUser.objects.get(pk=pk)
            group = Group.objects.get(pk=instance.id)
            permissions = group.permissions.all()
            for permission in permissions:
                user.user_permissions.remove(permission.id)
