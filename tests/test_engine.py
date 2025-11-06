import pytest
from kalah.engine import KalahState, InvalidMove


def test_initial_legal_moves():
    st = KalahState()
    assert len(st.legal_moves()) == 6


def test_apply_and_turn_switch():
    st = KalahState()
    move = st.legal_moves()[0]
    new_st, extra = st.apply(move)
    assert isinstance(new_st, KalahState)
    assert extra in (True, False)
    if not extra and not new_st.terminal():
        assert new_st.player == 1


def test_capture_rule_simple():
    st = KalahState()
    n = st.n
    # Пустое поле, ходит Игрок 1
    st.board = [0] * (2 * n + 2)
    st.player = 0

    # Подготовка к захвату:
    # Лунка 3 у Игрока 1 будет пустой и станет местом приземления
    # Лунка 2 содержит 1 камень -> ход из 2 приведёт к приземлению в 3
    st.board[2] = 1
    # Напротив лунки 3 находится индекс (2n-1-3)
    opp_idx = 2 * n - 1 - 3  # = 2n - 4
    st.board[n + (opp_idx - n)] = 0  # просто явное указание, не обязательно
    st.board[opp_idx] = 4  # у соперника напротив есть 4 камня

    new_st, extra = st.apply(2)  # ход из лунки 2 -> последний камень в 3 (пустая)

    # В склад игрока 1 должны уйти 4 (противник) + 1 (наш последний)
    assert new_st.board[2 * n] == 5
    assert new_st.board[3] == 0
    assert new_st.board[opp_idx] == 0

def test_endgame_collection():
    st = KalahState()
    n = st.n
    # У игрока 1 один ход — после него сторона опустеет
    st.board = [1] + [0]*(n-1) + [0]*n + [0, 0]
    st.player = 0
    new_st, _ = st.apply(0)
    assert new_st.terminal()
    # все камни соперника собираются в его склад
    assert new_st.board[2*n+1] == 0
    assert new_st.board[2*n] >= 1


def test_invalid_move():
    st = KalahState()
    st.board[0] = 0
    with pytest.raises(InvalidMove):
        st.apply(0)
