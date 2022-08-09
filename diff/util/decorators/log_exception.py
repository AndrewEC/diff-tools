def log_exception(message: str):
    def inner(function):
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except Exception as e:
                print(f'{message}. [{e}]')
                return None
        return wrapper
    return inner
