import typing as tp
from copy import deepcopy

from graph import Graph

"""
Dictionary that contains rules for given context-free grammar
Group of rule A -> a1...ak | b1...bl | ... will be represented as a pair:
A: [[a1, ..., ak], [b1, ..., bl], ...]
"""
Rules = tp.Dict[str, tp.Sequence[tp.Sequence[str]]]


class ContextFreeGrammar:
    """
    Represents context-free grammar (such grammar that contains only rules of form A->a1...ak, where A is non-terminal).
    Creates a class containing all information about given context-free grammar

    Fields:
    terminals - terminal symbols of grammar
    non-terminals - non-terminal symbols of grammar
    start - the start non-terminal symbol of grammar
    rules - rules of context-free grammar
    """
    def __init__(self,  terminals: tp.Set[str], non_terminals: tp.Set[str], start: str, rules: Rules):
        self.terminals = terminals
        self.non_terminals = non_terminals
        self.start = start
        self.rules = rules
        for non_term in rules:
            assert non_term in non_terminals, "This is not a context-free grammar"

    def delete_unreachable(self) -> None:
        """
        Deletes unreachable non-terminals from grammar.
        """
        reachable: tp.Set[str] = {self.start} if self.start in self.non_terminals else set()
        changed: bool = True  # if reachable was updated on last iteration
        while changed:
            changed = False
            for non_term, rules in self.rules.items():
                if non_term not in reachable:
                    continue
                for rule in rules:
                    for symbol in rule:
                        if symbol in self.non_terminals and symbol not in reachable:
                            reachable.add(symbol)
                            changed = True
        # delete not reachable symbols from grammar rules
        for symbol in self.non_terminals:
            if symbol not in reachable:
                self.rules.pop(symbol, None)
        self.non_terminals = reachable

    def delete_dead(self) -> None:
        """
        Deletes dead non-terminals from grammar
        """
        alive: tp.Set[str] = set()
        changed: bool = True  # if alive was updated on last iteration
        while changed:
            changed = False
            for non_term, rules in self.rules.items():
                if non_term in alive:
                    continue
                for rule in rules:
                    if all(x in self.terminals or x in alive for x in rule):
                        alive.add(non_term)
                        changed = True
                        break
        for symbol in self.non_terminals:
            if symbol not in alive:
                self.rules.pop(symbol)
        for symbol, rules in self.rules.items():
            # delete all rules containing dead non-terminals
            self.rules[symbol] = [rule for rule in rules if all(x in self.terminals or x in alive for x in rule)]
        self.non_terminals = alive

    def delete_extra_non_terminals(self) -> None:
        """
        Deletes dead and unreachable non-terminals from grammar.
        """
        self.delete_dead()
        self.delete_unreachable()

    def get_vanishings(self) -> tp.List[str]:
        """
        Get a list of vanishing terminals
        """
        vanishings: tp.Set[str] = set()
        changed: bool = True  # if vanishings were updated on last iteration
        while changed:
            changed = False
            for non_term, group in self.rules.items():
                if non_term in vanishings:
                    continue
                for rule in group:
                    if all(x in vanishings for x in rule):
                        vanishings.add(non_term)
                        changed = True
                        break
        return vanishings

    def has_left_recursion(self) -> bool:
        vanishings = self.get_vanishings()
        graph: tp.Dict[str, tp.Set[str]] = {v: set() for v in self.non_terminals}
        for symbol, group in self.rules.items():
            for rule in group:
                for sec_symbol in rule:
                    if sec_symbol not in self.non_terminals:
                        break
                    graph[symbol].add(sec_symbol)
                    if sec_symbol not in vanishings:
                        break
        # grammar has left recursion iff graph has cycle
        # now let's check if there is a cycle
        return Graph(graph).has_cycle()


def test_delete_extra():
    """
    Runs some checks for delete_extra_non_terminals
    """
    grammar = ContextFreeGrammar({'a', 'b'}, {'A', 'B'}, 'A', {'A': ['aA']})
    grammar.delete_unreachable()
    assert grammar.non_terminals == {'A'}
    grammar.delete_dead()
    assert grammar.non_terminals == set()

    # this example will give different results for different order of delete_dead/unreachable calls
    grammar = ContextFreeGrammar({'a', 'b'}, {'A', 'B'}, 'A', {'A': ['AB'], 'B': ['ab']})
    new_grammar = deepcopy(grammar)
    new_grammar.delete_extra_non_terminals()
    assert new_grammar.non_terminals == set()
    assert new_grammar.rules == dict()
    new_grammar = deepcopy(grammar)
    new_grammar.delete_unreachable()
    new_grammar.delete_dead()
    assert new_grammar.non_terminals == {'B'}

    grammar = ContextFreeGrammar({'a', 'b'}, {'A', 'B', 'C'}, 'A', {'A': ['B'], 'B': ['A', 'b'], 'C': ['Aa']})
    grammar.delete_extra_non_terminals()
    assert grammar.non_terminals == {'A', 'B'}


def test_vanishings():
    """
    Check get_vanishings
    """
    grammar = ContextFreeGrammar({'a', 'b'}, {'A', 'B', 'C'}, 'A', {'A': ['BC'], 'B': ['C'], 'C': ['']})
    assert grammar.get_vanishings() == {'A', 'B', 'C'}
    grammar = ContextFreeGrammar({'a', 'b'}, {'A', 'B', 'C'}, 'A', {'A': ['bc'], 'B': ['c'], 'C': ['']})
    assert grammar.get_vanishings() == {'C'}


def test_has_recursion():
    """
    Check has_left_recursion
    """
    grammar = ContextFreeGrammar({'a', 'b'}, {'A', 'B', 'C'}, 'A', {'A': ['BC'], 'B': ['C'], 'C': ['']})
    assert not grammar.has_left_recursion()
    simple_grammar = ContextFreeGrammar({}, {'A'}, 'A', {'A': ['A']})
    assert simple_grammar.has_left_recursion()
    grammar = ContextFreeGrammar({'a', 'b'}, {'A', 'B', 'C'}, 'A', {'A': ['BC'], 'B': [''], 'C': ['AB']})
    assert grammar.has_left_recursion()


if __name__ == "__main__":
    test_delete_extra()
    test_vanishings()
    test_has_recursion()
