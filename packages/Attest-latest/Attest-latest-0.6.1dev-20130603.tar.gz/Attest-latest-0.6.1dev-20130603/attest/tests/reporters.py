from __future__ import with_statement

import sys
import inspect
from traceback import format_exception_only

from attest import (Tests, Assert, assert_hook, TestFailure, COMPILES_AST,
                    utils)
import attest

from . import _meta


SOURCEFILE = inspect.getsourcefile(_meta)
LINENO = 21
EXCEPTION = format_exception_only(TestFailure, '')[0].rstrip()


suite = Tests()


@suite.test
def get_all_reporters():
    reporters = set(['auto', 'fancy', 'plain', 'xml', 'quickfix', 'xunit'])
    assert set(attest.get_all_reporters()) == reporters


@suite.test
def get_reporter_by_name():
    reporters = dict(auto=attest.auto_reporter,
                     fancy=attest.FancyReporter,
                     plain=attest.PlainReporter,
                     xml=attest.XmlReporter,
                    )
    for name, reporter in reporters.iteritems():
        assert attest.get_reporter_by_name(name) == reporter


@suite.test
def auto_reporter():
    # Inside tests, sys.stdout is not a tty
    assert isinstance(attest.auto_reporter(), attest.PlainReporter)

    class FakeTTY(object):

        def isatty(self):
            return True

    sys.stdout, orig = FakeTTY(), sys.stdout
    try:
        assert isinstance(attest.auto_reporter(), attest.FancyReporter)
        with attest.disable_imports('progressbar', 'pygments'):
            assert isinstance(attest.auto_reporter(), attest.PlainReporter)
    finally:
        sys.stdout = orig


@suite.test_if(COMPILES_AST)
def xml_reporter():
    """XmlReporter"""

    with attest.capture_output() as (out, err):
        _meta.suite.run(attest.XmlReporter)

    for line, expected in zip(out[:5] + out[-3:], [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<testreport tests="2">',
        '  <pass name="attest.tests._meta.passing"/>',
        '  <fail name="attest.tests._meta.failing" type="TestFailure">',
        '    Traceback (most recent call last):',
        '    %s' % EXCEPTION,
        '  </fail>',
        '</testreport>',
    ]):
        assert line == expected


@suite.test_if(COMPILES_AST)
def plain_reporter():
    """PlainReporter"""

    with attest.capture_output() as (out, err):
        with Assert.raises(SystemExit):
            _meta.suite.run(attest.PlainReporter)

    width, _ = utils.get_terminal_size()
    for line, expected in zip(out[:7] + out[-3:], [
        '.F',
        '',
        'attest.tests._meta.failing',
        '-' * width,
        '-> stdout',
        'E: stderr',
        'Traceback (most recent call last):',
        '%s' % EXCEPTION,
        '',
        'Failures: 1/2 (1 assertions)',
    ]):
        assert line == expected


@suite.test_if(COMPILES_AST)
def quickfix_reporter():
    """QuickFixReporter"""

    with attest.capture_output() as (out, err):
        with Assert.raises(SystemExit):
            _meta.suite.run(attest.QuickFixReporter)

    assert out == ['%s:%d: TestFailure' % (SOURCEFILE, LINENO)]


@suite.test
def empty_run_zero_division_regression():
    Tests().run(attest.FancyReporter)
