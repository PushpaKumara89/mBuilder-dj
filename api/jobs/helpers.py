from functools import wraps

from sentry_sdk import capture_exception


def sentry_exceptions(func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            capture_exception(e)
            raise

    return inner
