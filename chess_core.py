# Define constants for colors
WHITE = "white"
BLACK = "black"

# Define constants for piece types
PAWN = "pawn"
ROOK = "rook"
KNIGHT = "knight"
BISHOP = "bishop"
QUEEN = "queen"
KING = "king"

class Piece:
    """
    Represents a chess piece.
    """
    def __init__(self, color, piece_type):
        if color not in (WHITE, BLACK):
            raise ValueError("Invalid color for piece")
        if piece_type not in (PAWN, ROOK, KNIGHT, BISHOP, QUEEN, KING):
            raise ValueError("Invalid piece_type for piece")
        self.color = color
        self.piece_type = piece_type
        self.has_moved = False # Useful for castling and pawn's first move

    def __str__(self):
        """
        Provides a simple string representation for the piece,
        e.g., 'wP' for White Pawn, 'bN' for Black Knight.
        """
        type_char = self.piece_type[0].upper()
        if self.piece_type == KNIGHT:
            type_char = 'N'  # Standard algebraic notation for Knight
        return self.color[0].lower() + type_char

    def __repr__(self):
        return f"Piece('{self.color}', '{self.piece_type}')"

def create_initial_board():
    """
    Creates and returns an 8x8 board with pieces in their starting positions.
    """
    board = [[None for _ in range(8)] for _ in range(8)]

    # Place pawns
    for col in range(8):
        board[1][col] = Piece(BLACK, PAWN)
        board[6][col] = Piece(WHITE, PAWN)

    # Place rooks
    board[0][0] = Piece(BLACK, ROOK)
    board[0][7] = Piece(BLACK, ROOK)
    board[7][0] = Piece(WHITE, ROOK)
    board[7][7] = Piece(WHITE, ROOK)

    # Place knights
    board[0][1] = Piece(BLACK, KNIGHT)
    board[0][6] = Piece(BLACK, KNIGHT)
    board[7][1] = Piece(WHITE, KNIGHT)
    board[7][6] = Piece(WHITE, KNIGHT)

    # Place bishops
    board[0][2] = Piece(BLACK, BISHOP)
    board[0][5] = Piece(BLACK, BISHOP)
    board[7][2] = Piece(WHITE, BISHOP)
    board[7][5] = Piece(WHITE, BISHOP)

    # Place queens
    board[0][3] = Piece(BLACK, QUEEN)
    board[7][3] = Piece(WHITE, QUEEN)

    # Place kings
    board[0][4] = Piece(BLACK, KING)
    board[7][4] = Piece(WHITE, KING)

    return board

# Initialize the board
board = create_initial_board()

# Game state dictionary
game_state = {
    "current_player": WHITE,
    "castling_availability": {
        WHITE: {"kingside": True, "queenside": True},  # Corresponds to Kq notation
        BLACK: {"kingside": True, "queenside": True},  # Corresponds to kq notation
    },
    "en_passant_target_square": None,  # Stores as a (row, col) tuple, e.g., (2, 4)
    "halfmove_clock": 0,  # Number of halfmoves since the last capture or pawn advance
    "fullmove_number": 1,  # Starts at 1 and is incremented after Black's move
    "move_history": [], # List of moves made, could store them in algebraic notation or as (from_sq, to_sq)
    "king_positions": { # To quickly find kings for check/checkmate detection
        WHITE: (7, 4),
        BLACK: (0, 4)
    }
}

if __name__ == '__main__':
    # Example of how to print the board
    def print_board_debug(current_board):
        print("  a b c d e f g h")
        print("  ---------------")
        for i, row in enumerate(current_board):
            print(f"{8-i}| {' '.join(str(piece) if piece else '..' for piece in row)}")
        print("  ---------------")
        print("  a b c d e f g h")

    print_board_debug(board)
    print("\nInitial Game State:")
    for key, value in game_state.items():
        print(f"{key}: {value}")

    # Example of accessing a piece
    print(f"\nPiece at e1 (board[7][4]): {board[7][4]}")
    print(f"Piece at d8 (board[0][3]): {board[0][3]}")

    # Example of changing current player
    # game_state["current_player"] = BLACK
    # print(f"\nCurrent player changed to: {game_state['current_player']}")

# --- Helper Functions ---
def is_on_board(row, col):
    """Checks if the given coordinates are within the 8x8 board."""
    return 0 <= row < 8 and 0 <= col < 8

# --- Movement Logic ---
def get_pawn_moves(board, row, col, game_state):
    """
    Calculates all legal moves for a pawn at the given position.
    Does not yet consider if the move would put the king in check.
    """
    moves = []
    piece = board[row][col]
    if not piece or piece.piece_type != PAWN:
        return moves # Should not happen if called correctly

    color = piece.color
    direction = -1 if color == WHITE else 1 # White moves from row 6 to 0, Black from 1 to 7
    start_row = 6 if color == WHITE else 1

    # 1. Single square advance
    one_step_row, one_step_col = row + direction, col
    if is_on_board(one_step_row, one_step_col) and board[one_step_row][one_step_col] is None:
        moves.append(((row, col), (one_step_row, one_step_col)))

        # 2. Two square advance (only if one_step was possible and pawn hasn't moved)
        if row == start_row and not piece.has_moved: # Check has_moved for pawns that might have moved and returned
            two_steps_row = row + 2 * direction
            if is_on_board(two_steps_row, col) and board[two_steps_row][col] is None:
                moves.append(((row, col), (two_steps_row, col)))

    # 3. Diagonal captures
    for d_col in [-1, 1]: # Check left and right diagonal
        capture_row, capture_col = row + direction, col + d_col
        if is_on_board(capture_row, capture_col):
            target_piece = board[capture_row][capture_col]
            if target_piece and target_piece.color != color:
                moves.append(((row, col), (capture_row, capture_col)))

    # 4. En passant
    ep_target = game_state.get("en_passant_target_square")
    if ep_target:
        ep_row, ep_col = ep_target
        # The target square for en passant is the square the opposing pawn *skipped over*.
        # The pawn captures by moving to this skipped-over square.
        # This condition checks if the current pawn is adjacent to the pawn that just made a two-square move
        # and if the en passant target square is the correct diagonal capture for this pawn.
        if ep_row == row + direction and abs(col - ep_col) == 1:
             # Check if the pawn is actually next to the pawn that moved two squares
            pawn_to_capture_row = row
            pawn_to_capture_col = ep_col
            if is_on_board(pawn_to_capture_row, pawn_to_capture_col):
                piece_to_capture = board[pawn_to_capture_row][pawn_to_capture_col]
                if piece_to_capture and piece_to_capture.color != color and \
                   piece_to_capture.piece_type == PAWN:
                    # Check if the double-moved pawn is indeed the one that set up en passant
                    # This requires more state or move history, typically.
                    # For now, we assume if ep_target is set, it's valid if our pawn can attack it.
                    moves.append(((row, col), (ep_row, ep_col)))


    # Pawn promotion will be handled when a move is applied, not just generated.
    return moves

def get_knight_moves(board, row, col):
    """
    Calculates all legal moves for a knight at the given position.
    Does not yet consider if the move would put the king in check.
    """
    moves = []
    piece = board[row][col]
    if not piece or piece.piece_type != KNIGHT:
        return moves

    color = piece.color
    # All 8 possible L-shaped moves for a knight
    knight_move_offsets = [
        (-2, -1), (-2, 1), (-1, -2), (-1, 2),
        (1, -2), (1, 2), (2, -1), (2, 1)
    ]

    for dr, dc in knight_move_offsets:
        target_row, target_col = row + dr, col + dc
        if is_on_board(target_row, target_col):
            target_piece = board[target_row][target_col]
            if target_piece is None or target_piece.color != color:
                moves.append(((row, col), (target_row, target_col)))
    return moves

def _get_sliding_moves(board, row, col, directions):
    """
    Helper function for sliding pieces (Rook, Bishop, Queen).
    `directions` is a list of (dr, dc) tuples indicating directions of movement.
    """
    moves = []
    piece = board[row][col]
    if not piece:
        return moves
    color = piece.color

    for dr, dc in directions:
        for i in range(1, 8): # Max 7 steps in any direction
            target_row, target_col = row + i * dr, col + i * dc
            if not is_on_board(target_row, target_col):
                break # Off board

            target_piece = board[target_row][target_col]
            if target_piece is None:
                moves.append(((row, col), (target_row, target_col)))
            elif target_piece.color != color:
                moves.append(((row, col), (target_row, target_col))) # Capture
                break # Cannot move further in this direction
            else: # Own piece
                break # Blocked by own piece
    return moves

def get_rook_moves(board, row, col):
    """Calculates all legal moves for a rook."""
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)] # Right, Left, Down, Up
    return _get_sliding_moves(board, row, col, directions)

def get_bishop_moves(board, row, col):
    """Calculates all legal moves for a bishop."""
    directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)] # Diagonal
    return _get_sliding_moves(board, row, col, directions)

def get_queen_moves(board, row, col):
    """Calculates all legal moves for a queen."""
    # Queen moves like a rook and a bishop combined
    directions = [
        (0, 1), (0, -1), (1, 0), (-1, 0), # Rook directions
        (1, 1), (1, -1), (-1, 1), (-1, -1)  # Bishop directions
    ]
    return _get_sliding_moves(board, row, col, directions)

def get_king_moves(board, row, col, game_state):
    """
    Calculates all legal moves for a king at the given position.
    Does not yet consider if the move would put the king in check (critical for king moves).
    Castling is also not yet implemented.
    """
    moves = []
    piece = board[row][col]
    if not piece or piece.piece_type != KING:
        return moves

    color = piece.color
    king_move_offsets = [
        (0, 1), (0, -1), (1, 0), (-1, 0), # Horizontal/Vertical
        (1, 1), (1, -1), (-1, 1), (-1, -1)  # Diagonal
    ]

    for dr, dc in king_move_offsets:
        target_row, target_col = row + dr, col + dc
        if is_on_board(target_row, target_col):
            target_piece = board[target_row][target_col]
            if target_piece is None or target_piece.color != color:
                moves.append(((row, col), (target_row, target_col)))

    # TODO: Castling logic will be added here. It needs:
    # 1. King and chosen Rook have not moved.
    # 2. Squares between King and Rook are empty.
    # 3. King is not in check.
    # 4. King does not pass through or land on a square attacked by the opponent.
    # (This requires `is_square_attacked` function)

    # Castling Logic
    # Will be added after is_square_attacked is implemented
    # Needs to check:
    # - King and rook haven't moved (use piece.has_moved and game_state['castling_availability'])
    # - Squares between king and rook are empty
    # - King is not currently in check
    # - King does not pass through an attacked square
    # - King does not land on an attacked square

    # Placeholder for castling moves:
    # if color == WHITE and game_state["castling_availability"][WHITE]["kingside"] and not piece.has_moved:
    #   # Check rook, empty squares, attacked squares...
    #   pass # moves.append(...)
    # if color == WHITE and game_state["castling_availability"][WHITE]["queenside"] and not piece.has_moved:
    #   pass
    # Similar for BLACK

    # Castling Logic
    if not piece.has_moved and not is_square_attacked(board, row, col, BLACK if color == WHITE else WHITE):
        # Kingside Castling
        if game_state["castling_availability"][color]["kingside"]:
            rook_col = 7
            rook = board[row][rook_col]
            if rook and rook.piece_type == ROOK and not rook.has_moved:
                # Check squares between king and rook are empty
                # For white: (row, 5), (row, 6) (f1, g1)
                # For black: (row, 5), (row, 6) (f8, g8)
                if board[row][col+1] is None and board[row][col+2] is None:
                    # Check king doesn't pass through or land on attacked square
                    opponent_color = BLACK if color == WHITE else WHITE
                    if not is_square_attacked(board, row, col+1, opponent_color) and \
                       not is_square_attacked(board, row, col+2, opponent_color):
                        moves.append(((row, col), (row, col+2))) # King's move for castling

        # Queenside Castling
        if game_state["castling_availability"][color]["queenside"]:
            rook_col = 0
            rook = board[row][rook_col]
            if rook and rook.piece_type == ROOK and not rook.has_moved:
                # Check squares between king and rook are empty
                # For white: (row, 1), (row, 2), (row, 3) (b1, c1, d1)
                # For black: (row, 1), (row, 2), (row, 3) (b8, c8, d8)
                if board[row][col-1] is None and board[row][col-2] is None and board[row][col-3] is None:
                    # Check king doesn't pass through or land on attacked square
                    # King moves to col-2 (c1 or c8)
                    # Passes through col-1 (d1 or d8)
                    opponent_color = BLACK if color == WHITE else WHITE
                    if not is_square_attacked(board, row, col-1, opponent_color) and \
                       not is_square_attacked(board, row, col-2, opponent_color):
                        moves.append(((row, col), (row, col-2))) # King's move for castling
    return moves

# --- Attack and Check Logic ---

def is_square_attacked(board, target_row, target_col, attacker_color):
    """
    Checks if a square (target_row, target_col) is attacked by any piece of attacker_color.
    This is crucial for check detection and validating king moves (including castling).
    """
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece and piece.color == attacker_color:
                # Generate pseudo-legal moves for this piece
                # Note: For pawns, we only care about their diagonal attack moves, not forward pushes.
                # The existing get_xxx_moves functions generate all moves, including non-captures.
                # We need to be careful: a pawn doesn't "attack" the square in front of it.

                # A more direct way is to check based on piece type from (r,c) to (target_row, target_col)
                if piece.piece_type == PAWN:
                    direction = -1 if piece.color == WHITE else 1
                    # Pawns attack diagonally forward
                    if target_row == r + direction and (target_col == c + 1 or target_col == c - 1):
                        return True
                elif piece.piece_type == KNIGHT:
                    # Check if (target_row, target_col) is a knight's move from (r,c)
                    knight_move_offsets = [
                        (-2, -1), (-2, 1), (-1, -2), (-1, 2),
                        (1, -2), (1, 2), (2, -1), (2, 1)
                    ]
                    for dr, dc in knight_move_offsets:
                        if r + dr == target_row and c + dc == target_col:
                            return True
                elif piece.piece_type == KING:
                     king_move_offsets = [
                        (0, 1), (0, -1), (1, 0), (-1, 0),
                        (1, 1), (1, -1), (-1, 1), (-1, -1)
                    ]
                     for dr, dc in king_move_offsets:
                        if r + dr == target_row and c + dc == target_col:
                            return True
                elif piece.piece_type == ROOK or piece.piece_type == QUEEN:
                    # Check horizontal/vertical lines of attack
                    if r == target_row or c == target_col: # Potential rook attack
                        is_clear_path = True
                        if r == target_row: # Horizontal
                            step = 1 if target_col > c else -1
                            for cc in range(c + step, target_col, step):
                                if board[r][cc] is not None:
                                    is_clear_path = False
                                    break
                        else: # Vertical
                            step = 1 if target_row > r else -1
                            for rr in range(r + step, target_row, step):
                                if board[rr][c] is not None:
                                    is_clear_path = False
                                    break
                        if is_clear_path:
                            return True
                elif piece.piece_type == BISHOP or piece.piece_type == QUEEN:
                    # Check diagonal lines of attack
                    if abs(r - target_row) == abs(c - target_col): # Potential bishop attack
                        is_clear_path = True
                        dr = 1 if target_row > r else -1
                        dc = 1 if target_col > c else -1
                        cr, cc = r + dr, c + dc
                        while cr != target_row or cc != target_col:
                            if not is_on_board(cr,cc) or board[cr][cc] is not None: # check is_on_board just in case, though should not happen if path is clear
                                is_clear_path = False
                                break
                            cr += dr
                            cc += dc
                        if is_clear_path:
                            return True
    return False


# --- Top-level move generation ---
def get_legal_moves_for_piece(board, row, col, game_state):
    """
    Dispatches to the correct move generation function based on piece type.
    This function will later incorporate checks for whether a move leaves the king in check.
    """
    piece = board[row][col]
    if not piece:
        return []

    ptype = piece.piece_type
    if ptype == PAWN:
        return get_pawn_moves(board, row, col, game_state)
    elif ptype == KNIGHT:
        return get_knight_moves(board, row, col)
    elif ptype == BISHOP:
        return get_bishop_moves(board, row, col)
    elif ptype == ROOK:
        return get_rook_moves(board, row, col)
    elif ptype == QUEEN:
        return get_queen_moves(board, row, col)
    elif ptype == KING:
        return get_king_moves(board, row, col, game_state) # game_state needed for castling
    return []

# --- Game Logic: Applying Moves and Generating All Legal Moves ---
import copy # For deep copying board and game_state

def _apply_move_to_board(board_state, game_st, move, promotion_piece_type=None):
    """
    Applies a given move to a DEEP COPIED board and game state.
    Modifies the board_state and game_st in place.
    `move` is a tuple ((from_row, from_col), (to_row, to_col)).
    `promotion_piece_type` is the type to promote a pawn to (e.g., QUEEN).
    This function is primarily for simulating moves. A more complete version
    would update all aspects of game_state (halfmove clock, en passant, etc.).
    """
    from_row, from_col = move[0]
    to_row, to_col = move[1]
    piece = board_state[from_row][from_col]

    if not piece: # Should not happen if called with a valid move
        return

    # Basic move
    board_state[to_row][to_col] = piece
    board_state[from_row][from_col] = None
    original_has_moved = piece.has_moved
    piece.has_moved = True

    # Update king position if king moved
    if piece.piece_type == KING:
        game_st["king_positions"][piece.color] = (to_row, to_col)

    # Handle castling (rook movement)
    if piece.piece_type == KING and abs(from_col - to_col) == 2: # King moved 2 squares
        if to_col > from_col: # Kingside castling (e.g., e1g1 or e8g8)
            rook = board_state[from_row][7]
            board_state[from_row][5] = rook # Rook moves to f1/f8
            board_state[from_row][7] = None
            if rook: rook.has_moved = True
        else: # Queenside castling (e.g., e1c1 or e8c8)
            rook = board_state[from_row][0]
            board_state[from_row][3] = rook # Rook moves to d1/d8
            board_state[from_row][0] = None
            if rook: rook.has_moved = True

    # Handle en passant capture (removing the captured pawn)
    # The moving pawn moves to game_st['en_passant_target_square']
    # The captured pawn is at (from_row, to_col) for white, (from_row, to_col) for black.
    # More simply, if ep_target is set and this move is a pawn moving to ep_target:
    if piece.piece_type == PAWN and game_st.get("en_passant_target_square") == (to_row, to_col):
        # The captured pawn is on the same rank as the attacking pawn's original square,
        # and the same file as the en passant target square.
        captured_pawn_row = from_row
        captured_pawn_col = to_col
        board_state[captured_pawn_row][captured_pawn_col] = None

    # Handle pawn promotion
    if piece.piece_type == PAWN:
        if (piece.color == WHITE and to_row == 0) or \
           (piece.color == BLACK and to_row == 7):
            promo_type = promotion_piece_type if promotion_piece_type else QUEEN # Default to Queen
            board_state[to_row][to_col] = Piece(piece.color, promo_type)
            board_state[to_row][to_col].has_moved = True # Promoted piece is considered "moved"

    # For simulation, we don't need to update full game_state like halfmove clock,
    # en_passant_target_square for the *next* turn, or castling availability.
    # However, for a real move, these would be updated here.
    # For now, this is enough for check validation.


def get_all_truly_legal_moves_for_color(current_board, color_to_move, current_game_state):
    """
    Generates all truly legal moves for the given color.
    A move is truly legal if it does not leave the player's own king in check.
    """
    truly_legal_moves = []
    opponent_color = BLACK if color_to_move == WHITE else WHITE

    # Ensure king_positions is up-to-date before starting, though it should be.
    # This can be a source of bugs if not handled carefully after each real move.
    current_king_pos = current_game_state["king_positions"].get(color_to_move)
    if not current_king_pos or not is_on_board(current_king_pos[0], current_king_pos[1]) or \
       not current_board[current_king_pos[0]][current_king_pos[1]] or \
       current_board[current_king_pos[0]][current_king_pos[1]].piece_type != KING or \
       current_board[current_king_pos[0]][current_king_pos[1]].color != color_to_move:
        # Fallback: find the king if not correctly tracked. This is a safeguard.
        found_king = False
        for r_idx in range(8):
            for c_idx in range(8):
                p = current_board[r_idx][c_idx]
                if p and p.piece_type == KING and p.color == color_to_move:
                    current_game_state["king_positions"][color_to_move] = (r_idx, c_idx)
                    found_king = True
                    break
            if found_king: break
        if not found_king:
             # This should ideally not happen in a consistent game state
            # print(f"Error: King for {color_to_move} not found on board for legal move generation.")
            return []


    for r in range(8):
        for c in range(8):
            piece = current_board[r][c]
            if piece and piece.color == color_to_move:
                # Get pseudo-legal moves (includes castling, doesn't check for self-check yet)
                pseudo_legal_moves = get_legal_moves_for_piece(current_board, r, c, current_game_state)

                for move in pseudo_legal_moves:
                    # Simulate the move on a deep copy of the board and game state
                    # print(f"Simulating move: {move} for piece {piece} at ({r},{c})")

                    board_copy = copy.deepcopy(current_board)
                    game_state_copy = copy.deepcopy(current_game_state) # Important for king_positions and future state like en_passant

                    # Apply the move to the copied board and game state
                    # The _apply_move_to_board needs to handle king position updates within game_state_copy
                    _apply_move_to_board(board_copy, game_state_copy, move)

                    # Find the king of the current color on the copied board
                    # game_state_copy["king_positions"] should have been updated by _apply_move_to_board if king moved
                    king_pos_after_move = game_state_copy["king_positions"][color_to_move]

                    # Check if the king is attacked on the copied board
                    if not is_square_attacked(board_copy, king_pos_after_move[0], king_pos_after_move[1], opponent_color):
                        truly_legal_moves.append(move)
                    # else:
                        # print(f"  Move {move} results in check. King at {king_pos_after_move}, attacked by {opponent_color}")
                        # print_board_debug(board_copy)


    return truly_legal_moves

# --- Checkmate and Stalemate Detection ---
def is_king_in_check(board, king_color, game_state):
    """Checks if the specified king is currently in check."""
    king_pos = game_state["king_positions"].get(king_color)
    if not king_pos: # Should not happen in a valid game state
        # Fallback to find king if not tracked, for robustness during testing
        for r_idx in range(8):
            for c_idx in range(8):
                p = board[r_idx][c_idx]
                if p and p.piece_type == KING and p.color == king_color:
                    king_pos = (r_idx, c_idx)
                    game_state["king_positions"][king_color] = king_pos # Update state
                    break
            if king_pos: break
        if not king_pos: return False # King not on board, should not happen

    opponent_color = BLACK if king_color == WHITE else WHITE
    return is_square_attacked(board, king_pos[0], king_pos[1], opponent_color)

def is_checkmate(board, color_to_move, game_state):
    """Checks if the player (color_to_move) is in checkmate."""
    if not is_king_in_check(board, color_to_move, game_state):
        return False # Not in check, so cannot be checkmate

    # If in check, see if there are any legal moves
    legal_moves = get_all_truly_legal_moves_for_color(board, color_to_move, game_state)
    return not legal_moves # Checkmate if in check and no legal moves

def is_stalemate(board, color_to_move, game_state):
    """Checks if the player (color_to_move) is in stalemate."""
    if is_king_in_check(board, color_to_move, game_state):
        return False # In check, so not stalemate (could be checkmate or playable)

    # Not in check, see if there are any legal moves
    legal_moves = get_all_truly_legal_moves_for_color(board, color_to_move, game_state)
    return not legal_moves # Stalemate if not in check and no legal moves


# TODO: Implement apply_real_move function that updates the actual game state comprehensively.
# This will handle:
# - Updating piece.has_moved
# - Setting en_passant_target_square for the next turn
# - Updating castling_availability if king or rooks move
# - Updating halfmove_clock (for 50-move rule)
# - Incrementing fullmove_number
# - Switching current_player
# - Storing move in history

def apply_real_move(board, game_st, move, promotion_choice=None):
    """
    Applies a move to the actual game board and updates the game state.
    Assumes the move is legal.
    `move` is ((from_row, from_col), (to_row, to_col))
    `promotion_choice` is a piece type like QUEEN, ROOK, etc.
    """
    from_row, from_col = move[0]
    to_row, to_col = move[1]
    piece = board[from_row][from_col]

    if not piece: # Should not happen with a legal, validated move
        # print("Error: No piece to move in apply_real_move")
        return

    moving_piece_color = piece.color
    moving_piece_type = piece.piece_type
    captured_piece = board[to_row][to_col] # Could be None

    is_pawn_move = moving_piece_type == PAWN
    is_capture = captured_piece is not None

    # --- Pre-move state updates ---
    # 1. Clear previous en passant target square (it's only valid for one turn)
    previous_ep_target = game_st.pop("en_passant_target_square", None) # Use pop to ensure it's removed or None

    # --- Execute the move on the board ---
    board[to_row][to_col] = piece
    board[from_row][from_col] = None

    # --- Handle special move consequences ---
    # 2. Pawn's Two-Square Advance: Set new en passant target
    if is_pawn_move and abs(from_row - to_row) == 2:
        game_st["en_passant_target_square"] = ( (from_row + to_row) // 2, from_col )

    # 3. En Passant Capture: Remove the captured pawn
    # This happens if a pawn moves to the square that *was* the en_passant_target_square
    if is_pawn_move and (to_row, to_col) == previous_ep_target:
        # The captured pawn is on the same rank as the attacking pawn's original square,
        # and the same file as the en passant target square (which is to_col).
        captured_pawn_row = from_row
        board[captured_pawn_row][to_col] = None
        is_capture = True # En passant is a capture for halfmove clock purposes

    # 4. Castling: Move the rook
    if moving_piece_type == KING and abs(from_col - to_col) == 2:
        rook_from_col = 7 if to_col > from_col else 0 # Kingside or Queenside
        rook_to_col = 5 if to_col > from_col else 3   # f1/f8 or d1/d8
        rook = board[from_row][rook_from_col]
        if rook and rook.piece_type == ROOK:
            board[from_row][rook_to_col] = rook
            board[from_row][rook_from_col] = None
            rook.has_moved = True
        # is_capture remains False, is_pawn_move remains False for castling

    # 5. Pawn Promotion
    if is_pawn_move and ( (moving_piece_color == WHITE and to_row == 0) or \
                          (moving_piece_color == BLACK and to_row == 7) ):
        promo_type = promotion_choice if promotion_choice in [QUEEN, ROOK, BISHOP, KNIGHT] else QUEEN
        promoted_piece = Piece(moving_piece_color, promo_type)
        promoted_piece.has_moved = True # The new piece is considered to have "moved"
        board[to_row][to_col] = promoted_piece
        # is_pawn_move is still true for halfmove clock reset. is_capture could be true if promotion was a capture.

    # --- Update piece.has_moved for the primary moving piece ---
    # (Rook in castling is handled above, promoted piece is new)
    if not piece.has_moved: # Check original piece, not potentially promoted one
        piece.has_moved = True


    # --- Update game_state ---
    # 6. King Positions
    if moving_piece_type == KING:
        game_st["king_positions"][moving_piece_color] = (to_row, to_col)

    # 7. Castling Availability
    # If king moved
    if moving_piece_type == KING:
        game_st["castling_availability"][moving_piece_color]["kingside"] = False
        game_st["castling_availability"][moving_piece_color]["queenside"] = False
    # If a rook moved from its starting square
    # White rooks: (7,0) for Queenside, (7,7) for Kingside
    # Black rooks: (0,0) for Queenside, (0,7) for Kingside
    if moving_piece_type == ROOK:
        if moving_piece_color == WHITE:
            if from_row == 7 and from_col == 0: game_st["castling_availability"][WHITE]["queenside"] = False
            if from_row == 7 and from_col == 7: game_st["castling_availability"][WHITE]["kingside"] = False
        elif moving_piece_color == BLACK:
            if from_row == 0 and from_col == 0: game_st["castling_availability"][BLACK]["queenside"] = False
            if from_row == 0 and from_col == 7: game_st["castling_availability"][BLACK]["kingside"] = False
    # If a rook is captured on its starting square
    if captured_piece and captured_piece.piece_type == ROOK:
        cap_color = captured_piece.color
        if cap_color == WHITE:
            if to_row == 7 and to_col == 0: game_st["castling_availability"][WHITE]["queenside"] = False
            if to_row == 7 and to_col == 7: game_st["castling_availability"][WHITE]["kingside"] = False
        elif cap_color == BLACK:
            if to_row == 0 and to_col == 0: game_st["castling_availability"][BLACK]["queenside"] = False
            if to_row == 0 and to_col == 7: game_st["castling_availability"][BLACK]["kingside"] = False


    # 8. Halfmove Clock (for 50-move rule)
    if is_pawn_move or is_capture:
        game_st["halfmove_clock"] = 0
    else:
        game_st["halfmove_clock"] += 1

    # 9. Fullmove Number (incremented after Black's move)
    if moving_piece_color == BLACK:
        game_st["fullmove_number"] += 1

    # 10. Move History (simple representation for now)
    # TODO: Convert to algebraic notation later if needed
    move_repr = {
        "from": (from_row, from_col),
        "to": (to_row, to_col),
        "piece": str(piece), # Original piece string before promotion
        "promotion": promotion_choice if promotion_choice and is_pawn_move and \
                                        ((moving_piece_color == WHITE and to_row == 0) or \
                                         (moving_piece_color == BLACK and to_row == 7)) else None,
        "captured": str(captured_piece) if captured_piece else None,
        # Could add flags for check, checkmate, castling etc.
    }
    game_st["move_history"].append(move_repr)

    # 11. Switch Current Player
    game_st["current_player"] = BLACK if moving_piece_color == WHITE else WHITE

    # Note: Insufficient material for draw (e.g., K vs K, K vs KB, K vs KN) is not handled here yet.
    # Threefold repetition is also not handled here.


if __name__ == '__main__':
    # Example of how to print the board
    def print_board_debug(current_board):
        print("\n  a b c d e f g h")
        print("  -----------------")
        for i, r in enumerate(current_board):
            print(f"{8-i}| {' '.join(str(p) if p else '..' for p in r)}")
        print("  -----------------")
        print("  a b c d e f g h")

    print_board_debug(board)
    print("\nInitial Game State:")
    for key, value in game_state.items():
        print(f"{key}: {value}")

    print(f"\nPiece at e1 (board[7][4]): {board[7][4]} ({repr(board[7][4])})")
    print(f"Piece at d8 (board[0][3]): {board[0][3]} ({repr(board[0][3])})")

    # Test pawn moves
    print("\n--- Pawn Move Tests ---")
    # White pawn e2
    e2_pawn_moves = get_pawn_moves(board, 6, 4, game_state) # e2 is (6,4)
    print(f"Moves for White pawn at e2 (6,4): {e2_pawn_moves}") # Expected: [((6,4),(5,4)), ((6,4),(4,4))]

    # Black pawn d7
    d7_pawn_moves = get_pawn_moves(board, 1, 3, game_state) # d7 is (1,3)
    print(f"Moves for Black pawn at d7 (1,3): {d7_pawn_moves}") # Expected: [((1,3),(2,3)), ((1,3),(3,3))]

    # Test capture scenario
    board_capture_test = create_initial_board()
    board_capture_test[5][4] = None # Clear e3
    board_capture_test[4][4] = None # Clear e4
    board_capture_test[3][3] = Piece(BLACK, PAWN) # Black pawn on d5
    board_capture_test[3][5] = Piece(BLACK, PAWN) # Black pawn on f5
    # White pawn e2 moves to e4
    # board_capture_test[6][4].has_moved = True # Not strictly needed for get_pawn_moves
    # board_capture_test[4][4] = board_capture_test[6][4]
    # board_capture_test[6][4] = None
    # print_board_debug(board_capture_test)
    # d5_pawn_moves = get_pawn_moves(board_capture_test, 3, 3, game_state) # Black pawn at d5
    # print(f"Moves for Black pawn at d5 (3,3) after e4: {d5_pawn_moves}")

    # Simulate a white pawn on e4, black pawn on d5
    board_diag_test = create_initial_board()
    board_diag_test[4][4] = Piece(WHITE, PAWN) # White pawn on e4 (4,4)
    board_diag_test[4][4].has_moved = True
    board_diag_test[3][3] = Piece(BLACK, PAWN) # Black pawn on d5 (3,3)
    board_diag_test[3][3].has_moved = True
    board_diag_test[6][4] = None # remove original e2 pawn
    board_diag_test[1][3] = None # remove original d7 pawn
    print_board_debug(board_diag_test)
    e4_pawn_diag_moves = get_pawn_moves(board_diag_test, 4, 4, game_state)
    print(f"Moves for White pawn at e4 (4,4) with Black pawn at d5: {e4_pawn_diag_moves}") # Expected: [((4,4),(3,4)), ((4,4),(3,3))]

    # Test en passant
    # Scenario: White pawn on e2, Black pawn on d7.
    # 1. White e2-e4. (board[6][4] -> board[4][4]), game_state["en_passant_target_square"] = (5,4)
    # 2. Now check moves for Black pawn on d4 (moved from d5 for test) if it were adjacent
    board_ep_test = create_initial_board()
    # Move white e2 pawn to e4
    white_e_pawn = board_ep_test[6][4]
    white_e_pawn.has_moved = True
    board_ep_test[4][4] = white_e_pawn
    board_ep_test[6][4] = None

    # Place a black pawn on d4 (for testing en passant capture of e-pawn)
    # Normally this black pawn would be on d5 and would capture e.p. if white pawn on e5 had moved from e7
    # Let's set up a more canonical en passant:
    # White pawn on e5 (moved from e2->e4->e5)
    # Black pawn on d7 moves to d5. Now white pawn on e5 can capture en passant.

    # Setup: White pawn c2-c4. Black pawn d7-d5. White c4-c5. Black d5 takes e.p. c6.
    # Simpler: White pawn on e5. Black pawn from d7 moves to d5.
    # `game_state` for en passant after black d7-d5
    gs_ep_black_move = game_state.copy() # Don't modify original
    gs_ep_black_move["en_passant_target_square"] = (2,3) # d6, if black pawn moved d7-d5 (1,3)->(3,3)

    # Let's test the example from Wikipedia: White pawn on c5, Black pawn on b7 moves to b5.
    # White can capture en passant on b6.
    # board_ep_test has standard setup.
    # Move white c-pawn to c5
    board_ep_test[6][2] = None # clear c2
    board_ep_test[3][2] = Piece(WHITE, PAWN) # White pawn on c5 (row 3, col 2)
    board_ep_test[3][2].has_moved = True

    # Black b-pawn is at (1,1) (b7). Imagine it just moved to (3,1) (b5).
    # So, en_passant_target_square would be (2,1) (b6)
    gs_ep_test_wiki = game_state.copy()
    gs_ep_test_wiki["en_passant_target_square"] = (2,1) # b6
    gs_ep_test_wiki["current_player"] = WHITE # White's turn to capture

    # The pawn that can capture is the white pawn on c5.
    # It will try to capture the black pawn that *would be* on b5 (row 3, col 1)
    # by moving to b6 (row 2, col 1)
    # For get_pawn_moves, the black pawn on b5 must exist.
    board_ep_test[1][1] = None # clear original b7 pawn
    board_ep_test[3][1] = Piece(BLACK, PAWN) # Black pawn on b5 (row 3, col 1)
    board_ep_test[3][1].has_moved = True # It just moved two squares

    print_board_debug(board_ep_test)
    print(f"Game state for EP test: en_passant_target_square = {gs_ep_test_wiki['en_passant_target_square']}")
    c5_pawn_ep_moves = get_pawn_moves(board_ep_test, 3, 2, gs_ep_test_wiki)
    print(f"Moves for White pawn at c5 (3,2) with EP target b6 (2,1): {c5_pawn_ep_moves}")
    # Expected: advance to c6 ((3,2),(2,2)), capture on b6 ((3,2),(2,1))

    # Test a white pawn on e5 (4,4) -> (3,4) if black pawn on d7 (1,3) just moved to d5 (3,3)
    # en_passant_target_square would be (2,3)
    board_ep_white_capture = create_initial_board()
    # White pawn on e5 (simulating it moved there)
    wp_e5 = Piece(WHITE, PAWN)
    wp_e5.has_moved = True
    board_ep_white_capture[3][4] = wp_e5 # White pawn at e5 (3,4)
    board_ep_white_capture[6][4] = None # clear original e2

    # Black pawn on d5 (simulating it just moved from d7)
    bp_d5 = Piece(BLACK, PAWN)
    bp_d5.has_moved = True # This implies it could have made a double move
    board_ep_white_capture[3][3] = bp_d5 # Black pawn at d5 (3,3)
    board_ep_white_capture[1][3] = None # clear original d7

    gs_ep_white_capture_state = game_state.copy()
    gs_ep_white_capture_state["en_passant_target_square"] = (2,3) # d6, because black pawn moved d7->d5
    gs_ep_white_capture_state["current_player"] = WHITE

    print_board_debug(board_ep_white_capture)
    print(f"Game state for white EP capture: {gs_ep_white_capture_state['en_passant_target_square']}")
    white_e5_moves = get_pawn_moves(board_ep_white_capture, 3, 4, gs_ep_white_capture_state)
    print(f"Moves for White pawn at e5 (3,4) with EP target d6 (2,3): {white_e5_moves}")
    # Expected: e5-e6 ((3,4),(2,4)), e5xd6 en passant ((3,4),(2,3))
    # Plus any captures of other pieces if they were there, e.g. on f6.
    # board_ep_white_capture[2][5] = Piece(BLACK, ROOK) # Black rook on f6
    # print_board_debug(board_ep_white_capture)
    # white_e5_moves_with_capture = get_pawn_moves(board_ep_white_capture, 3, 4, gs_ep_white_capture_state)
    # print(f"Moves for White pawn at e5 (3,4) with EP target d6 and Rook on f6: {white_e5_moves_with_capture}")
