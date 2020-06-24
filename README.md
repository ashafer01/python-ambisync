# python-ambisync

Define methods that can be called synchronously or with `await` with the same signature.

This is meant to be used by authors and maintainers of general-purpose library modules/packages. Authors of application code are encouraged to choose one paradigm.

Copying and modifying the module for your library/application is welcome. Please star the repo on GitHub if you use it!

Available on PyPI: `pip install ambisync`

At present, the following caveats exist:

* The classes containing such methods must know whether they are operating syncronously or asynchronously.
  * Ambisync _cannot_ determine at call time whether it should behave synchronously or asynchronously.
* The method's body must be broken into subroutines if it's not already. For subroutines that need to `await`, both a synchronous local function and equivalent `async` local [sub-]coroutine must be defined.
* The sequence in which to call these subroutines must be defined, and equivalent sync/async subroutines must be declared as such.

See comments in [example.py](example.py) for documentation.
