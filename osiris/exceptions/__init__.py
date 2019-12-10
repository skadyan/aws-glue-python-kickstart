class IllegalArgumentException(Exception):
    def __init__(self, msg: str):
        self.msg = msg


class IllegalStateException(Exception):
    def __init__(self, msg: str):
        self.msg = msg


class BadInterpolationException(Exception):
    def __init__(self, msg):
        self.msg = msg
