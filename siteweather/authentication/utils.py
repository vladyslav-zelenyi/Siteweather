from rest_framework import serializers


def username_validator(username):
    if len(username) < 4:
        raise serializers.ValidationError('Your username has to contain at least 4 symbols')
    return username
