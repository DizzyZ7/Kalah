import argparse
from .engine import KalahGame, InvalidMove
from .minimax import AIPlayer

BANNER = """
=======================
   KALAH (MANCALA)
=======================
"""


def play(args):
    game = KalahGame(pits_per_side=args.pits, seeds_per_pit=args.seeds)
    ai_first = AIPlayer(args.depth) if args.ai in ("first", "both") else None
    ai_second = AIPlayer(args.depth) if args.ai in ("second", "both") else None

    print(BANNER)

    while True:
        st = game.state
        print(st.render())
        if st.terminal():
            s0, s1 = st.score()
            print(f"Игра окончена. Склад Игрок1: {s0}, Склад Игрок2: {s1}")
            if s0 == s1:
                print("Ничья.")
            elif s0 > s1:
                print("Победил Игрок 1!")
            else:
                print("Победил Игрок 2!")
            return

        current_ai = ai_first if st.player == 0 else ai_second
        if current_ai:
            move = current_ai.choose(st)
            print(f"ИИ игрок {st.player+1} выбирает лунку: {move - st.n * (st.player) + 1}")
        else:
            prompt = f"Игрок {st.player+1}, ваш ход (1..{st.n}, q=выход): "
            s = input(prompt).strip().lower()
            if s == 'q':
                print('Выход. До встречи!')
                return
            if not s.isdigit():
                print('Введите номер лунки.\n')
                continue
            p = int(s) - 1
            move = p if st.player == 0 else st.n + p

        try:
            game.state, extra = st.apply(move)
            if extra:
                print("Бонусный ход! Ходите ещё раз.")
        except InvalidMove as e:
            print(str(e))


def main():
    parser = argparse.ArgumentParser(prog="kalah", description="Kalah console game")
    sub = parser.add_subparsers(dest="cmd")

    p_play = sub.add_parser("play", help="Play the game")
    p_play.add_argument("--pits", type=int, default=6, help="Лунок на стороне")
    p_play.add_argument("--seeds", type=int, default=6, help="Камней в лунке изначально")
    p_play.add_argument("--ai", choices=["none", "first", "second", "both"], default="none", help="Кто играет ИИ")
    p_play.add_argument("--depth", type=int, default=6, help="Глубина поиска ИИ")
    p_play.set_defaults(func=play)

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return
    args.func(args)

if __name__ == "__main__":
    main()
