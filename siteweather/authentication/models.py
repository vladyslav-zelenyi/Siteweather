from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.html import format_html


class CustomUser(AbstractUser):
    photo = models.ImageField(null=True, blank=True, upload_to='users/%Y/%m/%d')
    phone_number = models.CharField(verbose_name='Phone number', max_length=15, blank=True)
    user_city = models.CharField(verbose_name='City', max_length=50, blank=True)

    STANDARD = 'Standard'
    PREMIUM = 'Premium'

    ROLE_CHOICES = (
        (STANDARD, 'Standard'),
        (PREMIUM, 'Premium'),
    )

    role = models.CharField(max_length=100, choices=ROLE_CHOICES, default=STANDARD, verbose_name='Role')

    def colored_premium(self):
        if self.role == 'Premium':
            return format_html(f'<span style="color: #FFBD1B;"><strong>{self.role}</strong></span>')
        else:
            return self.role

    colored_premium.short_description = 'Role'

    def get_absolute_url(self):
        return reverse('weather:profile', kwargs={'pk': self.pk})

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['username']