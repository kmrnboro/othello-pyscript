from pyscript import document, window
import js
import asyncio
from game_logic import OthelloGame

game = None

def init_game():
    global game
    print("Initialize Othello/Reversi...")
    game = OthelloGame()
    js.console.log("Game Initialized", game.get_counts())
    render_board()
    asyncio.create_task(check_game_state_and_continue())

def render_board():
    """HTML盤面の描画更新"""
    board_el = document.getElementById("game-board")
    
    # 初回生成（空の場合）
    if board_el.childElementCount == 0:
        for r in range(8):
            for c in range(8):
                cell_div = document.createElement("div")
                cell_div.className = "cell"
                cell_div.dataset.row = str(r)
                cell_div.dataset.col = str(c)
                
                # 石を表す要素
                piece_div = document.createElement("div")
                piece_div.className = "piece"
                cell_div.appendChild(piece_div)

                # クリックイベント
                def on_cell_click(event, r=r, c=c):
                     asyncio.create_task(handle_click(r, c))

                from pyodide.ffi.wrappers import add_event_listener
                add_event_listener(cell_div, "click", on_cell_click)
                
                board_el.appendChild(cell_div)

    # 盤面更新
    cells = document.querySelectorAll(".cell")
    for i in range(len(cells)):
        r = int(cells[i].dataset.row)
        c = int(cells[i].dataset.col)
        cell_val = game.board[r][c]
        
        # クラスのリセット（black/white削除）
        cells[i].classList.remove("black", "white", "valid-move")
        
        if cell_val == OthelloGame.BLACK:
            cells[i].classList.add("black")
        elif cell_val == OthelloGame.WHITE:
            cells[i].classList.add("white")

    update_status()
    highlight_valid_moves()

def get_ai_color():
    """AIの色を取得（プレイヤーの逆）"""
    player_color = document.getElementById("player-color").value
    return OthelloGame.WHITE if player_color == "black" else OthelloGame.BLACK

def update_status():
    """ステータス表示更新"""
    current = "くろ" if game.current_turn == OthelloGame.BLACK else "しろ"
    black, white = game.get_counts()
    status_text = f"じゅんばん: {current} | くろ: {black} | しろ: {white}"
    if not game.has_valid_move() and not game.is_game_over():
         status_text += " (パス！)"
    document.getElementById("status").innerText = status_text

async def handle_click(r, c):
    """セルクリック時の処理"""
    if game.is_game_over():
        return

    # AIの手番中は操作無効
    ai_level = document.getElementById("ai-level").value
    if ai_level != "none" and game.current_turn == get_ai_color():
        return

    if game.apply_move(r, c):
        js.console.log(f"Move applied: {r}, {c}")
        render_board()
        await check_game_state_and_continue()

async def check_game_state_and_continue():
    """ゲーム状態を確認し、必要なら次へ進む（AIターンなど）"""
    if game.is_game_over():
        show_game_over()
        return

    if not game.has_valid_move():
        js.console.log("No valid moves, switching turn")
        game.switch_turn()
        update_status() 
        render_board()
        if game.is_game_over(): # パスして相手も打てない場合
             show_game_over()
             return
        # パスしたので再度チェック（ループする可能性があるので注意だが、Othelloは無限ループしない）
        # ここで再帰的に呼ぶとAIとのパス合戦でスタック溢れるかもだが、数回なのでOK
        await asyncio.sleep(1) # パス表示のためのウェイト
        await check_game_state_and_continue()
        return

    # AIのターンかチェック
    ai_level = document.getElementById("ai-level").value
    if ai_level != "none" and game.current_turn == get_ai_color():
        await process_ai_turn(ai_level)

async def process_ai_turn(level):
    """AIの思考ルーチン"""
    update_status_ai_thinking()
    await asyncio.sleep(0.5) # 思考時間演出

    move = None
    if level == "random":
        move = game.get_random_move()
    elif level == "greedy":
        move = game.get_greedy_move()
    elif level == "hard":
        # 本番の思考は少し深めにしても良いが、ブラウザでの動作を考慮して3か4
        move = game.get_minimax_move(depth=3)
    
    if move:
        r, c = move
        game.apply_move(r, c)
        render_board()
        await check_game_state_and_continue()
    else:
        # AIパス
        game.switch_turn()
        update_status()
        await check_game_state_and_continue()

def show_game_over():
    black, white = game.get_counts()
    winner_text = "ひきわけ"
    if black > white:
        winner_text = "くろ"
    elif white > black:
        winner_text = "しろ"
    
    document.getElementById("status").innerText = f"対局終了！ {winner_text}のかち！ (くろ:{black} - しろ:{white})"

def update_status_ai_thinking():
    black, white = game.get_counts()
    document.getElementById("status").innerText = f"AI思考中... | くろ:{black} - しろ:{white}"

def highlight_valid_moves():
    """有効手のハイライト処理"""
    # ドロップダウンの状態を確認
    hint_black = document.getElementById("hint-black").value
    hint_white = document.getElementById("hint-white").value

    current_turn = game.current_turn
    
    # ヒントを表示すべきか判定
    show_valid = False
    show_best = False
    
    if current_turn == OthelloGame.BLACK:
        if hint_black in ["hints", "best"]:
            show_valid = True
        if hint_black == "best":
            show_best = True
    elif current_turn == OthelloGame.WHITE:
        if hint_white in ["hints", "best"]:
            show_valid = True
        if hint_white == "best":
            show_best = True

    moves = []
    if show_valid or show_best:
        moves = game.get_valid_moves(current_turn)

    cells = document.querySelectorAll(".cell")
    
    # ベストムーブの計算（Greedy -> Minimax）
    best_move = None
    if show_best:
        # ヒント用は深さを浅くしてレスポンス優先（それでも3あれば十分強い）
        best_move = game.get_minimax_move(depth=3)

    for i in range(len(cells)):
        r = int(cells[i].dataset.row)
        c = int(cells[i].dataset.col)
        
        # 既存のクラス削除
        cells[i].classList.remove("valid-move", "best-move")
        
        if (r, c) in moves:
            if show_valid:
                cells[i].classList.add("valid-move")
            
            if best_move and r == best_move[0] and c == best_move[1]:
                cells[i].classList.add("best-move")

def on_toggle_hints(event):
    # ヒント計算は少し重い可能性があるので、非同期でUIブロックを避ける工夫ができれば良いが、
    # 簡易実装としてそのまま呼び出す（depth=3なら一瞬のはず）
    render_board()

def on_new_game(event):
    """新規ゲーム開始"""
    init_game()

def on_undo(event):
    """1手戻す"""
    if game.undo():
        render_board()

async def on_player_color_change(event):
    """プレイヤーの色変更時、AIの手番になる可能性があるためチェック"""
    await check_game_state_and_continue()

init_game()

# イベントリスナーの設定
from pyodide.ffi.wrappers import add_event_listener
add_event_listener(document.getElementById("new-game-btn"), "click", on_new_game)
add_event_listener(document.getElementById("undo-btn"), "click", on_undo)
add_event_listener(document.getElementById("hint-black"), "change", on_toggle_hints)
add_event_listener(document.getElementById("hint-white"), "change", on_toggle_hints)
add_event_listener(document.getElementById("player-color"), "change", on_player_color_change)
