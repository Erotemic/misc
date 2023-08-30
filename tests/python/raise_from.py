class MyException(Exception):
    ...

try:
    raise MyException('ex1')
except Exception as ex:
    raise RuntimeError('got error') from ex
