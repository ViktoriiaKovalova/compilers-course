from lts import LTS, Transition
from rex import ReX, Epsilon, Symbol, KleeneStar, Union, Concatenation
import typing as tp


def rex2lts(rexp: ReX, first_state=0) -> LTS:
    """
    Builds LTS from given regexp.
    States will be numbered as 0, .m.., len(states) - 1.
    First one is starting state, last one - ending state.
    First_state is used to avoid collisions of states in recursive calls.
    """
    if isinstance(rexp, Epsilon) or isinstance(rexp, Symbol):
        label = ""
        if isinstance(rexp, Symbol):
            label = rexp.value
        start, end = first_state, first_state + 1
        transitions = {Transition(start, label, end)}
    elif isinstance(rexp, KleeneStar):
        lts_inner = rex2lts(rexp.inner, first_state + 1)  # we reserve first state for start
        start, end = first_state, lts_inner.end + 1
        transitions = lts_inner.transitions
        transitions.add(Transition(start, "", lts_inner.start))
        transitions.add(Transition(lts_inner.end, "", end))
        transitions.add(Transition(lts_inner.end, "", lts_inner.start))
        transitions.add(Transition(lts_inner.start, "", lts_inner.end))
    elif isinstance(rexp, Union):
        lts_fir = rex2lts(rexp.first, first_state + 1)  # first state is for start
        lts_sec = rex2lts(rexp.second, first_state + 1 + len(lts_fir.states))  # states from first lts are used already
        start, end = first_state, lts_sec.end + 1
        transitions = lts_fir.transitions
        transitions.update(lts_sec.transitions)
        transitions.add(Transition(start, "", lts_fir.start))
        transitions.add(Transition(start, "", lts_sec.start))
        transitions.add(Transition(lts_fir.end, "", end))
        transitions.add(Transition(lts_sec.end, "", end))
    elif isinstance(rexp, Concatenation):
        lts_fir = rex2lts(rexp.first)
        lts_sec = rex2lts(rexp.second, first_state + len(lts_fir.states))  # states from first lts are used already
        start, end = lts_fir.start, lts_sec.end
        transitions = lts_fir.transitions
        transitions.update(lts_sec.transitions)
        transitions.add(Transition(lts_fir.end, "", lts_sec.start))
    else:
        raise TypeError("Unknown regexp")
    return LTS(start, end, range(start, end + 1), {x.lbl for x in transitions}, transitions)


def main():
    """
    examples and some checks for correct work
    """
    a_lts = rex2lts(Symbol('a'))
    print(a_lts)  # start: 0, end: 1, transitions: {Transition(from_=0, lbl='a', to=1)}
    assert a_lts.accepts("a")
    assert not a_lts.accepts("b")
    a_star = rex2lts(KleeneStar(Symbol("a")))
    assert a_star.accepts("")
    assert a_star.accepts("aaaa")
    assert not a_star.accepts("aaabaa")
    cat_or_dog = rex2lts(Union(Symbol("cat"), Symbol("dog")))
    assert cat_or_dog.accepts(["cat"])
    assert cat_or_dog.accepts(["dog"])
    assert not cat_or_dog.accepts(["cow"])
    aaaa_cat = rex2lts(Concatenation(KleeneStar(Symbol("a")), Symbol("cat")))
    assert aaaa_cat.accepts(["a", "a", "a", "cat"])
    assert not aaaa_cat.accepts(["a", "a", "b", "cat"])


if __name__ == "__main__":
    main()



