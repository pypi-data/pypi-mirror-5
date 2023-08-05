import threading


class ThreadLocalManager(threading.local):
    def __init__(self, default=None):
        # http://code.google.com/p/google-app-engine-django/issues/detail?id=119
        # we *must* use a keyword argument for ``default`` here instead
        # of a positional argument to work around a bug in the
        # implementation of _threading_local.local in Python, which is
        # used by GAE instead of _thread.local
        self.stack = []
        self.default = default

    def push(self, info):
        self.stack.append(info)

    set = push # b/c

    def pop(self):
        if self.stack:
            return self.stack.pop()

    def get(self):
        try:
            return self.stack[-1]
        except IndexError:
            return self.default()

    def clear(self):
        self.stack[:] = []


manager = ThreadLocalManager(default=defaults)


def get_thread_data(key):
    return manager.get()[key]

