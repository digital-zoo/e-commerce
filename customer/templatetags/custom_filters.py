from django import template

register = template.Library()

@register.filter
def calc_discount(price, discount_rate):
    return price * (1 - discount_rate)