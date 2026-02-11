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
        """最も多く取れる手を返す"""
        import copy
        moves = self.get_valid_moves(self.current_turn)
        if not moves:
            return None
        
        best_move = None
        max_flipped = -1
        
        for r, c in moves:
            # シミュレーション
            # apply_moveは盤面を変えてしまうので、カウントだけ計算するロジックが必要だが、
            # 既存のロジックを再利用するために一時的にコピーするか、
            # _get_flips のようなヘルパーメソッドがあれば良い。
            # ここでは簡易的に deepcopy を使う（パフォーマンスは落ちるが実装は楽）
            
            # または apply_move のロジックの一部（ひっくり返る数の計算）を切り出す
            flipped_count = self.count_flips(r, c)
            if flipped_count > max_flipped:
                max_flipped = flipped_count
                best_move = (r, c)
                
        return best_move

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
