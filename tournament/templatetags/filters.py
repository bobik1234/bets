import os
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def match_id(value):
    """

    :param value: uzywany glownie przy glosowaniu (vote_form.html) - value (w formularzu field label)
     ma wartosc nazwa kraju i nr meczu, stad funkcja pop()
    :return:
    """
    field_label = value.split(" ")
    return field_label.pop()


@register.filter
@stringfilter
def team_name(value):
    """

    :param value: uzywany glownie przy glosowaniu (vote_form.html) - value (w formularzu field label)
     ma wartosc nazwa kraju i nr meczu. Problemem jest jak nazwa kraju jest kilku czlonowa - kolejne czlony pisane
     sa malymi literami podczas gdy w bazie match.name wszyskie kolejne wyraz sa duzymi literami, Stad uzycie funkcji
        title()
    :return:
    """

    value = value.title()
    field_label = value.split(" ")
    field_label.pop()
    return " ".join(field_label)
