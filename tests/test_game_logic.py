import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
from game_logic import OthelloGame
import copy

def test_initial_setup():
    game = OthelloGame()
    black, white = game.get_counts()
    assert black == 2
    assert white == 2
    assert game.board[3][3] == OthelloGame.WHITE
    assert game.board[4][4] == OthelloGame.WHITE
    assert game.board[3][4] == OthelloGame.BLACK
    assert game.board[4][3] == OthelloGame.BLACK
    assert game.current_turn == OthelloGame.BLACK

def test_valid_moves_initial():
    game = OthelloGame()
    moves = game.get_valid_moves(OthelloGame.BLACK)
    expected_moves = {(2, 3), (3, 2), (4, 5), (5, 4)}
    assert set(moves) == expected_moves

def test_apply_move_vertical():
    game = OthelloGame()
    # Apply a move at (2, 3) - should flip (3, 3) which is WHITE
    # Initial: (3,3)=W, (4,3)=B. Move (2,3) B -> sandwich (3,3) with (4,3)
    
    assert game.board[3][3] == OthelloGame.WHITE
    assert game.board[4][3] == OthelloGame.BLACK
    
    success = game.apply_move(2, 3)
    assert success
    assert game.board[2][3] == OthelloGame.BLACK
    assert game.board[3][3] == OthelloGame.BLACK # Flipped
    assert game.current_turn == OthelloGame.WHITE

def test_apply_move_horizontal():
    game = OthelloGame()
    # Apply move at (3, 2). (3,3) is W, (3,4) is B.
    # Move (3,2) B -> sandwich (3,3) with (3,4)
    
    assert game.board[3][3] == OthelloGame.WHITE
    assert game.board[3][4] == OthelloGame.BLACK
    
    success = game.apply_move(3, 2)
    assert success
    assert game.board[3][2] == OthelloGame.BLACK
    assert game.board[3][3] == OthelloGame.BLACK # Flipped
    assert game.current_turn == OthelloGame.WHITE

def test_switch_turn():
    game = OthelloGame()
    assert game.current_turn == OthelloGame.BLACK
    game.switch_turn()
    assert game.current_turn == OthelloGame.WHITE
    game.switch_turn()
    assert game.current_turn == OthelloGame.BLACK

def test_game_over_conditions():
    game = OthelloGame()
    assert not game.is_game_over()
    
    # Fill board with BLACK (artificially)
    game.board = [[OthelloGame.BLACK for _ in range(8)] for _ in range(8)]
    assert game.is_game_over()
    
    # Fill with empty but no moves allowed (e.g. all white surrounded by empty but unconnected?)
    # Easier: just verify that if get_valid_moves returns empty for both, it's game over.
    game.board = [[OthelloGame.EMPTY for _ in range(8)] for _ in range(8)]
    # Place one black at 0,0 and one white at 7,7 (too far to capture)
    game.board[0][0] = OthelloGame.BLACK
    game.board[7][7] = OthelloGame.WHITE
    
    assert len(game.get_valid_moves(OthelloGame.BLACK)) == 0
    assert len(game.get_valid_moves(OthelloGame.WHITE)) == 0
    assert game.is_game_over()

def test_ai_random_move():
    game = OthelloGame()
    move = game.get_random_move()
    assert move in game.get_valid_moves(OthelloGame.BLACK)

def test_undo():
    game = OthelloGame()
    initial_board = copy.deepcopy(game.board)
    game.apply_move(2, 3)
    assert game.board != initial_board
    
    game.undo()
    assert game.board == initial_board
    assert game.current_turn == OthelloGame.BLACK
