import logging
import os
from celery import Celery
from celery import signals

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'task.settings')
app = Celery('task')

app.config_from_object('django.conf:settings')

app.autodiscover_tasks()


@signals.setup_logging.connect
def on_celery_setup_logging(**kwargs):
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '{levelname} | CELERY | {asctime} | {module} | {message}',
                'style': '{',
            },
            'colored': {
                '()': 'colorlog.ColoredFormatter',
                'format': '{log_color}{levelname} | CELERY | {asctime} | {module} | {message}',
                'style': '{',
            }
        },
        'handlers': {
            'celery': {
                'level': 'INFO',
                'class': 'logging.FileHandler',
                'filename': '/home/vladyslav/PycharmProjects/task/siteweather/celery.log',
                'formatter': 'default'
            },
            'console': {
                'level': 'INFO',
                'class': 'colorlog.StreamHandler',
                'formatter': 'colored'
            }
        },
        'loggers': {
            'celery': {
                'handlers': ['celery', 'console'],
                'level': 'INFO',
                'propagate': False
            },
        }
    }

    logging.config.dictConfig(config)
