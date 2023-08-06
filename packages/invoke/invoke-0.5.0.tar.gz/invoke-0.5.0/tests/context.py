from spec import Spec, skip
from mock import patch

from invoke.context import Context


class Context_(Spec):
    class run_:
        def _honors(self, kwarg, value):
            with patch('invoke.context.run') as run:
                Context(run={kwarg: value}).run('x')
                run.assert_called_with('x', **{kwarg: value})

        def warn(self):
            self._honors('warn', True)

        def hide(self):
            self._honors('hide', 'both')

        def pty(self):
            self._honors('pty', True)

        def echo(self):
            self._honors('echo', True)

    class clone:
        def returns_copy_of_self(self):
            skip()

        def contents_of_dicts_are_distinct(self):
            skip()
