import typing as tp
from copy import deepcopy, copy
from collections import defaultdict

from graph import Graph

"""
Dictionary that contains rules for given context-free grammar
Group of rule A -> a1...ak | b1...bl | ... will be represented as a pair:
A: [[a1, ..., ak], [b1, ..., bl], ...]
"""
Rules = tp.Dict[str, tp.List[tp.Sequence[str]]]


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
        self.rules = defaultdict(list, {key: [list(rule) for rule in group] for key, group in rules.items()})
        self._last_used_symbol = 0
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
        """
        Checks whether grammar has left_recursion
        """
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

    def delete_vanishings(self) -> None:
        """
        Gets rid of vanishing non-terminals
        """
        vanishings = self.get_vanishings()
        for symb, group in self.rules.items():
            new_rules = []
            for rule in group:
                vanishing_ind = []
                for i, ch in enumerate(rule):
                    if ch in vanishings:
                        vanishing_ind.append(i)
                combinations = 1 << len(vanishing_ind)
                vanishing_ind.append(len(rule))
                for mask in range(combinations):
                    beg = 0
                    new_rule = []
                    for i, ind in enumerate(vanishing_ind):
                        new_rule.extend(rule[beg:ind + (1 if (1 << i) & mask else 0)])
                        beg = ind + 1
                    if new_rule:
                        new_rules.append(new_rule)
            self.rules[symb] = new_rules
        # if there is an empty word in language we should add it
        if self.start in vanishings:
            new_start = self._get_next_unused()
            self.non_terminals.add(new_start)
            self.rules[new_start] = [[self.start], []]
            self.start = new_start

    def delete_chain_rules(self) -> None:
        """
        Deletes rules of type A->B
        """
        graph = {v: [] for v in self.non_terminals}
        for v in graph:
            for rule in self.rules[v]:
                if len(rule) == 1 and rule[0] in self.non_terminals:
                    graph[v].append(rule[0])
        reachable = Graph(graph).find_reachables()
        # delete chain rules
        for symb, rules in self.rules.items():
            self.rules[symb] = [rule for rule in rules if len(rule) != 1 or rule[0] not in self.non_terminals]
        new_rules = deepcopy(self.rules)
        for a, reachables in reachable.items():
            for b in reachables:
                if a != b:
                    new_rules[a].extend(self.rules[b])
        self.rules = new_rules

    def eliminate_left_recursion(self) -> None:
        """
        Eliminates left recursion
        """
        if not self.has_left_recursion():
            return
        self.delete_extra_non_terminals()
        self.delete_vanishings()
        self.delete_chain_rules()
        self.delete_extra_non_terminals()

        nonterminals = list(self.non_terminals)
        # process starting non_terminal first
        if self.start in nonterminals:
            ind = nonterminals.index(self.start)
            nonterminals[ind], nonterminals[-1] = nonterminals[-1], nonterminals[ind]
        while nonterminals:
            non_term = nonterminals.pop()
            # if doesn't have recursion
            if not any(rule and rule[0] == non_term for rule in self.rules[non_term]):
                continue
            non_term_rules, other_rules = [], []
            for rule in self.rules[non_term]:
                if rule[0] == non_term:
                    non_term_rules.append(rule[1:])
                else:
                    other_rules.append(rule)
            new_symb = self._get_next_unused()
            self.non_terminals.add(new_symb)
            self.rules[non_term] = [rule + [new_symb] for rule in other_rules]
            self.rules[new_symb] = [rule + [new_symb] for rule in non_term_rules] + [[]]
            # replace it in every right part beginning of bigger non-terminals rules
            for bigger_symb in nonterminals:
                if any(rule and rule[0] == non_term for rule in self.rules[bigger_symb]):
                    new_rules = []
                    for rule in self.rules[bigger_symb]:
                        if rule and rule[0] == non_term:
                            for non_term_left in self.rules[non_term]:
                                new_rules.append(non_term_left + rule[1:])
                        else:
                            new_rules.append(rule)
                    self.rules[bigger_symb] = new_rules

    def _left_factorize_group(self, non_term: str) -> None:
        rules_by_first = defaultdict(list)
        for rule in self.rules[non_term]:
            rules_by_first[rule[0] if rule else ''].append(rule)
        new_rules = []
        new_symbols = []
        for symbol, sym_rules in rules_by_first.items():
            if not symbol or symbol in self.terminals or len(sym_rules) < 2:
                new_rules.extend(sym_rules)
            else:
                new_beg = self._get_next_unused()
                self.non_terminals.add(new_beg)
                new_symbols.append(new_beg)
                new_rules.append([symbol, new_beg])
                self.rules[new_beg] = [rule[1:] for rule in sym_rules]
        self.rules[non_term] = new_rules
        for new_sym in new_symbols:
            self._left_factorize_group(new_sym)

    def left_factorize(self) -> None:
        """
        Performs left factorization of rules
        """
        for non_term in copy(self.non_terminals):
            self._left_factorize_group(non_term)

    def _get_next_unused(self) -> str:
        """
        Helper function to create new unused symbol
        """
        while str(self._last_used_symbol) in self.non_terminals or str(self._last_used_symbol) in self.terminals:
            self._last_used_symbol += 1
        return str(self._last_used_symbol)


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


def test_delete_vanishings():
    grammar = ContextFreeGrammar({'a', 'b'}, {'A', 'B', 'C'}, 'A', {'A': ['BC'], 'B': ['C'], 'C': ['']})
    grammar.delete_vanishings()
    assert [] in grammar.rules[grammar.start]


def test_left_factorize():
    grammar = ContextFreeGrammar({'a', 'b'}, {'A', 'B'}, 'A', {'A': ['BB', 'BB', 'C', ''], 'B': ''})
    grammar.left_factorize()
    assert set("".join(rule) for rule in grammar.rules['A']) == {'B0', 'C', ''}
    assert set("".join(rule) for rule in grammar.rules['0']) == {'B1'}
    assert set("".join(rule) for rule in grammar.rules['1']) == {''}


def check_eliminate_recursion():
    grammar = ContextFreeGrammar({'c', '+', '*'}, {'term', 'exp'}, 'exp', {'term': [['c'], ['c', '*', 'term']],
                                                                            'exp': [['exp', '+', 'exp'], ['term']]})
    grammar.eliminate_left_recursion()
    print(grammar.rules, grammar.start)
    # {'term': [['c'], ['c', '*', 'term']], 'exp': [['term', '0']], '0': [['+', 'exp', '0'], []]} exp


if __name__ == "__main__":
    test_delete_extra()
    test_vanishings()
    test_has_recursion()
    test_delete_vanishings()
    test_left_factorize()
    check_eliminate_recursion()
