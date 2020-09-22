import typing as tp

class ReX:
    """
    Abstract class that contains regular expression.
    """
    def __str__(self) -> str:
        pass

    def accepts(self, string: str) -> bool:
        pass


class Epsilon(ReX):
    """
    Empty regular expression.
    """
    def __str__(self) -> str:
        return ""

    def accepts(self, string: str) -> bool:
        return not string


class Symbol(ReX):
    """
    Regular expression, consisting of one symbol.
    """
    def __init__(self, symbol: str):
        self.value = symbol

    def __str__(self) -> str:
        return self.value

    def accepts(self, string: str) -> bool:
        return self.value == string


class Concatenation(ReX):
    """
    Creates new ReX by using (a,b) rule.
    """
    def __init__(self, first: ReX, second: ReX):
        self.first = first
        self.second = second

    def __str__(self) -> str:
        return f"({self.first},{self.second})"

    def accepts(self, string: str) -> bool:
        for l in range(len(string) + 1):
            if self.first.accepts(string[:l]) and self.second.accepts(string[l:]):
                return True
        return False


class Union(ReX):
    """
    Creates new ReX by using (a|b) rule.
    """

    def __init__(self, first: ReX, second: ReX):
        self.first = first
        self.second = second

    def __str__(self) -> str:
        return f"({self.first}|{self.second})"

    def accepts(self, string: str) -> bool:
        return self.first.accepts(string) or self.second.accepts(string)


class KleeneStar(ReX):
    """
    Creates new ReX by using e* rule.
    """

    def __init__(self, regular_expression: ReX):
        self.value = regular_expression

    def __str__(self) -> str:
        return str(self.value) + "*"

    def accepts(self, string: str) -> bool:
        if not string:
            return True

        for l in range(1, len(string) + 1):
            if self.value.accepts(string[:l]) and self.accepts(string[l:]):
                return True

        return False


class RexIterator:
    def __init__(self, expression: str):
        self.expression = expression
        self.cursor = 0

        while self.token().isspace():
            self.cursor += 1

    def is_end(self) -> bool:
        return self.cursor >= len(self.expression)

    def token(self) -> str:
        return self.expression[self.cursor] if not self.is_end() else ""

    def advance(self):
        self.cursor += 1
        while self.cursor < len(self.expression) and self.expression[self.cursor].isspace():
            self.cursor += 1

    def __next__(self) -> ReX:
        if self.is_end():
            raise StopIteration

        current_token = self.token()
        if current_token == "(":
            self.advance()
            first_rex = self.__next__()

            if self.is_end() or self.token() not in [",", "|"]:
                raise Exception("Wrong format of expression, expected , or | after (")

            operation = self.token()
            self.advance()

            second_rex = self.__next__()
            if self.is_end() or self.token() != ")":
                raise Exception(f"Expected ')', found '{self.token()}")

            self.advance()
            if operation == ",":
                result = Concatenation(first_rex, second_rex)
            elif operation == "|":
                result = Union(first_rex, second_rex)
            else:
                assert False, "Unreachable"

        elif current_token.isalpha():
            result = Symbol(current_token)
            self.advance()
        else:
            raise Exception(f"Unexpected '{current_token}' found")

        while not self.is_end() and self.token() == "*":
            result = KleeneStar(result)
            self.advance()

        return result

    def rest(self) -> str:
        return self.expression[self.cursor:]


class RexSequence:
    def __init__(self, expression: str):
        self.expression = expression

    def __iter__(self):
        return RexIterator(self.expression)


def parse(expression: str) -> ReX:
    iterator = RexIterator(expression)
    try:
        rex = iterator.__next__()
    except StopIteration:
        rex = Epsilon()

    if not iterator.is_end():
        raise Exception(f"Unexpected string {iterator.rest()} found")

    return rex


############
# EXAMPLES #
############


def single_example():
    """
    Parses expression from sample string and checks it for several strings
    """

    rex = parse("(a,(b|c))*")

    assert rex.accepts("")
    assert rex.accepts("acab")
    assert rex.accepts("ac")

    assert not rex.accepts("a")
    assert not rex.accepts("bacbac")
    assert not rex.accepts("aa")


def some_examples(sequence_string: str, strings: tp.List[str]):
    """
    Parses expressions from given sequence and checks for every string if it is accepted by regexp

    :arg sequence_string: sequence with regexps
    :arg strings: strings to check
    """
    for expression in RexSequence(sequence_string):
        for string in strings:
            print(expression, "accepts" if expression.accepts(string) else "not accepts", string)


def simple_examples():
    # Let's create (a|b)* regular expression:
    example_expression = KleeneStar(Union(Symbol('a'), Symbol('b')))

    print(example_expression)
    # prints (a|b)*

    # (a, b*) regular expression:
    example_expression = Concatenation(Symbol('a'), KleeneStar(Symbol('b')))

    print(example_expression)
    # prints (a,b*)


if __name__ == "__main__":
    single_example()
    some_examples(sequence_string="a (a,b) a** (b|a)", strings=["", "aa", "ab", "b", "a"])
    # prints:
    #   a not accepts
    #   (a,b) not accepts aa
    #   (a,b) accepts ab
    #   (a,b) not accepts b
    #   (b|a) accepts a
    # and so on
    simple_examples()
