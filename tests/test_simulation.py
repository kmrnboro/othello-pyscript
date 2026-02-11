import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
from game_logic import OthelloGame
import random

def test_ai_vs_ai_random():
    """Run a full game with Random AI vs Random AI to check for exceptions"""
    game = OthelloGame()
    
    # Limit moves to avoid infinite loops if something is wrong (though Othello is finite)
    max_moves = 64
    moves_count = 0
    
    while not game.is_game_over() and moves_count < max_moves:
        # Check current turn
        current_ai_level = "random" # Both are random
        
        # Get move
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
    black, white = game.get_counts()
    # Total pieces should be <= 64, typically close to 64 at end
    assert black + white <= 64
    assert black + white > 4 # At least initial pieces + some moves
