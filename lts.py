import typing as tp
from collections import defaultdict
from dataclasses import dataclass


@dataclass(frozen=True)
class Transition:
    """
    Transition represents the transition in LTS
    and contains two states and label of transition.
    """
    from_: int
    lbl: str
    to: int


class LTS:
    """
    LTS represents the labelled transition system.
    Constructor parameters are starting state, ending state, set of states, tokens and transitions.
    """

    def __init__(self, start: int, end: int, states: tp.Set[int], tokens: tp.Set[str], transitions: tp.Set[Transition]):
        self.start = start
        self.end = end
        self.tokens = tokens
        self.states = states
        self.transitions = transitions
        # we store transitions in dict with keys (from, lbl) to get faster access to transitions
        # given state, from which transitions are needed, and label
        trans_from_with_label: tp.Dict[tp.Tuple[int, str], tp.List[Transition]] = defaultdict(list)
        for tr in transitions:
            trans_from_with_label[(tr.from_, tr.lbl)].append(tr)
        self.trans_from_lbl = dict(trans_from_with_label)

    def __repr__(self) -> str:
        return f"start: {self.start}, end: {self.end}, transitions: {sorted(self.transitions, key=lambda x: x.from_)}"

    def closure(self, states: tp.List[int]) -> tp.Set[int]:
        """
        returns the closure of given states, e.g. all states reachable via epsilon-transitions
        """
        set_ = set(states)
        added = list(set_)
        while added:
            cur = added.pop()
            # if no epsilon transitions
            if self.trans_from_lbl.get((cur, "")) is None:
                continue
            for tr in self.trans_from_lbl[(cur, "")]:
                if tr.to not in set_:
                    set_.add(tr.to)
                    added.append(tr.to)
        return set_

    def accepts(self, chain: tp.Sequence[str]) -> bool:
        reached = {(x, 0) for x in self.closure([self.start])}
        while reached:
            state, length = reached.pop()
            # if we found good path
            if length == len(chain) and state == self.end:
                return True
            # if path is longer than chain
            if length >= len(chain):
                continue
            if self.trans_from_lbl.get((state, chain[length])):
                new_states = []
                for tr in self.trans_from_lbl[(state, chain[length])]:
                    new_states.append(tr.to)
                reached.update([(x, length + 1) for x in self.closure(new_states)])
        return False
