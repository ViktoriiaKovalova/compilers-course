from enum import Enum
import typing as tp

T = tp.TypeVar('T')


class Color(Enum):
    NOT_VISITED = 0,
    VISITING = 1,
    VISITED = 2


class CycleFound(Exception):
    pass


class Graph:
    def __init__(self, graph: tp.Dict[T, tp.Iterable[T]]):
        self.graph = graph
        self.state = {}

    def has_cycle(self) -> bool:
        self.state = {v: Color.NOT_VISITED for v in self.graph}
        for v in self.graph:
            try:
                self._dfs(v)
            except CycleFound:
                return True
        return False

    def find_reachables(self) -> tp.Dict[T, tp.Set[T]]:
        def dfs(v: T) -> None:
            visited.add(v)
            for u in self.graph[v]:
                if u not in visited:
                    dfs(u)
        result = {}
        for v in self.graph:
            visited = set()
            dfs(v)
            result[v] = visited
        return result

    def _dfs(self, v):
        if self.state[v] == Color.VISITED:
            return
        if self.state[v] == Color.VISITING:
            raise CycleFound()
        self.state[v] = Color.VISITING
        for next_v in self.graph[v]:
            self._dfs(next_v)
        self.state[v] = Color.VISITED


def test_has_cycle():
    loop = Graph({1: [1]})
    graph = Graph({1: [2, 3], 2: [], 3: [4], 4: [2]})
    assert not  graph.has_cycle()
    graph = Graph({2: [3, 4], 1: [3], 3: [4], 4: [1]})
    assert graph.has_cycle()


if __name__ == "__main__":
    test_has_cycle()