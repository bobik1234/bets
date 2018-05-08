import os
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def match_id(value):
    return value.split(" ")[1]


@register.filter
@stringfilter
def team_name(value):
    return value.split(" ")[0]
