from modules.utilities.user_input import get_user_input
from modules.deck_builder.deck_builder import build_deck
from modules.utilities.data_loader import load_data
from modules.simulation.simulation import simulate_game


def deck_building_assistant():
    """
    Main function to assist in deck building based on user input.
    """

    # 1. Get the desired deck theme from the user
    user_theme = get_user_input()

    # 2. Build the deck based on the user's theme
    deck_dict = build_deck(user_theme, load_data('data/cards_catalog.csv'))

    print()
    print('Your Deck:')

    # 3. Display the deck to the user
    def display_deck(deck_dict):
        for card_name, count in deck_dict.items():
            print(f"{count}x {card_name}")

    # Actually calling the function to display the deck
    display_deck(deck_dict)

    return deck_dict


if __name__ == "__main__":
    # Sample decks for simulation
    sample_deck1 = deck_building_assistant()
    sample_deck2 = deck_building_assistant()

    simulate_game(sample_deck1, sample_deck2)
