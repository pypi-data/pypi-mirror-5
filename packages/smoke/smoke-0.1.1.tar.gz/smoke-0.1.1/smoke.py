#!/usr/bin/env python3

from collections import defaultdict
from functools import partial


class SignalControl(Exception):
    '''Base type of signal control exceptions'''


class Disconnect(SignalControl):
    '''Handlers which raise this exception will be disconnected from the
    active signal'''


class StopPropagation(SignalControl):
    '''When this exception is raised by a handler no further handlers will
    be called for the active signal'''


def weak(meth, exception=Disconnect):
    '''Adapt a bound method to not count towards the refcount.

    Useful in e.g UI code where a view wants updates from a model but don't
    want that subscription to keep the widget around after closing the view.

    It works by holding a reference to the underlying function and creating a
    weakref to the bound `self` of the method. When the callback is called if
    the instance is no longer alive a `Disconnect` will be raised to the
    publish loop.
    '''

    import weakref

    try:  # python 3
        fun = meth.__func__
        ref = meth.__self__
    except AttributeError as e:  # python 2
        fun = meth.im_func
        ref = meth.im_self

    # precompute some strings that rely on the bound to object.
    srpr = repr(ref)
    funpath = '.'.join((
        fun.__module__,
        ref.__class__.__name__,
        fun.__name__))

    # Drop hard references to the bound object.
    ref = weakref.ref(ref)
    del meth

    def weak_method(*args, **kwargs):
        '''weakly bound method %s of %r''' % (funpath, srpr)

        obj = ref()
        if obj is None:
            raise exception("%s called on dead object" % funpath)

        return fun(obj, *args, **kwargs)

    return weak_method


def subscribers(obj, event):
    '''Get a list of all subscribers to `event` on `obj`'''
    if not hasattr(obj, '_subscribers'):
        obj._subscribers = defaultdict(list)

    return obj._subscribers[event]


def subscribe(obj, event, subscriber):
    '''Add a subscriber to `event` on `obj`'''
    subscribers(obj, event).append(subscriber)


def disconnect(obj, event, subscriber):
    '''Disconnect a subscriber to `event` on `obj`'''
    subscribers(obj, event).remove(subscriber)


def publish(obj, _event, **kwargs):
    '''Invoke all subscribers to `event` on `obj`

        Two flowcontrol exceptions exist that may be raised by subscribers
         * `Disconnect`
            A subscriber raising this exception will not be notified of
            this event further
         * `StopPropagation`
            Immediatly breaks the publish loop, no other subscribers will
            be notified.

        All other exceptions will be passed to the parent context and will
        break the publish loop without notifing remaining subscribers
    '''
    subs = subscribers(obj, _event)
    disconnected = []
    try:
        for sub in subs:
            try:
                sub(**kwargs)
            except Disconnect:
                disconnected.append(sub)
            except StopPropagation:
                break
    finally:
        for d in disconnected:
            subs.remove(d)


class Broker(object):
    ''' Mixin with event publish/subscribe methods'''

    subscribe = subscribe
    disconnect = disconnect
    publish = publish


class boundsignal(object):
    '''A signal that when published calls all of its subscribers'''

    def __init__(self, signal, im_self):
        self.__signal = signal
        self.__im_self = im_self

    def subscribe(self, subscriber):
        '''Subscribe a callback to this event'''
        subscribe(self.__im_self, self.__signal.name or self, subscriber)

    def disconnect(self, subscriber):
        '''Disconnect a callback from this event'''
        disconnect(self.__im_self, self.__signal.name or self, subscriber)

    def publish(self, **kwargs):
        '''Publish this event on `obj`'''
        publish(self.__im_self, self.__signal.name or self, **kwargs)

    def __call__(self, **kwargs):
        self.publish(**kwargs)

    def __hash__(self):
        return hash(self.__signal) ^ hash(self.__im_self)

    def __eq__(self, other):
        try:
            osignal = other.__signal
            oself = other.__im_self
        except AttributeError:
            return False

        return (self.__signal == osignal and self.__im_self == oself)

    def __repr__(self):
        return '<bound signal of %r>' % (self.__im_self,)


def binding(cls, fun):
    '''Create a proxy to `fun` that binds to `cls`

    When the proxy is called it dispatches to `fun` with a new instance of
    `cls` as the first argument. The new instance is created from the 1st and
    2nd argument to the proxy. The remaining arguments is forwarded to the
    original function.
    '''

    def bound(self, obj, *args, **kwargs):
        '''Proxy of %s binding as %s''' % (fun, cls)
        fun(cls(self, obj), *args, **kwargs)

    return bound


class signal(object):
    '''Publish/Subscribe pattern in a descriptor

    By creating a class member of this type you are enabling the class
    to publish events by that name for others to subscribe too
    '''

    def __init__(self, name=None):
        self.name = name

    def __get__(self, obj, objtype=None):
        '''Descriptor protocol

        returns self wrapped in a `boundsignal` when accessed from a
        instance
        '''

        if obj is None:
            return self
        return boundsignal(self, obj)

    subscribe = binding(boundsignal, boundsignal.subscribe)
    disconnect = binding(boundsignal, boundsignal.disconnect)
    publish = binding(boundsignal, boundsignal.publish)

    def __call__(self, obj, **kwargs):
        '''Alias for publish'''
        self.publish(obj, **kwargs)

    def __repr__(self):
        return '<signal(%s) at 0x%r>' % (self.name or '', id(self))


if __name__ == '__main__':
    import logging
    out = logging.getLogger().info

    class Bar:
        throb = signal()

    class Foo:
        method_two = signal()

        def __init__(self, bar):
            self.__bar = bar
            self.method_one = bar.throb
            bar.throb.subscribe(self.method_two)

    bar = Bar()

    bar.throb.subscribe(partial(out, 'hello '))
    Bar.throb.subscribe(bar, partial(out, 'world!'))

    # prints
    bar.throb()

    # prints too
    f = bar.throb
    f()

    foo = Foo(bar)
    foo.method_one.subscribe(partial(out, 'spam'))
    foo.method_two.subscribe(partial(out, 'egg'))

    # prints some more
    bar.throb()
