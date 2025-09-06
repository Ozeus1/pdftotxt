import chess_core

def print_board(board_to_print, perspective=chess_core.WHITE):
    """
    Prints the chess board to the console from a given perspective.
    `perspective` determines if row 8 is at the top (WHITE) or row 1 (BLACK).
    """
    if perspective == chess_core.WHITE:
        files = "  a b c d e f g h"
        rank_range = range(8) # 0-7 for rows
        border = "  -----------------"
    else: # Black's perspective
        files = "  h g f e d c b a" # Reverse files
        rank_range = range(7, -1, -1) # 7-0 for rows
        border = "  -----------------"

    print(files)
    print(border)

    for r_idx in rank_range:
        row_str = f"{8-r_idx if perspective == chess_core.WHITE else r_idx+1}|" # Rank numbers

        # Iterate through columns based on perspective
        col_indices = range(8) if perspective == chess_core.WHITE else range(7, -1, -1)

        for c_idx in col_indices:
            piece = board_to_print[r_idx][c_idx]
            row_str += f" {str(piece) if piece else '..'}"
        row_str += f" |{8-r_idx if perspective == chess_core.WHITE else r_idx+1}" # Rank numbers again
        print(row_str)

    print(border)
    print(files)

def square_to_coords(square_notation):
    """
    Converts algebraic square notation (e.g., "e4") to (row, col) tuple.
    Returns None if invalid.
    """
    square_notation = square_notation.lower().strip()
    if len(square_notation) != 2:
        return None

    file_char = square_notation[0]
    rank_char = square_notation[1]

    if not ('a' <= file_char <= 'h' and '1' <= rank_char <= '8'):
        return None

    col = ord(file_char) - ord('a')
    row = 8 - int(rank_char) # Chess ranks are 1-8 from bottom up; list index is 0-7 from top down

    if not (0 <= row < 8 and 0 <= col < 8): # Should be caught by above, but good sanity check
        return None

    return row, col

def parse_move_input(input_str, board, current_player_color, game_state):
    """
    Parses user move input (e.g., "e2e4", "e7e8q", "O-O", "O-O-O").
    Returns a move tuple ((from_row, from_col), (to_row, to_col)) and promotion piece type if any.
    Returns None, None if input is invalid or ambiguous.
    """
    input_str = input_str.strip().lower()

    # Handle castling first as it's special
    if input_str == "o-o" or input_str == "0-0": # Kingside castling
        king_row = 7 if current_player_color == chess_core.WHITE else 0
        king_col = 4 # 'e' file
        # Check if this castling move is legal by seeing if get_king_moves generates it
        king_moves = chess_core.get_king_moves(board, king_row, king_col, game_state)
        castle_move = ((king_row, king_col), (king_row, king_col + 2))
        if castle_move in king_moves:
            return castle_move, None
        else:
            # print("Debug: Kingside castling o-o not found in king_moves")
            return None, None

    if input_str == "o-o-o" or input_str == "0-0-0": # Queenside castling
        king_row = 7 if current_player_color == chess_core.WHITE else 0
        king_col = 4 # 'e' file
        king_moves = chess_core.get_king_moves(board, king_row, king_col, game_state)
        castle_move = ((king_row, king_col), (king_row, king_col - 2))
        if castle_move in king_moves:
            return castle_move, None
        else:
            # print("Debug: Queenside castling o-o-o not found in king_moves")
            return None, None

    if len(input_str) < 4 or len(input_str) > 5:
        return None, None

    from_sq_str = input_str[0:2]
    to_sq_str = input_str[2:4]

    from_coords = square_to_coords(from_sq_str)
    to_coords = square_to_coords(to_sq_str)

    if not from_coords or not to_coords:
        return None, None

    promotion_piece_type = None
    if len(input_str) == 5:
        promo_char = input_str[4]
        if promo_char == 'q': promotion_piece_type = chess_core.QUEEN
        elif promo_char == 'r': promotion_piece_type = chess_core.ROOK
        elif promo_char == 'b': promotion_piece_type = chess_core.BISHOP
        elif promo_char == 'n': promotion_piece_type = chess_core.KNIGHT
        else:
            return None, None # Invalid promotion character

        # Validate if promotion is even possible for this move
        piece_at_from = board[from_coords[0]][from_coords[1]]
        if not piece_at_from or piece_at_from.piece_type != chess_core.PAWN:
            return None, None # Only pawns can promote

        promotion_rank = 0 if piece_at_from.color == chess_core.WHITE else 7
        if to_coords[0] != promotion_rank:
            return None, None # Pawn not reaching promotion rank

    return (from_coords, to_coords), promotion_piece_type


def get_player_move(board, current_player_color, game_state):
    """
    Prompts the current player for their move and parses it.
    Keeps asking until a syntactically valid move format is entered.
    Does not validate if the move is legal on the board, only format.
    """
    while True:
        try:
            player_input = input(f"{current_player_color.capitalize()}'s turn. Enter move (e.g., e2e4, e7e8q, O-O): ")
            parsed_move, promotion = parse_move_input(player_input, board, current_player_color, game_state)
            if parsed_move:
                return parsed_move, promotion
            else:
                print("Invalid move format. Try again. Examples: 'e2e4', 'g1f3', 'e7e8q' (for queen promotion), 'O-O' (kingside castle).")
        except Exception as e:
            print(f"An error occurred during input: {e}. Please try again.")


if __name__ == '__main__':
    # Test board printing
    b = chess_core.create_initial_board()
    print("--- White's Perspective ---")
    print_board(b, chess_core.WHITE)
    print("\n--- Black's Perspective ---")
    print_board(b, chess_core.BLACK)

    # Test square_to_coords
    print(f"\n--- Testing square_to_coords ---")
    print(f"e4 -> {square_to_coords('e4')}")   # Expected: (4, 4)
    print(f"a1 -> {square_to_coords('a1')}")   # Expected: (7, 0)
    print(f"h8 -> {square_to_coords('h8')}")   # Expected: (0, 7)
    print(f"g5 -> {square_to_coords('g5')}")   # Expected: (3, 6)
    print(f"z9 -> {square_to_coords('z9')}")   # Expected: None
    print(f"a -> {square_to_coords('a')}")     # Expected: None

    # Test parse_move_input
    print(f"\n--- Testing parse_move_input (initial board state) ---")
    gs = chess_core.game_state # Use the initial game_state from chess_core

    # Standard move
    move, promo = parse_move_input("e2e4", b, chess_core.WHITE, gs)
    print(f"e2e4 -> {move}, {promo}") # Expected: ((6,4),(4,4)), None

    # Pawn promotion (syntactically, not checking if pawn is there or can promote yet)
    move, promo = parse_move_input("e7e8q", b, chess_core.BLACK, gs) # Black pawn for testing syntax
    # To make this test more valid for promotion, let's put a black pawn on e2
    test_board_promo = chess_core.create_initial_board()
    test_board_promo[6][4] = chess_core.Piece(chess_core.BLACK, chess_core.PAWN) # Black pawn on e2 (row 6, col 4)
    test_board_promo[1][4] = None # Clear original black e7 pawn
    # print_board(test_board_promo, chess_core.WHITE)
    move, promo = parse_move_input("e2e1q", test_board_promo, chess_core.BLACK, gs)
    print(f"e2e1q (black pawn on e2) -> {move}, {promo}") # Expected: ((6,4),(7,4)), queen

    move, promo = parse_move_input("a7a8N", b, chess_core.BLACK, gs) # Black pawn for testing syntax
    # Place black pawn on a2 for this test
    test_board_promo_knight = chess_core.create_initial_board()
    test_board_promo_knight[6][0] = chess_core.Piece(chess_core.BLACK, chess_core.PAWN) # Black pawn on a2 (row 6, col 0)
    test_board_promo_knight[1][0] = None
    move, promo = parse_move_input("a2a1n", test_board_promo_knight, chess_core.BLACK, gs)
    print(f"a2a1n (black pawn on a2) -> {move}, {promo}") # Expected: ((6,0),(7,0)), knight

    # Castling (these will return None,None if castling is not actually legal from initial setup using get_king_moves)
    # To test castling parsing properly, we need a state where castling is an option returned by get_king_moves
    # For now, parse_move_input attempts to validate castling by checking get_king_moves.
    # In a real game loop, get_all_truly_legal_moves_for_color would be the source of truth.
    # Let's assume for syntax parsing it's okay for now, the game loop will catch illegal castling.
    # For O-O to be valid for white initially (it's not, f1/g1 blocked):
    gs_can_castle_white_kingside = chess_core.game_state.copy()
    b_can_castle_white_kingside = chess_core.create_initial_board()
    b_can_castle_white_kingside[7][5] = None # Clear f1
    b_can_castle_white_kingside[7][6] = None # Clear g1
    # print_board(b_can_castle_white_kingside)
    # print(f"King moves for white from e1: {chess_core.get_king_moves(b_can_castle_white_kingside, 7, 4, gs_can_castle_white_kingside)}")
    move, promo = parse_move_input("O-O", b_can_castle_white_kingside, chess_core.WHITE, gs_can_castle_white_kingside)
    print(f"O-O (White, f1/g1 clear) -> {move}, {promo}") # Expected: ((7,4),(7,6)), None

    # Invalid
    move, promo = parse_move_input("e2e2", b, chess_core.WHITE, gs)
    print(f"e2e2 -> {move}, {promo}") # Expected: None, None (or depends on how get_legal_moves handles this)
    move, promo = parse_move_input("j3j5", b, chess_core.WHITE, gs)
    print(f"j3j5 -> {move}, {promo}") # Expected: None, None

    # Test get_player_move (requires manual input)
    # print("\n--- Testing get_player_move (will require input) ---")
    # current_board_for_input = chess_core.create_initial_board()
    # current_gs_for_input = chess_core.game_state.copy()
    # player_move, player_promo = get_player_move(current_board_for_input, chess_core.WHITE, current_gs_for_input)
    # print(f"Player entered: {player_move}, promotion: {player_promo}")
    # player_move, player_promo = get_player_move(current_board_for_input, chess_core.BLACK, current_gs_for_input)
    # print(f"Player entered: {player_move}, promotion: {player_promo}")

    pass # End of main tests
