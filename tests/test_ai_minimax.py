import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
from game_logic import OthelloGame

def test_ai_minimax_vs_random():
    """Run a game with Minimax AI vs Random AI to check for exceptions and basic logic"""
    game = OthelloGame()
    
    # Limit moves to avoid infinite loops
    max_moves = 64
    moves_count = 0
    
    while not game.is_game_over() and moves_count < max_moves:
        # Minimax (Depth 1 for speed in test) vs Random
        if game.current_turn == OthelloGame.BLACK:
            move = game.get_minimax_move(depth=1)
        else:
            move = game.get_random_move()
        
        if move:
            r, c = move
            success = game.apply_move(r, c)
            assert success, f"AI returned invalid move {move}"
        else:
            # Pass
            game.switch_turn()
            
        moves_count += 1
    
    assert game.is_game_over() or moves_count == max_moves

def test_evaluation_score():
    """Test evaluation function basics"""
    game = OthelloGame()
    # Initial state: equal
    score_black = game.evaluate_board(game.board, OthelloGame.BLACK)
    score_white = game.evaluate_board(game.board, OthelloGame.WHITE)
    assert score_black == score_white # Symmetric start
