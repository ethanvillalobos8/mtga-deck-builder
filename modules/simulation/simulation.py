from modules.simulation.game_state import MTGGame
from modules.utilities.data_loader import load_data


def simulate_game(player1_deck, player2_deck):
    card_catalog = load_data('data/cards_catalog.csv')
    game = MTGGame(player1_deck, player2_deck, card_catalog)
    game.game_loop()

