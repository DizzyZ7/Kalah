from typing import Callable, Optional, Tuple
from .engine import KalahState

EvalFn = Callable[[KalahState], int]

# Простейшая эвристика: (мой_склад - склад_оппонента) + (0.2 * мои_камни_на_стороне)
# Можно заменить на что-то сложнее при желании.
def evaluate(state: KalahState, player: int) -> int:
    n = state.n
    my_store = state.board[2*n + player]
    opp_store = state.board[2*n + (1 - player)]
    my_side = sum(state.board[i] for i in state.pits_range(player))
    return (my_store - opp_store) * 100 + int(0.2 * my_side)


def minimax(state: KalahState, depth: int, player: int, alpha: int, beta: int) -> Tuple[int, Optional[int]]:
    if depth == 0 or state.terminal():
        return evaluate(state, player), None

    best_move = None

    if state.player == player:
        # Максимизируем
        max_eval = -10**9
        for m in state.legal_moves():
            nxt, extra = state.apply(m)
            if extra and not nxt.terminal():
                val, _ = minimax(nxt, depth - 1, player, alpha, beta)
            else:
                val, _ = minimax(nxt, depth - 1, player, alpha, beta)
            if val > max_eval:
                max_eval, best_move = val, m
            alpha = max(alpha, val)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        # Минимизируем
        min_eval = 10**9
        for m in state.legal_moves():
            nxt, extra = state.apply(m)
            val, _ = minimax(nxt, depth - 1, player, alpha, beta)
            if val < min_eval:
                min_eval, best_move = val, m
            beta = min(beta, val)
            if beta <= alpha:
                break
        return min_eval, best_move


class AIPlayer:
    def __init__(self, depth: int = 6):
        self.depth = depth

    def choose(self, state: KalahState) -> int:
        _, move = minimax(state, self.depth, state.player, -10**9, 10**9)
        assert move is not None, "Нет допустимых ходов"
        return move


def best_move(state: KalahState, depth: int = 6) -> int:
    return AIPlayer(depth).choose(state)
