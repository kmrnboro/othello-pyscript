from pyscript import document, window
from pyscript.ffi import create_proxy
import asyncio

from game_logic import OthelloGame


game = None
_event_proxies = []


def _keep_proxy(callback):
    """Keep JS callback proxies alive for the lifetime of the page."""
    proxy = create_proxy(callback)
    _event_proxies.append(proxy)
    return proxy


def init_game():
    global game
    window.console.log("Initialize Othello/Reversi...")
    game = OthelloGame()
    window.console.log("Game Initialized")
    render_board()
    asyncio.create_task(check_game_state_and_continue())


def render_board():
    """HTML盤面の描画更新"""
    board_el = document.getElementById("game-board")

    # 初回生成
    if board_el.childElementCount == 0:
        for r in range(8):
            for c in range(8):
                cell_div = document.createElement("div")
                cell_div.className = "cell"
                cell_div.dataset.row = str(r)
                cell_div.dataset.col = str(c)

                piece_div = document.createElement("div")
                piece_div.className = "piece"
                cell_div.appendChild(piece_div)

                def on_cell_click(event, r=r, c=c):
                    asyncio.create_task(handle_click(r, c))

                cell_div.addEventListener("click", _keep_proxy(on_cell_click))
                board_el.appendChild(cell_div)

    cells = document.querySelectorAll(".cell")
    for i in range(cells.length):
        r = int(cells[i].dataset.row)
        c = int(cells[i].dataset.col)
        cell_val = game.board[r][c]

        cells[i].classList.remove("black", "white", "valid-move", "best-move")

        if cell_val == OthelloGame.BLACK:
            cells[i].classList.add("black")
        elif cell_val == OthelloGame.WHITE:
            cells[i].classList.add("white")

    update_status()
    highlight_valid_moves()


def get_ai_color():
    player_color = document.getElementById("player-color").value
    return OthelloGame.WHITE if player_color == "black" else OthelloGame.BLACK


def update_status():
    current = "くろ" if game.current_turn == OthelloGame.BLACK else "しろ"
    black, white = game.get_counts()
    status_text = f"じゅんばん: {current} | くろ: {black} | しろ: {white}"
    if not game.has_valid_move() and not game.is_game_over():
        status_text += " (パス！)"
    document.getElementById("status").innerText = status_text


async def handle_click(r, c):
    if game.is_game_over():
        return

    ai_level = document.getElementById("ai-level").value
    if ai_level != "none" and game.current_turn == get_ai_color():
        return

    if game.apply_move(r, c):
        window.console.log(f"Move applied: {r}, {c}")
        render_board()
        await check_game_state_and_continue()


async def check_game_state_and_continue():
    if game.is_game_over():
        show_game_over()
        return

    if not game.has_valid_move():
        window.console.log("No valid moves, switching turn")
        game.switch_turn()
        render_board()
        if game.is_game_over():
            show_game_over()
            return
        await asyncio.sleep(1)
        await check_game_state_and_continue()
        return

    ai_level = document.getElementById("ai-level").value
    if ai_level != "none" and game.current_turn == get_ai_color():
        await process_ai_turn(ai_level)


async def process_ai_turn(level):
    update_status_ai_thinking()
    await asyncio.sleep(0.5)

    move = None
    if level == "random":
        move = game.get_random_move()
    elif level == "greedy":
        move = game.get_greedy_move()
    elif level == "hard":
        move = game.get_minimax_move(depth=3)

    if move:
        r, c = move
        game.apply_move(r, c)
        render_board()
        await check_game_state_and_continue()
    else:
        game.switch_turn()
        update_status()
        await check_game_state_and_continue()


def show_game_over():
    black, white = game.get_counts()
    if black > white:
        result = "くろのかち！"
    elif white > black:
        result = "しろのかち！"
    else:
        result = "ひきわけ！"
    document.getElementById("status").innerText = (
        f"対局終了！ {result} (くろ:{black} - しろ:{white})"
    )


def update_status_ai_thinking():
    black, white = game.get_counts()
    document.getElementById("status").innerText = (
        f"AI思考中... | くろ:{black} - しろ:{white}"
    )


def highlight_valid_moves():
    hint_black = document.getElementById("hint-black").value
    hint_white = document.getElementById("hint-white").value

    current_turn = game.current_turn
    show_valid = False
    show_best = False

    if current_turn == OthelloGame.BLACK:
        show_valid = hint_black in ("hints", "best")
        show_best = hint_black == "best"
    else:
        show_valid = hint_white in ("hints", "best")
        show_best = hint_white == "best"

    moves = game.get_valid_moves(current_turn) if (show_valid or show_best) else []
    best_move = game.get_minimax_move(depth=3) if show_best else None

    cells = document.querySelectorAll(".cell")
    for i in range(cells.length):
        r = int(cells[i].dataset.row)
        c = int(cells[i].dataset.col)
        cells[i].classList.remove("valid-move", "best-move")

        if (r, c) in moves:
            if show_valid:
                cells[i].classList.add("valid-move")
            if best_move and (r, c) == best_move:
                cells[i].classList.add("best-move")


def on_toggle_hints(event):
    render_board()


def on_new_game(event):
    init_game()


def on_undo(event):
    if game.undo():
        render_board()


def on_player_color_change(event):
    asyncio.create_task(check_game_state_and_continue())


def on_ai_level_change(event):
    asyncio.create_task(check_game_state_and_continue())


def bind_events():
    document.getElementById("new-game-btn").addEventListener(
        "click", _keep_proxy(on_new_game)
    )
    document.getElementById("undo-btn").addEventListener(
        "click", _keep_proxy(on_undo)
    )
    document.getElementById("hint-black").addEventListener(
        "change", _keep_proxy(on_toggle_hints)
    )
    document.getElementById("hint-white").addEventListener(
        "change", _keep_proxy(on_toggle_hints)
    )
    document.getElementById("player-color").addEventListener(
        "change", _keep_proxy(on_player_color_change)
    )
    document.getElementById("ai-level").addEventListener(
        "change", _keep_proxy(on_ai_level_change)
    )


try:
    bind_events()
    init_game()
except Exception as exc:
    window.console.error("Othello startup failed", str(exc))
    document.getElementById("status").innerText = f"起動エラー: {exc}"
    raise
