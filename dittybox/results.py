import collections

SuccessTuple = collections.namedtuple('SuccessTuple', ['succeeded'])
FailureTuple = collections.namedtuple('FailureTuple', ['succeeded', 'message'])


def success():
    return SuccessTuple(True)


def failure(message):
    return FailureTuple(False, message)
