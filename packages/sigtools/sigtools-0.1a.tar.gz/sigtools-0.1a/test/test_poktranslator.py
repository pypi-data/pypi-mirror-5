#!/bin/env python
import unittest

from sigtools import modifiers
from sigtools._util import funcsigs, signature
from sigtools.test import test_func_sig_coherent, f, s, func_from_sig
from sigtools.signatures import sort_params, apply_params
from test.util import sigtester

def replace_parameter(sig, param):
    params = sig.parameters.copy()
    params[param.name] = param
    return sig.replace(parameters=params.values())

def defaults_variations(exp, orig):
    yield exp, orig
    if set(exp.parameters.keys()) == set(orig.parameters.keys()):
        keys = [param.name for param in orig.parameters.values()
                if param.kind not in (param.VAR_POSITIONAL, param.VAR_KEYWORD)]
        for i in range(len(keys)):
            keys_ = keys[i:]
            exp_ = exp
            orig_ = orig
            for j, key in enumerate(keys_, i):
                exp_ = replace_parameter(
                    exp_, exp_.parameters[key].replace(default=j))
                orig_ = replace_parameter(
                    orig_, orig_.parameters[key].replace(default=j))
            yield exp_, orig_

def insert_varargs(sig, args, kwargs):
    posargs, pokargs, varargs, kwoargs, varkwargs = sort_params(sig)
    if args:
        varargs = funcsigs.Parameter(
            'args', funcsigs.Parameter.VAR_POSITIONAL)
    if kwargs:
        varkwargs = funcsigs.Parameter(
            'kwargs', funcsigs.Parameter.VAR_KEYWORD)
    ret = apply_params(sig, posargs, pokargs, varargs, kwoargs, varkwargs)
    return ret

def stars_variations(exp, orig):
    yield exp, orig
    yield insert_varargs(exp, True, False), insert_varargs(orig, True, False)
    yield insert_varargs(exp, False, True), insert_varargs(orig, False, True)
    yield insert_varargs(exp, True, True), insert_varargs(orig, True, True)

@sigtester
def poktranslator_tests(self, expected_sig_str, orig_sig_str,
                        posoargs, kwoargs):
    expected_sig = s(expected_sig_str)
    orig_sig = s(orig_sig_str)
    for exp, orig in defaults_variations(expected_sig, orig_sig):
        for exp, orig in stars_variations(exp, orig):
            func = modifiers._PokTranslator(
                func_from_sig(orig), posoargs, kwoargs)
            self.assertSigsEqual(exp, signature(func))
            test_func_sig_coherent(func)
            repr(func) # must not cause an error

@poktranslator_tests
class PokTranslatorTestsOneArg(object):
    _sig = 'a'

    regular = 'a', _sig, '', ''

    kwoarg = '*, a', _sig, '', 'a'

    posarg = '<a>', _sig, 'a', ''

    pos_already_pos = '<a>', '<a>', 'a', ''
    kwo_already_kwo = '*, a', '*, a', '', 'a'

    def test_kwoargs_noop(self):
        func = f('')
        self.assertIs(func, modifiers.kwoargs()(func))

    def test_posoargs_noop(self):
        func = f('')
        self.assertIs(func, modifiers.posoargs()(func))

@poktranslator_tests
class PokTranslatorTestsTwoArgs(object):
    _sig = 'a, b'

    regular = 'a, b', _sig, '', ''

    head_kwoarg = 'b, *, a', _sig, '', 'a'
    tail_kwoarg = 'a, *, b', _sig, '', 'b'
    all_kwoargs = '*, a, b', _sig, '', 'ab'

    one_posarg = '<a>, b', _sig, 'a', ''
    two_posargs = '<a>, <b>', _sig, 'ab', ''

    one_posarg_one_kwoarg = '<a>, *, b', _sig, 'a', 'b'
    one_kwoarg_one_posarg = '<b>, *, a', _sig, 'b', 'a'

    def test_merge_other(self):
        orig_func = f('a, b')
        func = modifiers.kwoargs('b')(modifiers.posoargs(end='a')(orig_func))
        self.assertSigsEqual(s('<a>, *, b'), signature(func))

@poktranslator_tests
class PokTranslatorTestsThreeArgs(object):
    _sig = 'a, b, c'

    regular = 'a, b, c', _sig, '', ''

    head_kwoarg = 'b, c, *, a', _sig, '', 'a'
    head_two_kwoargs = 'c, *, a, b', _sig, '', 'ab'

    all_kwoargs = '*, a, b, c', _sig, '', 'abc'

    tail_two_kwargs = 'a, *, b, c', _sig, '', 'bc'
    tail_kwarg = 'a, b, *, c', _sig, '', 'c'

    center_kwarg = 'a, c, *, b', _sig, '', 'b'

    one_posarg = '<a>, b, c', _sig, 'a', ''
    two_posargs = '<a>, <b>, c', _sig, 'ab', ''
    two_posargs_rev = '<a>, <b>, c', _sig, 'ba', ''
    three_posargs = '<a>, <b>, <c>', _sig, 'abc', ''

    posarg_pokarg_kwoarg = '<a>, b, *, c', _sig, 'a', 'c'
    posarg_kwoarg_pokarg = '<a>, c, *, b', _sig, 'a', 'b'
    kwoarg_posarg_pokarg = '<b>, c, *, a', _sig, 'b', 'a'
    posarg_kwoarg_kwoarg = '<a>, *, b, c', _sig, 'a', 'bc'
    kwoarg_posarg_kwoarg = '<b>, *, a, c', _sig, 'b', 'ac'
    kwoarg_kwoarg_posarg = '<c>, *, a, b', _sig, 'c', 'ab'

@sigtester
def poktranslator_raise_tests(self, sig_str, posoargs, kwoargs):
    func = f(sig_str)
    try:
        ret = modifiers._PokTranslator(func, posoargs, kwoargs)
    except ValueError:
        pass
    else:
        raise AssertionError(
            '_PokTranslator({0}, {1!r}, {2!r}) did not raise ValueError, '
            'instead returned {3}'.format(
                self.format_func(func), posoargs, kwoargs, ret))

@poktranslator_raise_tests
class PokTranslatorRaiseTests(object):
    missing_pos = '', 'a', ''
    missing_kwo = '', '', 'a'

    specifed_as_both = 'a', 'a', 'a'

    posarg_right = 'a, b', 'b', ''
    posarg_right_with_left = 'a, b, c', 'ac', ''

    pokarg_posarg_kwoarg = 'a, b, c', 'b', 'c'
    pokarg_kwoarg_posarg = 'a, b, c', 'c', 'b'

    pos_already_kwo = '*, a', 'a', ''
    pos_varargs = '*a', 'a', ''
    pos_kwargs = '**a', 'a', ''

    kwo_already_pos = '<a>', '', 'a'
    kwo_varargs = '*a', '', 'a'
    kwo_kwargs = '**a', '', 'a'

    def test_posoargs_end_missing_raises(self):
        func = f('')
        self.assertRaises(ValueError, modifiers.posoargs(end='a'), func)

    def test_kwoargs_start_missing_raises(self):
        func = f('')
        self.assertRaises(ValueError, modifiers.kwoargs(start='a'), func)

@sigtester
def kwoarg_start_tests(self, expected_sig_str, orig_sig_str, start):
    orig_func = f(orig_sig_str)
    func = modifiers.kwoargs(start=start)(orig_func)
    self.assertSigsEqual(s(expected_sig_str), signature(func))

@kwoarg_start_tests
class KwoargStartTests(object):
    _sig = 'a, b, c'

    first = '*, a, b, c', _sig, 'a'
    second = 'a, *, b, c', _sig, 'b'
    third = 'a, b, *, c', _sig, 'c'

    _sig = 'a, b, c, *args'

    star_first = '*args, a, b, c', _sig, 'a'
    star_second = 'a, *args, b, c', _sig, 'b'
    star_third = 'a, b, *args, c', _sig, 'c'

    _sig = '<a>, b, c'

    already_posoarg_second = '<a>, *, b, c', _sig, 'b'
    already_posoarg_third = '<a>, b, *, c', _sig, 'c'

@sigtester
def posoargs_end_tests(self, expected_sig_str, orig_sig_str, end):
    orig_func = f(orig_sig_str)
    func = modifiers.posoargs(end=end)(orig_func)
    self.assertSigsEqual(s(expected_sig_str), signature(func))

@posoargs_end_tests
class PosoargEndTests(object):
    _sig = 'a, b, c'

    first = '<a>, b, c', _sig, 'a'
    second = '<a>, <b>, c', _sig, 'b'
    third = '<a>, <b>, <c>', _sig, 'c'

    _sig = 'a, b, c, *args'

    star_first = '<a>, b, c, *args', _sig, 'a'
    star_second = '<a>, <b>, c, *args', _sig, 'b'
    star_third = '<a>, <b>, <c>, *args', _sig, 'c'

    _sig = '<a>, b, c'

    already_posoarg_second = '<a>, <b>, c', _sig, 'b'
    already_posoarg_third = '<a>, <b>, <c>', _sig, 'c'

@sigtester
def autokwoargs_tests(self, expected_sig_str, orig_sig_str, exceptions):
    orig_func = f(orig_sig_str)
    func = modifiers.autokwoargs(exceptions=exceptions)(orig_func)
    self.assertSigsEqual(s(expected_sig_str), signature(func))

@autokwoargs_tests
class AutokwoargsTests(object):
    none = 'a, b, c', 'a, b, c', ''
    one_arg = 'a, b, *, c=1', 'a, b, c=1', ''

if __name__ == '__main__':
    unittest.main()
