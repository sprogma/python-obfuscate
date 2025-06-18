import common


class CompilationError(Exception):
    def __init__(self, msg):
        super(CompilationError, self).__init__(msg)
