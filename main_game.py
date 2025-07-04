import chess_core
import chess_ui
import copy

def play_game():
    """
    Main function to run a text-based chess game.
    """
    board = chess_core.create_initial_board()
    # Deepcopy initial game_state to allow for multiple games or resets if needed later
    game_state = copy.deepcopy(chess_core.game_state)

    game_over = False
    winner = None

    while not game_over:
        current_player = game_state["current_player"]
        opponent_color = chess_core.BLACK if current_player == chess_core.WHITE else chess_core.WHITE

        # 1. Display board and game info
        print("\n" + "="*30)
        chess_ui.print_board(board, perspective=current_player) # Show board from current player's perspective
        print(f"Current player: {current_player.capitalize()}")

        if chess_core.is_king_in_check(board, current_player, game_state):
            print(f"{current_player.capitalize()} is IN CHECK!")

        # 2. Get all legal moves for the current player
        legal_moves = chess_core.get_all_truly_legal_moves_for_color(board, current_player, game_state)

        # 3. Check for game end conditions
        if not legal_moves:
            if chess_core.is_king_in_check(board, current_player, game_state):
                winner = opponent_color
                print(f"\nCHECKMATE! {winner.capitalize()} wins!")
            else:
                print("\nSTALEMATE! It's a draw.")
            game_over = True
            break

        # Check for 50-move rule (basic check)
        if game_state["halfmove_clock"] >= 100: # 50 moves = 100 half-moves
            print("\nDRAW by 50-move rule!")
            game_over = True
            break

        # (Threefold repetition and insufficient material checks would go here in a more advanced version)

        # 4. Get player input
        print(f"You have {len(legal_moves)} legal move(s).")
        # For debugging, can print legal moves:
        # print("Legal moves:", [ (chess_ui.coords_to_square(m[0]), chess_ui.coords_to_square(m[1])) for m in legal_moves])

        chosen_move_coords, promotion_piece = None, None
        while True:
            chosen_move_coords, promotion_piece = chess_ui.get_player_move(board, current_player, game_state)

            if chosen_move_coords in legal_moves:
                # Check if this move requires a promotion choice if one wasn't given
                from_r, from_c = chosen_move_coords[0]
                to_r, to_c = chosen_move_coords[1]
                piece_moved = board[from_r][from_c]

                if piece_moved and piece_moved.piece_type == chess_core.PAWN and \
                   ( (piece_moved.color == chess_core.WHITE and to_r == 0) or \
                     (piece_moved.color == chess_core.BLACK and to_r == 7) ):
                    if not promotion_piece: # If input was e.g. "e7e8" but needs promotion
                        while True:
                            promo_input = input("Promote pawn to (q, r, b, n): ").strip().lower()
                            if promo_input == 'q': promotion_piece = chess_core.QUEEN; break
                            elif promo_input == 'r': promotion_piece = chess_core.ROOK; break
                            elif promo_input == 'b': promotion_piece = chess_core.BISHOP; break
                            elif promo_input == 'n': promotion_piece = chess_core.KNIGHT; break
                            else: print("Invalid promotion choice.")
                break
            else:
                print("That is not a legal move. Please try again.")
                # print("Legal moves are:", legal_moves) # For debugging
                # print("Your move was:", chosen_move_coords)

        # 5. Apply move
        chess_core.apply_real_move(board, game_state, chosen_move_coords, promotion_piece)
        print(f"{current_player.capitalize()} moved: {chess_ui.square_to_coords_notation(chosen_move_coords[0])}{chess_ui.square_to_coords_notation(chosen_move_coords[1])}{promotion_piece[0] if promotion_piece else ''}")


    # Game finished
    print("\n--- Final Board ---")
    chess_ui.print_board(board, chess_core.WHITE) # Show final board from White's perspective
    print("\nGame Over.")
    if winner:
        print(f"{winner.capitalize()} is victorious!")
    else:
        print("The game is a draw.")

def main():
    """ Main entry point """
    while True:
        play_game()
        if input("Play again? (y/n): ").strip().lower() != 'y':
            break
    print("Thanks for playing!")

if __name__ == "__main__":
    # Add coords_to_square to chess_ui for debugging prints if it's not there
    # For now, let's define a simple version here for the print statement above
    # This should ideally be in chess_ui.py
    def temp_coords_to_square(coords):
        if not coords: return ""
        r, c = coords
        return chr(ord('a') + c) + str(8 - r)

    chess_ui.coords_to_square_notation = temp_coords_to_square # Monkey patch for now

    main()
