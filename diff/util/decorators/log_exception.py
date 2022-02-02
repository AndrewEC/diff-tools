def log_exception(function):
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as e:
            print(f'The requested action could not be completed successfully. Reason: [{e}]')
            return None
    return wrapper
