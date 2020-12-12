import typing as tp
from copy import deepcopy

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
    epsilon - empty symbol for grammar (default is "")
    """
    def __init__(self,  terminals: tp.Set[str], non_terminals: tp.Set[str], start: str, rules: Rules, epsilon: str = ""):
        self.terminals = terminals
        self.non_terminals = non_terminals
        self.start = start
        self.rules = rules
        self.epsilon = epsilon
        for non_term in rules:
            assert non_term in non_terminals, "This is not a context-free grammar"


def delete_unreachable(grammar: ContextFreeGrammar):
    """
    Deletes unreachable non-terminals from given CF grammar.
    """
    reachable: tp.Set[str] = {grammar.start} if grammar.start in grammar.non_terminals else set()
    changed: bool = True  # if reachable was updated on last iteration
    while changed:
        changed = False
        for non_term, rules in grammar.rules.items():
            if non_term not in reachable:
                continue
            for rule in rules:
                for symbol in rule:
                    if symbol in grammar.non_terminals and symbol not in reachable:
                        reachable.add(symbol)
                        changed = True
    # delete not reachable symbols from grammar rules
    for symbol in grammar.non_terminals:
        if symbol not in reachable:
            grammar.rules.pop(symbol, None)
    grammar.non_terminals = reachable


def delete_dead(grammar: ContextFreeGrammar):
    """
    Deletes dead non-terminals from given CF grammar
    """
    alive: tp.Set[str] = set()
    changed: bool = True  # if alive was updated on last iteration
    while changed:
        changed = False
        for non_term, rules in grammar.rules.items():
            if non_term in alive:
                continue
            for rule in rules:
                if all(x in grammar.terminals or x in alive for x in rule):
                    alive.add(non_term)
                    changed = True
                    break
    for symbol in grammar.non_terminals:
        if symbol not in alive:
            grammar.rules.pop(symbol)
    for symbol, rules in grammar.rules.items():
        # delete all rules containing dead non-terminals
        grammar.rules[symbol] = [rule for rule in rules if all(x in grammar.terminals or x in alive for x in rule)]
    grammar.non_terminals = alive


def delete_extra_non_terminals(grammar: ContextFreeGrammar):
    """
    Deletes dead and unreachable non-terminals from grammar.
    """
    delete_dead(grammar)
    delete_unreachable(grammar)


def test_delete_extra():
    """
    Runs some checks for delete_extra_non_terminals
    """
    grammar = ContextFreeGrammar({'a', 'b'}, {'A', 'B'}, 'A', {'A': ['aA']})
    delete_unreachable(grammar)
    assert grammar.non_terminals == {'A'}
    delete_dead(grammar)
    assert grammar.non_terminals == set()

    # this example will give different results for different order of delete_dead/unreachable calls
    grammar = ContextFreeGrammar({'a', 'b'}, {'A', 'B'}, 'A', {'A': ['AB'], 'B': ['ab']})
    new_grammar = deepcopy(grammar)
    delete_extra_non_terminals(new_grammar)
    assert new_grammar.non_terminals == set()
    assert new_grammar.rules == dict()
    new_grammar = deepcopy(grammar)
    delete_unreachable(new_grammar)
    delete_dead(new_grammar)
    assert new_grammar.non_terminals == {'B'}

    grammar = ContextFreeGrammar({'a', 'b'}, {'A', 'B', 'C'}, 'A', {'A': ['B'], 'B': ['A', 'b'], 'C': ['Aa']})
    delete_extra_non_terminals(grammar)
    assert grammar.non_terminals == {'A', 'B'}


if __name__ == "__main__":
    test_delete_extra()
