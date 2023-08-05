# -*- coding: utf-8 -*-
"""
Use nose
`$ pip install nose`
`$ pip install mock`
`$ nosetests test_commando.py -d -v`
"""

from contextlib import nested
from commando import *
from mock import patch


try:
    import cStringIO
    StringIO = cStringIO
except ImportError:
    import StringIO as xStringIO
    StringIO = xStringIO


def trap_exit_fail(f):
    def test_wrapper(*args):
        try:
            f(*args)
        except SystemExit:
            import traceback
            print traceback.format_exc()
            assert False
    test_wrapper.__name__ = f.__name__
    return test_wrapper


def trap_exit_pass(f):
    def test_wrapper(*args):
        try:
            print f.__name__
            f(*args)
        except SystemExit:
            pass
    test_wrapper.__name__ = f.__name__
    return test_wrapper


class BasicCommandLine(Application):

    @command(description='test', prog='Basic')
    @param('--force', action='store_true', dest='force1')
    @param('--force2', action='store', dest='force2')
    @param('--version', action='version', version='%(prog)s 1.0')
    def main(self, params):
        assert params.force1 == eval(params.force2)
        self._main()

    def _main(self):
        pass

@trap_exit_fail
def test_command_basic():

    with patch.object(BasicCommandLine, '_main') as _main:
        c = BasicCommandLine()
        args = c.parse(['--force', '--force2', 'True'])
        c.run(args)
        assert _main.call_count == 1

        args = c.parse(['--force2', 'False'])
        c.run(args)

        assert _main.call_count == 2


def test_command_version_param():
    with patch.object(BasicCommandLine, '_main') as _main:
        c = BasicCommandLine()
        exception = False
        try:
            c.parse(['--version'])
            assert False
        except SystemExit:
            exception = True
        assert exception
        assert not _main.called


def test_positional_params():
    class PositionalCommandLine(Application):

        @command(description='test', prog='Basic')
        @param('force1', action='store')
        @param('force3', action='store')
        @param('force2', action='store')
        def main(self, params):
            self._main(params)

        def _main(self, params):
            assert params.force1 == '1'
            assert params.force3 == '2'
            assert params.force2 == '3'



    p = PositionalCommandLine()
    args = p.parse(['1', '2', '3'])
    p.run(args)


def test_command_version():
    class VersionCommandLine(Application):

        @command(description='test', prog='Basic')
        @param('--force', action='store_true', dest='force1')
        @param('--force2', action='store', dest='force2')
        @version('--version', version='%(prog)s 1.0')
        def main(self, params):
            assert params.force1 == eval(params.force2)
            self._main()

        def _main(self):
            pass

    with patch.object(VersionCommandLine, '_main') as _main:
        c = VersionCommandLine()
        exception = False
        try:
            c.parse(['--version'])
            assert False
        except SystemExit:
            exception = True
        assert exception
        assert not _main.called


class SuperDecoratedCommandLine(Application):

    @command(description='test', prog='Basic')
    @true('--force', dest='force1')
    @store('--force2', dest='force2')
    @const('--jam', const='jam')
    @version('--version', version='%(prog)s 1.0')
    def main(self, params):
        assert params.force1 == eval(params.force2)
        self._main()

    def _main(self):
        pass


def test_command_super():
    with patch.object(SuperDecoratedCommandLine, '_main') as _main:
        c = SuperDecoratedCommandLine()
        args = c.parse(['--force', '--force2', 'True'])
        c.run(args)
        assert _main.call_count == 1
        assert not args.jam

        args = c.parse(['--force2', 'False', '--jam'])
        c.run(args)
        assert _main.call_count == 2
        assert args.jam == 'jam'


class ComplexCommandLine(Application):

    @command(description='test', prog='Complex')
    @param('--force', action='store_true', dest='force1')
    @param('--force2', action='store', dest='force2')
    @param('--version', action='version', version='%(prog)s 1.0')
    def main(self, params):
        assert params.force1 == eval(params.force2)
        self._main()

    @subcommand('sub', description='test')
    @param('--launch', action='store_true', dest='launch1')
    @param('--launch2', action='store', dest='launch2')
    def sub(self, params):
        assert params.launch1 == eval(params.launch2)
        self._sub()

    def _main():
        pass

    def _sub():
        pass


@trap_exit_pass
def test_command_subcommands_usage():
    with nested(patch.object(ComplexCommandLine, '_main'),
                patch.object(ComplexCommandLine, '_sub')) as (_main, _sub):
        c = ComplexCommandLine()
        c.parse(['--usage'])


@trap_exit_fail
def test_command_subcommands():
    with nested(patch.object(ComplexCommandLine, '_main'),
                patch.object(ComplexCommandLine, '_sub')) as (_main, _sub):
        c = ComplexCommandLine()
        args = c.parse(['sub', '--launch', '--launch2', 'True'])
        c.run(args)
        assert not _main.called
        assert _sub.call_count == 1


class EmptyCommandLine(Application):

    @command(description='test', prog='Empty')
    def main(self, params):
        assert params == []
        self._main()

    @subcommand('sub', description='test sub')
    def sub(self, params):
        assert params
        assert len(params.__dict__) == 1
        self._sub()

    def _main():
        pass

    def _sub():
        pass


@trap_exit_pass
def test_empty_main_command():
    with nested(patch.object(EmptyCommandLine, '_main'),
                patch.object(EmptyCommandLine, '_sub')) as (_main, _sub):
        e = EmptyCommandLine(raise_exceptions=True)
        args = e.parse(None)
        e.run(args)
        assert not _sub.called
        assert _main.call_count == 1


def test_empty_sub_command():
    with nested(patch.object(EmptyCommandLine, '_main'),
                patch.object(EmptyCommandLine, '_sub')) as (_main, _sub):
        e = EmptyCommandLine(raise_exceptions=True)
        e.run(e.parse(['sub']))
        assert not _main.called
        assert _sub.call_count == 1


class NestedCommandLine(Application):

    @command(description='test', prog='Nested')
    @param('--force', action='store_true', dest='force1')
    @param('--force2', action='store', dest='force2')
    @param('--version', action='version', version='%(prog)s 1.0')
    def main(self, params):
        assert params.force1 == eval(params.force2)
        self._main()

    @subcommand('sub', description='sub')
    @param('--launch', action='store_true', dest='launch1')
    @param('--launch2', action='store', dest='launch2')
    def sub(self, params):
        assert params.launch1 == eval(params.launch2)
        self._sub()

    @subcommand('foobar', description="foo bar!")
    def foobar(self, params):
        assert False

    @subcommand('bla', parent=foobar)
    @param('--launch2', action='store_true', dest='launch2')
    def foobar_bla(self, params):
        assert params.launch2
        self._foobar_bla()

    @subcommand('blip', parent=foobar)
    def foobar_blip(self, params):
        assert False

    @subcommand('blop', parent=foobar_blip)
    def foobar_blip_blop(self, params):
        self._foobar_blip_blop()

    def _main():
        pass

    def _sub():
        pass

    def _foobar_bla():
        pass

    def _foobar_blip_blop():
        pass


@trap_exit_fail
def test_nested_command_subcommands():
    with nested(patch.object(NestedCommandLine, '_main'),
                patch.object(NestedCommandLine, '_sub'),
                patch.object(NestedCommandLine, '_foobar_bla'),
                patch.object(NestedCommandLine, '_foobar_blip_blop')) \
                as (_main, _sub, _foobar_bla, _foobar_blip_blop):

        c = NestedCommandLine(raise_exceptions=True)

        args = c.parse(['sub', '--launch', '--launch2', 'True'])
        c.run(args)
        assert not _main.called
        assert _sub.call_count == 1

        args = c.parse(['foobar', 'bla', '--launch2'])
        c.run(args)

        assert not _main.called
        assert _sub.call_count == 1
        assert _foobar_bla.call_count == 1

        args = c.parse(['foobar', 'blip', 'blop'])
        c.run(args)
        assert not _main.called
        assert _sub.call_count == 1
        assert _foobar_bla.call_count == 1
        assert _foobar_blip_blop.call_count == 1
