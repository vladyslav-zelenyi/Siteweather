from django import template

register = template.Library()

# register.filter('name', name)

# @register.filter(name='name')
#     def name(value, arg):
#         return value.func()
