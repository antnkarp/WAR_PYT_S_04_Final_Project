from django import template

register = template.Library()

@register.filter
def lookup(dict, key):
    return dict[key]

@register.filter
def sort(dict):
    return sorted(dict)

@register.filter
def tuple_lookup(dict, key):
    key_list = key.split(',')
    return dict[(int(key_list[0]), int(key_list[1]))]

@register.filter
def add_str(str1, str2):
    return str(str1) + str(str2)