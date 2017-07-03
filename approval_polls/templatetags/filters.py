from django.template import Library

register = Library()

# Taken from https://djangosnippets.org/snippets/1357/


@register.filter
def get_range(value):
    """
    Filter - returns a list containing range made from given value
    Usage (in template):

    <ul>{% for i in 3|get_range %}
      <li>{{ i }}. Do something</li>
    {% endfor %}</ul>

    Results with the HTML:
    <ul>
      <li>0. Do something</li>
      <li>1. Do something</li>
      <li>2. Do something</li>
    </ul>

    Instead of 3 one may use the variable set in the views
    """
    return range(1, value)


@register.filter
def get_item(value, arg):
    val = value.get(arg)
    if val is not None:
        return str(val)
    else:
        return val


@register.filter
def get_hash_item(value, arg):
    val = value.get(arg)
    return val
