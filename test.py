#!/usr/bin/env python
#-*- encoding: utf-8 -*-

from functools import wraps
from datetime import datetime

def log_func(func):
    @wraps(func)
    def logger(*args, **kwargs):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print('[%s] Start %s(%s, %s)...' % (now, func.__name__, args, kwargs))
        return func(*args, **kwargs)
    return logger

@log_func
def addition_func(x):
   """Do some math."""
   return x + x


result = addition_func(4)
print(result)
# Output: addition_func was called