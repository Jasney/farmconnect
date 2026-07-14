from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


def _to_decimal(value):
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal("0")


@register.filter
def mul(value, arg):
    return _to_decimal(value) * _to_decimal(arg)


@register.filter
def div(value, arg):
    denominator = _to_decimal(arg)
    if denominator == 0:
        return 0
    return _to_decimal(value) / denominator


@register.filter
def filter_rating(reviews, rating):
    try:
        target = int(rating)
    except (TypeError, ValueError):
        return []

    if hasattr(reviews, "filter"):
        return reviews.filter(rating=target)

    return [review for review in reviews if getattr(review, "rating", None) == target]
