from copy import deepcopy

from .runner import run


class Context(object):
    """
    Context-aware API wrapper & state-passing object.

    `.Context` objects are created during command-line parsing (or, if desired,
    by hand) and used to share parser and configuration state with executed
    tasks (see :ref:`context-intro`). Specifically, the class offers wrappers
    for core API calls (such as `.run`) which take into account CLI parser
    flags, configuration files, and/or changes made at runtime.

    Instances of `.Context` may be shared between tasks when executing
    sub-tasks - either the same context the caller was given, or an altered
    copy thereof (or, theoretically, a brand new one).

    .. note::
        Transmitting a copy (using e.g. `.clone`) instead of mutating a
        ``Context`` in-place is a nice way to limit unwanted or hard-to-track
        state mutation, and/or to enable safer concurrency.
    """
    def __init__(self, run=None):
        """
        :param run:
            A dict acting as default ``**kwargs`` for `.run`. E.g. to create a
            `.Context` whose `Context.run` method defaults to ``echo=True``,
            say::

                ctx = Context(run={'echo': True})

        """
        self.config = {
            'run': run or {}
        }

    def clone(self):
        """
        Return a new Context instance resembling this one.

        Simple syntactic sugar for a handful of ``deepcopy`` calls, which
        generally work fine because config values are simple data structures.
        """
        return Context(
            run=deepcopy(self.config['run'])
        )

    def run(self, *args, **kwargs):
        """
        Wrapper for `.run`.

        To set default `.run` keyword argument values, instantiate `.Context`
        with the ``run`` kwarg set to a dict.

        E.g. to create a `.Context` whose `.Context.run` method always defaults
        to ``warn=True``::

            ctx = Context(run={'warn': True})
            ctx.run('command') # behaves like invoke.run('command', warn=True)

        """
        options = dict(self.config['run'])
        options.update(kwargs)
        return run(*args, **options)
