class ReX:
    """
    Abstract class that contains regular expression.
    """
    def __str__(self):
        pass


class Epsilon(ReX):
    """
    Empty regular expression.
    """
    def __str__(self):
        return ""


class Token(ReX):
    """
    Regular expression, consisting of one token.
    """
    def __init__(self, token: str):
        self.value = token

    def __str__(self):
        return self.value


class Concatenation(ReX):
    """
    Creates new ReX by using (a,b) rule.
    """
    def __init__(self, first: ReX, second: ReX):
        self.first = first
        self.second = second

    def __str__(self):
        return "(" + str(self.first) + "," + str(self.second) + ")"


class Union(ReX):
    """
    Creates new ReX by using (a|b) rule.
    """

    def __init__(self, first: ReX, second: ReX):
        self.first = first
        self.second = second

    def __str__(self):
        return "(" + str(self.first) + "|" + str(self.second) + ")"


class KleeneStar(ReX):
    """
    Creates new ReX by using e* rule.
    """

    def __init__(self, regular_expression: ReX):
        self.value = regular_expression

    def __str__(self):
        return str(self.value) + "*"


############

# EXAMPLES #

############

# Let's create (a|b)* regular expression:

example_expression = KleeneStar(Union(Token('a'), Token('b')))

print(example_expression)  # (a|b)*

# (a, b*) regular expression:

example_expression = Concatenation(Token('a'), KleeneStar(Token('b')))

print(example_expression)  # (a,b*)
