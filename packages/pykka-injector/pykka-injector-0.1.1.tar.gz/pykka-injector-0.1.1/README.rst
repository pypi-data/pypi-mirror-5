pykka-injector
==============

.. image:: https://travis-ci.org/jstasiak/pykka_injector.png?branch=master
   :alt: Build status
   :target: https://travis-ci.org/jstasiak/pykka_injector


pykka-injector is a module uniting `Injector <https://github.com/alecthomas/injector>`_ (Dependency Injection framework) and `Pykka <https://github.com/jodal/pykka>`_ (Python implementation of the actor model). It's only purpose is to allow you to inject dependencies into Pykka Actors.

Works with:

* CPython 2.x >= 2.6, 3.x >= 3.2
* PyPy >= 1.9

Platform independent.


Usage example
-------------

::

    from injector import inject, Injector, InstanceProvider, Key, singleton
    from pykka import ThreadingActor
    from pykka_injector import ActorStarter

    Config = Key('Config')

    class MyActor(ThreadingActor):
        @inject(config=Config)
        def __init__(self, config, user):
            self.config = config
            self.user = user

    def configure(binder):
        binder.bind(
            Config,
            to=InstanceProvider(dict(environment='dev')),
            scope=singleton,
        )

    if __name__ == '__main__':
        injector = Injector(configure)
        starter = injector.get(ActorStarter)
        actor_ref = starter.start(MyActor, kwargs=dict(user='root'))

        actor_proxy = actor_ref.proxy()
        print(actor_proxy.config.get(), actor_proxy.user.get())

        actor_ref.stop()

Copyright
---------

Copyright (C) 2013 Jakub Stasiak

This source code is licensed under MIT license, see LICENSE file for details.
