class Result(object):
    def __init__(self, succeeded, message=None):
        self._succeeded = succeeded
        self.message = message

    @property
    def succeeded(self):
        return self._succeeded


class Success(Result):
    def __init__(self):
        super(Success, self).__init__(True)


class Failure(Result):
    def __init__(self, message):
        super(Failure, self).__init__(False, message)
