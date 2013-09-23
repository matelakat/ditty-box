class FakeStream(object):
    def __init__(self):
        self.state = 'open'

    def close(self):
        assert self.state == 'open'
        self.state = 'closed'

    @property
    def closed(self):
        return self.state == 'closed'
