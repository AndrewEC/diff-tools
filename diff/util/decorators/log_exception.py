def log_exception(function):
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as e:
            print(f'The command did not complete successfully. Reason: [{e}]')
            return None
    return wrapper
