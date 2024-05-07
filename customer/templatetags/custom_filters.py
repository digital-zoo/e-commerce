﻿from django import template

register = template.Library()

@register.filter
def calc_discount(price, discount_rate):
    return price * (1 - discount_rate)

@register.filter
def multiply_by_100(value):
    return value * 100

from customer.models import Customer

@register.filter
def like_tf(product, customer):
    try:
        current_customer = Customer.objects.get(id=14)
        if product.like_set.filter(customer=current_customer).exists():
            return True
        else:
            return False
    except Customer.DoesNotExist:
        return False
