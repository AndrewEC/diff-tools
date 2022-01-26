def log_exception(function):
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as e:
            print(f'An error occurred that prevented this action from completing: [{e}]')
            return None
    return wrapper
