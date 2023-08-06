import time

from pykka.actor import ThreadingActor
from pykka.registry import ActorRegistry


def time_it(func):
    start = time.time()
    func()
    print('%s took %.3fs' % (func.func_name, time.time() - start))


class SomeObject(object):
    pykka_traversable = False
    cat = 'bar.cat'

    def func(self):
        pass


class AnActor(ThreadingActor):
    bar = SomeObject()
    bar.pykka_traversable = True

    foo = 'foo'

    def __init__(self):
        super(AnActor, self).__init__()
        self.cat = 'quox'

    def func(self):
        pass


def test_direct_plain_attribute_access():
    actor = AnActor.start().proxy()
    for _ in range(10000):
        actor.foo.get()


def test_direct_callable_attribute_access():
    actor = AnActor.start().proxy()
    for _ in range(10000):
        actor.func().get()


def test_traversible_plain_attribute_access():
    actor = AnActor.start().proxy()
    for _ in range(10000):
        actor.bar.cat.get()


def test_traversible_callable_attribute_access():
    actor = AnActor.start().proxy()
    for _ in range(10000):
        actor.bar.func().get()


if __name__ == '__main__':
    try:
        time_it(test_direct_plain_attribute_access)
        time_it(test_direct_callable_attribute_access)
        time_it(test_traversible_plain_attribute_access)
        time_it(test_traversible_callable_attribute_access)
    finally:
        ActorRegistry.stop_all()
