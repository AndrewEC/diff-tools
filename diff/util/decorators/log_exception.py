def log_exception(message: str):
    """
    Wraps the decorated function in a try catch that will log the exception along with a custom message
    and default the function to return None.

    :param message: The custom message to be logged when an exception is caught.
    """
    def inner(function):
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except Exception as e:
                print(f'{message} [{e}]')
                return None
        return wrapper
    return inner
