import logging

from django.core.mail import send_mail
from django.utils.timezone import localtime

from siteweather.models import CustomUser
from task.celery import app


logger = logging.getLogger('django')


@app.task(name='base_tasks.add')
def add(x, y):
    return x + y


@app.task(name='base_tasks.mul')
def mul(x, y):
    return x * y


@app.task(name='base_tasks.general_sum')
def general_sum(numbers):
    return sum(numbers)


@app.task(name='base_tasks.test_task')
def test_task(arg):
    return logger.info(f'{arg} (beat)')


@app.task(name='base_tasks.inactive_users_check')
def inactive_users_check():
    users = CustomUser.objects.filter(is_active=True)
    today = localtime()
    for user in users:
        if not user.last_login:
            days_not_active = (today - user.date_joined).days
        else:
            days_not_active = (today-user.last_login).days
        if days_not_active > 30:
            user.is_active = False
            user.save()
            logger.info(f"User's {user} status has been changed to not active")
    logger.info(f"All users were checked for inactivity at {today}")


@app.task(name='base_tasks.delete_inactive_users')
def delete_inactive_users():
    users = CustomUser.objects.filter(is_active=False)
    today = localtime()
    for user in users:
        if not user.last_login:
            days_not_active = (today - user.date_joined).days
        else:
            days_not_active = (today-user.last_login).days
        if days_not_active > 60:
            user.delete()


@app.task(name='base_tasks.send_warning_to_inactive_users')
def send_warning_to_inactive_users():
    users = CustomUser.objects.filter(is_active=True)
    today = localtime()
    for user in users:
        days_not_active = (today - user.date_joined).days
        if days_not_active > 14:
            send_mail(
                subject='Inactivity on the siteweather (TEST)',
                from_email='Siteweather',
                message=f"Dear {user.first_name}, you have been inactive for two weeks. Please notice, "
                        f"that your account will be marked as inactive after 30 days.\n"
                        f"You will be unable to work with the site with this account. All you need to do is to log in.",
                recipient_list=[user.email]
            )
            logger.info(f"User {user} has been notified about his inactivity.")
