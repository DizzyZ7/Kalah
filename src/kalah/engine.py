from dataclasses import dataclass
from typing import List, Optional, Tuple

class InvalidMove(Exception):
    pass

@dataclass
class KalahState:
    pits_per_side: int = 6
    seeds_per_pit: int = 6
    board: Optional[List[int]] = None
    player: int = 0  # 0 or 1; 0 ходит первым

    def __post_init__(self):
        if self.board is None:
            n = self.pits_per_side
            self.board = [self.seeds_per_pit] * (2 * n) + [0, 0]  # склады в конце: store0, store1
        # Индексы: 0..n-1 (первый игрок), n..2n-1 (второй игрок), 2n -> store0, 2n+1 -> store1

    @property
    def n(self) -> int:
        return self.pits_per_side

    @property
    def store_idx(self) -> int:
        return 2 * self.n + self.player

    @property
    def opp_store_idx(self) -> int:
        return 2 * self.n + (1 - self.player)

    def copy(self) -> "KalahState":
        return KalahState(self.n, self.seeds_per_pit, self.board.copy(), self.player)

    def pits_range(self, player: int) -> range:
        if player == 0:
            return range(0, self.n)
        return range(self.n, 2 * self.n)

    def is_own_pit(self, idx: int, player: Optional[int] = None) -> bool:
        if player is None:
            player = self.player
        r = self.pits_range(player)
        return idx in r

    def opposite_idx(self, idx: int) -> int:
        # Отражение относительно линии между сторонами
        return 2 * self.n - 1 - idx

    def legal_moves(self) -> List[int]:
        return [i for i in self.pits_range(self.player) if self.board[i] > 0]

    def terminal(self) -> bool:
        # Игра заканчивается, когда у текущего игрока ИЛИ у оппонента пустые все 6 лунок
        side0_empty = all(self.board[i] == 0 for i in self.pits_range(0))
        side1_empty = all(self.board[i] == 0 for i in self.pits_range(1))
        return side0_empty or side1_empty

    def score(self) -> Tuple[int, int]:
        n = self.n
        return self.board[2 * n], self.board[2 * n + 1]

    def collect_remaining(self):
        n = self.n
        side0 = sum(self.board[i] for i in self.pits_range(0))
        side1 = sum(self.board[i] for i in self.pits_range(1))
        for i in self.pits_range(0):
            self.board[i] = 0
        for i in self.pits_range(1):
            self.board[i] = 0
        self.board[2 * n] += side0
        self.board[2 * n + 1] += side1

    def apply(self, move: int) -> Tuple["KalahState", bool]:
        """Выполнить ход из лунки `move`. Возвращает (новое_состояние, extra_turn?).
        Бросает InvalidMove, если ход невозможен."""
        if move not in self.legal_moves():
            raise InvalidMove(f"Неверный ход: {move+1}")
        st = self.copy()
        stones = st.board[move]
        st.board[move] = 0
        idx = move
        n = st.n
        store0, store1 = 2 * n, 2 * n + 1
        own_store = store0 if st.player == 0 else store1
        opp_store = store1 if st.player == 0 else store0

        while stones > 0:
            idx = (idx + 1) % (2 * n + 2)
            if idx == opp_store:
                continue  # пропускаем склад соперника
            st.board[idx] += 1
            stones -= 1

        extra_turn = (idx == own_store)

        # Захват: последний камень в пустую свою лунку, напротив есть камни
        if not extra_turn and st.is_own_pit(idx) and st.board[idx] == 1:
            opp_idx = st.opposite_idx(idx)
            if st.board[opp_idx] > 0:
                captured = st.board[opp_idx] + 1
                st.board[opp_idx] = 0
                st.board[idx] = 0
                st.board[own_store] += captured

        # Проверка конца игры: если одна сторона пуста — собрать оставшееся
        if st.terminal():
            st.collect_remaining()
        else:
            if not extra_turn:
                st.player = 1 - st.player
        return st, extra_turn

    # Удобная текстовая визуализация
    def render(self) -> str:
        n = self.n
        top = self.board[self.n:2*self.n]
        bottom = self.board[:self.n]
        store0, store1 = self.board[2*n], self.board[2*n+1]
        # формат: верхняя строка справа налево (как в классических схемах)
        top_str = "  " + "  ".join(f"{top[i]:2d}" for i in reversed(range(len(top))))
        bottom_str = "  " + "  ".join(f"{bottom[i]:2d}" for i in range(len(bottom)))
        s = []
        s.append("\n    ┌" + "───" * n + "───────────" + "───" * n + "┐")
        s.append(f"    │   {'  '.join(['  ']*n)}  P1:{store0:2d}   {'  '.join(['  ']*n)}   │")
        s.append("    │  " + "  ".join(f"{i+1:>2}" for i in reversed(range(n))) + "     ↑     " + "  ".join(f"{i+1:>2}" for i in range(n)) + "  │")
        s.append("    │  " + "  ".join(f"{v:>2}" for v in reversed(top)) + "     │     " + "  ".join(f"{v:>2}" for v in bottom) + "  │")
        s.append(f"    │   {'  '.join(['  ']*n)}  P2:{store1:2d}   {'  '.join(['  ']*n)}   │")
        s.append("    └" + "───" * n + "───────────" + "───" * n + "┘\n")
        turn = "Игрок 1" if self.player == 0 else "Игрок 2"
        s.append(f"Ходит: {turn}. Выберите лунку 1..{n} на своей стороне.")
        return "\n".join(s)

class KalahGame:
    def __init__(self, pits_per_side: int = 6, seeds_per_pit: int = 6):
        self.state = KalahState(pits_per_side, seeds_per_pit)

    def winner(self) -> Optional[int]:
        if not self.state.terminal():
            return None
        s0, s1 = self.state.score()
        if s0 == s1:
            return -1  # ничья
        return 0 if s0 > s1 else 1
