class OthelloGame:
    # 定数定義
    EMPTY = 0
    BLACK = 1
    WHITE = 2
    BOARD_SIZE = 8

    def __init__(self):
        """ゲームの初期化"""
        self.board = [[self.EMPTY for _ in range(self.BOARD_SIZE)] for _ in range(self.BOARD_SIZE)]
        self.current_turn = self.BLACK
        self.history = []  # 履歴（アンドゥ用）
        self.initial_setup()

    def initial_setup(self):
        """初期配置（中央に白黒2枚ずつ）"""
        center = self.BOARD_SIZE // 2
        self.board[center - 1][center - 1] = self.WHITE
        self.board[center][center] = self.WHITE
        self.board[center - 1][center] = self.BLACK
        self.board[center][center - 1] = self.BLACK

    def get_valid_moves(self, color):
        """指定された色の有効な手（置ける場所）のリストを返す"""
        moves = []
        for r in range(self.BOARD_SIZE):
            for c in range(self.BOARD_SIZE):
                if self.is_valid_move(r, c, color):
                    moves.append((r, c))
        return moves

    def is_valid_move(self, r, c, color):
        """指定された位置に置けるか判定"""
        if not (0 <= r < self.BOARD_SIZE and 0 <= c < self.BOARD_SIZE):
            return False
        if self.board[r][c] != self.EMPTY:
            return False

        opponent = self.WHITE if color == self.BLACK else self.BLACK
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.BOARD_SIZE and 0 <= nc < self.BOARD_SIZE and self.board[nr][nc] == opponent:
                # 相手の駒が隣にある場合、その先を探索
                while True:
                    nr += dr
                    nc += dc
                    if not (0 <= nr < self.BOARD_SIZE and 0 <= nc < self.BOARD_SIZE):
                        break
                    if self.board[nr][nc] == self.EMPTY:
                        break
                    if self.board[nr][nc] == color:
                        return True  # 自分の駒で挟めた
        return False

    def apply_move(self, r, c):
        """手を実行し、盤面を更新する"""
        if not self.is_valid_move(r, c, self.current_turn):
            return False

        # 履歴に現在の状態を保存（ディープコピーまたは必要なデータのみ）
        self.save_history()

        self.board[r][c] = self.current_turn
        opponent = self.WHITE if self.current_turn == self.BLACK else self.BLACK
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]

        for dr, dc in directions:
            pieces_to_flip = []
            nr, nc = r + dr, c + dc
            while 0 <= nr < self.BOARD_SIZE and 0 <= nc < self.BOARD_SIZE and self.board[nr][nc] == opponent:
                pieces_to_flip.append((nr, nc))
                nr += dr
                nc += dc
            
            if 0 <= nr < self.BOARD_SIZE and 0 <= nc < self.BOARD_SIZE and self.board[nr][nc] == self.current_turn:
                for fr, fc in pieces_to_flip:
                    self.board[fr][fc] = self.current_turn

        self.switch_turn()
        return True

    def switch_turn(self):
        """手番を交代する。パスの判定もここで行うのが一般的だが、UI側で制御しやすくするため単純な交代のみ"""
        self.current_turn = self.WHITE if self.current_turn == self.BLACK else self.BLACK

    def has_valid_move(self):
        """現在の手番プレイヤーに打てる手があるか"""
        return len(self.get_valid_moves(self.current_turn)) > 0

    def get_counts(self):
        """黒と白の石の数をカウント"""
        black = sum(row.count(self.BLACK) for row in self.board)
        white = sum(row.count(self.WHITE) for row in self.board)
        return black, white

    def is_game_over(self):
        """ゲーム終了判定（両者打つ手がない、または盤面が埋まった）"""
        # 手番プレイヤーに手があるか
        if self.has_valid_move():
            return False
        
        # 相手プレイヤーに手があるか確認
        opponent = self.WHITE if self.current_turn == self.BLACK else self.BLACK
        if not self.get_valid_moves(opponent):
            return True
            
        return False

    def save_history(self):
        """アンドゥ用に盤面のコピーを保存"""
        import copy
        self.history.append({
            'board': copy.deepcopy(self.board),
            'turn': self.current_turn
        })

    def undo(self):
        """1手戻る"""
        if self.history:
            state = self.history.pop()
            self.board = state['board']
            self.current_turn = state['turn']
            return True
        return False

    def get_random_move(self):
        """ランダムな有効手を返す"""
        import random
        moves = self.get_valid_moves(self.current_turn)
        if moves:
            return random.choice(moves)
        return None

    def get_greedy_move(self):
        """貪欲法：最も多く石を裏返せる手を選ぶ"""
        valid_moves = self.get_valid_moves(self.current_turn)
        if not valid_moves:
            return None
        
        best_move = None
        max_flips = -1
        
        for r, c in valid_moves:
            flips = self.count_flips(r, c)
            if flips > max_flips:
                max_flips = flips
                best_move = (r, c)
                
        return best_move

    def evaluate_board(self, board, player):
        """盤面評価関数"""
        opponent = self.BLACK if player == self.WHITE else self.WHITE
        
        # 1. 石の数（終盤は重要だが、序中盤はそうでもない）
        player_score = sum(row.count(player) for row in board)
        opponent_score = sum(row.count(opponent) for row in board)
        
        # 2. 確定石の数（簡易的に角のみ）
        corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
        player_corners = sum(1 for r, c in corners if board[r][c] == player)
        opponent_corners = sum(1 for r, c in corners if board[r][c] == opponent)
        
        # 3. 配置（重み付け）
        # 簡易的な重み付け
        weights = [
            [100, -20, 10, 5, 5, 10, -20, 100],
            [-20, -50, -2, -2, -2, -2, -50, -20],
            [10, -2, -1, -1, -1, -1, -2, 10],
            [5, -2, -1, -1, -1, -1, -2, 5],
            [5, -2, -1, -1, -1, -1, -2, 5],
            [10, -2, -1, -1, -1, -1, -2, 10],
            [-20, -50, -2, -2, -2, -2, -50, -20],
            [100, -20, 10, 5, 5, 10, -20, 100],
        ]
        
        position_score = 0
        for r in range(8):
            for c in range(8):
                if board[r][c] == player:
                    position_score += weights[r][c]
                elif board[r][c] == opponent:
                    position_score -= weights[r][c]

        # 総合評価（重みは調整が必要）
        score = (player_score - opponent_score) + (player_corners - opponent_corners) * 1000 + position_score
        return score

    def get_minimax_move(self, depth=3):
        """Minimax法（Alpha-Beta法）で手を選ぶ"""
        best_score = float('-inf')
        best_move = None
        alpha = float('-inf')
        beta = float('inf')
        
        valid_moves = self.get_valid_moves(self.current_turn)
        if not valid_moves:
            return None
            
        # 最初に中央付近や角を優先探索するとAlpha-Beta効率が良いが、今回は単純に探索
        for r, c in valid_moves:
            # 仮想的な盤面を作成して一手進める
            # copy.deepcopyは遅いので、手動でコピーするか、リスト内包表記を使う
            temp_game = OthelloGame() 
            temp_game.board = [row[:] for row in self.board]
            temp_game.current_turn = self.current_turn
            temp_game.apply_move(r, c) # 手番も変わる
            
            # 再帰呼び出し
            # apply_moveで手番が変わっているため、minimaxの呼び出しでは
            # is_maximizing=False (相手のターンなので最小化) となるべきだが、
            # minimax内で「現在の手番」を基準に評価するか、「最大化プレイヤー」を基準に評価するかによる。
            # ここでは minimax(..., maximizing_player=self.current_turn) を渡す。
            # 次の層は相手番なので is_maximizing=False
            score = self.minimax(temp_game, depth - 1, alpha, beta, False, self.current_turn)
            
            if score > best_score:
                best_score = score
                best_move = (r, c)
            
            alpha = max(alpha, best_score)
            
        return best_move

    def minimax(self, game_state, depth, alpha, beta, is_maximizing, maximizing_player):
        if depth == 0 or game_state.is_game_over():
            return self.evaluate_board(game_state.board, maximizing_player)

        valid_moves = game_state.get_valid_moves(game_state.current_turn)
        
        # パスの場合
        if not valid_moves:
            temp_game = OthelloGame()
            temp_game.board = [row[:] for row in game_state.board]
            temp_game.current_turn = game_state.current_turn
            # パスさせる（手番交代のみ）
            temp_game.switch_turn()
            # 手番交代したので、is_maximizingを反転させる？
            # いや、パスは「手が選べない」だけなので、最大化/最小化の役割は交代する
            return self.minimax(temp_game, depth - 1, alpha, beta, not is_maximizing, maximizing_player)

        if is_maximizing:
            max_eval = float('-inf')
            for r, c in valid_moves:
                temp_game = OthelloGame()
                temp_game.board = [row[:] for row in game_state.board]
                temp_game.current_turn = game_state.current_turn
                temp_game.apply_move(r, c)
                
                eval = self.minimax(temp_game, depth - 1, alpha, beta, False, maximizing_player)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for r, c in valid_moves:
                temp_game = OthelloGame()
                temp_game.board = [row[:] for row in game_state.board]
                temp_game.current_turn = game_state.current_turn
                temp_game.apply_move(r, c)
                
                eval = self.minimax(temp_game, depth - 1, alpha, beta, True, maximizing_player)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def count_flips(self, r, c):
        """指定した位置に置いた場合にひっくり返る数を計算"""
        opponent = self.WHITE if self.current_turn == self.BLACK else self.BLACK
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        
        total_flips = 0
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            current_flips = 0
            while 0 <= nr < self.BOARD_SIZE and 0 <= nc < self.BOARD_SIZE and self.board[nr][nc] == opponent:
                current_flips += 1
                nr += dr
                nc += dc
            
            if 0 <= nr < self.BOARD_SIZE and 0 <= nc < self.BOARD_SIZE and self.board[nr][nc] == self.current_turn:
                total_flips += current_flips
                
        return total_flips
