import collections

SuccessTuple = collections.namedtuple('SuccessTuple', ['succeeded'])
FailureTuple = collections.namedtuple('FailureTuple', ['succeeded', 'message'])


def Success():
    return SuccessTuple(True)


def Failure(message):
    return FailureTuple(False, message)
