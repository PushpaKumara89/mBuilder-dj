from rest_framework.views import exception_handler
from moneyed import CurrencyDoesNotExist
from rest_framework.exceptions import ValidationError, AuthenticationFailed


def custom_exception_handler(exception, context):
    response = exception_handler(exception, context)

    handleCurrencyDoesNotExist(exception)

    return updateResponseDetailMessage(exception, response)


def handleCurrencyDoesNotExist(exception):
    if isinstance(exception, CurrencyDoesNotExist):
        raise ValidationError('Currency code is invalid.')


def updateResponseDetailMessage(exception, response):
    if isinstance(exception, AuthenticationFailed):
        response.data['detail'] = 'The email address or password you entered is incorrect.'

    return response
