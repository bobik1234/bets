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
        title().
        Drugi problem to niektore kraje maja slowko "and" ktore musi byc z malej stad replace. Slowka sa problematyczne.
    :return:
    """

    #TODO: moze by tak zmienic mechanizm nazywania pol i pozniejszego porownywania ich w templatach????
    value = value.title()
    value = value.replace('And','and').replace('Mcdonald','McDonald').replace('Of','of').replace('The','the').replace(' I ', ' i ')
    field_label = value.split(" ")
    field_label.pop()
    return " ".join(field_label)

@register.filter
@stringfilter
def team_name_from_error(value):
    """

    :param value: uzywany glownie przy glosowaniu (vote_form.html) lub zmianie glosowania
    value (jest to key w form.errors.items) ma wartosc nazwa kraju, _ i nr meczu.
    :return:
    """

    field_label = value.split("_")
    field_label.pop()
    "".join(field_label)
    return field_label[0]


@register.filter
@stringfilter
def unicode_escape(value):

    return value.encode().decode('unicode_escape')