from grammar import ContextFreeGrammar
from copy import deepcopy
import typing as tp


class Parser:
    """
    Normalizes grammar so that is doesn't have left recursion and is left factorized.
    Performs left recursive parsing to check whether some word is in the given grammar.
    """
    def __init__(self, grammar: ContextFreeGrammar) -> None:
        self._grammar = deepcopy(grammar)
        self._grammar.eliminate_left_recursion()
        self._grammar.left_factorize()

    def is_in_language(self, word: tp.Sequence[str], cur=None) -> bool:
        if cur is None:
            cur = [self._grammar.start]
        if not word:
            vanishings = self._grammar.get_vanishings()
            return all(x in vanishings for x in cur)
        if not cur:
            return False
        if cur and cur[0] in self._grammar.terminals:
            if word[0] == cur[0]:
                return self.is_in_language(word[1:], cur[1:])
            return False
        for rule in self._grammar.rules[cur[0]]:
            if self.is_in_language(word, rule + cur[1:]):
                return True
        return False


def test_parser_brackets() -> None:
    brackets = ContextFreeGrammar(terminals={'(', ')'}, non_terminals={'A'}, start='A',
                                  rules={'A': ['(A)', '', 'AA']})
    parser = Parser(brackets)
    assert parser.is_in_language('')
    assert parser.is_in_language('()')
    assert parser.is_in_language("()()(())")
    assert not parser.is_in_language("())((())")


def test_parser_arithmetic() -> None:
    arithm = ContextFreeGrammar(terminals={'(', ')', '+', '*', '1', '2'}, non_terminals={'t', 's', 'c'}, start='s',
                                rules={'c': ['1', '2'], 't': ['c', 't*c', '(s)'], 's': ['t', 's+t']})
    parser = Parser(arithm)
    assert parser.is_in_language("1*2+2")
    assert parser.is_in_language("(1*2+2*1)")
    assert not parser.is_in_language("1+(2*1*)")


def test_parser_polynoms() -> None:
    polynoms = ContextFreeGrammar(terminals={'x', '^', 'n', '+'}, non_terminals={'m', 'p'}, start='p',
                                rules={'p': ['m', 'p+m'], 'm': ['x', 'x^n']})
    parser = Parser(polynoms)
    assert parser.is_in_language("x^n+x+x^n")
    assert not parser.is_in_language("x^x^n+x+x^n")
