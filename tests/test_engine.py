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
    # Сценарий для захвата: у игрока 1 на лунке 0 один камень, напротив у соперника >0
    st = KalahState()
    n = st.n
    st.board = [0]* (2*n + 2)
    st.player = 0
    st.board[0] = 1
    st.board[n + (n-1)] = 4  # напротив лунки 0 — индекс 2n-1
    new_st, extra = st.apply(0)
    assert new_st.board[2*n] == 5  # 4 + 1 в склад игрока 1
    assert new_st.board[0] == 0
    assert new_st.board[2*n - 1] == 0


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
