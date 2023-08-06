import six
from .email import email
from .extremes import Min, Max
from .ip_address import ipv4, ipv6
from .mac_address import mac_address
from .utils import ValidationFailure, validator
from .url import url
from .uuid import uuid


__all__ = (
    ipv4,
    ipv6,
    email,
    mac_address,
    url,
    uuid,
    validator,
    ValidationFailure,
    Min,
    Max,
)


__version__ = '0.2'


@validator
def truthy(value):
    """
    Validates that given value is not a falsey value.

    This validator is based on `WTForms DataRequired validator`_.

    .. _WTForms DataRequired validator:
       https://github.com/wtforms/wtforms/blob/master/wtforms/validators.py

    Examples::


        >>> assert truthy(1)

        >>> assert truthy('someone')

        >>> assert not truthy(0)

        >>> assert not truthy('    ')

        >>> assert not truthy(False)

        >>> assert not truthy(None)

    .. versionadded:: 0.2
    """
    return (
        not value or
        isinstance(value, six.string_types) and not value.strip()
    )


@validator
def number_range(value, min=None, max=None):
    """
    Validates that a number is of a minimum and/or maximum value, inclusive.
    This will work with any comparable number type, such as floats and
    decimals, not just integers.

    This validator is based on `WTForms NumberRange validator`_.

    .. _WTForms NumberRange validator:
       https://github.com/wtforms/wtforms/blob/master/wtforms/validators.py

    Examples::


        >>> assert number_range(5, min=2)

        >>> assert number_range(13.2, min=13, max=14)

        >>> assert not number_range(500, max=400)


    :param min:
        The minimum required value of the number. If not provided, minimum
        value will not be checked.
    :param max:
        The maximum value of the number. If not provided, maximum value
        will not be checked.

    .. versionadded:: 0.2
    """
    if min is None and max is None:
        raise AssertionError(
            'At least one of `min` or `max` must be specified.'
        )
    if min is None:
        min = Min
    if max is None:
        max = Max
    if min > max:
        raise AssertionError('`min` cannot be more than `max`.')

    return min <= value <= max


@validator
def length(value, min=None, max=None):
    """
    Returns whether or not the length of given string is within a specified
    range.

    Examples::


        >>> assert length('something', min=2)

        >>> assert length('something', min=9, max=9)

        >>> assert not length('something', max=5)


    :param value:
        The string to validate.
    :param min:
        The minimum required length of the string. If not provided, minimum
        length will not be checked.
    :param max:
        The maximum length of the string. If not provided, maximum length
        will not be checked.

    .. versionadded:: 0.2
    """
    if (min is not None and min < 0) or (max is not None and max < 0):
        raise AssertionError(
            '`min` and `max` need to be greater than zero.'
        )
    return number_range(len(value), min=min, max=max)
