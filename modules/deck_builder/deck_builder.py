import pandas as pd
from typing import List, Dict
from modules.utilities.keyword_extractor import extract_keywords_from_input, keywords_df


# Simplified Color Conversion
def letter_to_color(color: str) -> str:
    color_dict = {
        'W': 'White',
        'U': 'Blue',
        'B': 'Black',
        'R': 'Red',
        'G': 'Green'
    }
    return color_dict.get(color, '')


# Refactored determine_colors
def determine_colors(user_input: str) -> List[str]:
    color_keywords = {
        'W': ['white', 'life', 'heal', 'humans', 'warriors', 'wipe'],
        'U': ['blue', 'counter', 'draw', 'bounce', 'removal'],
        'B': ['black', 'swamp', 'graveyard', 'death', 'removal', 'destroy', 'loss'],
        'R': ['red', 'burn', 'dragon', 'aggro', 'aggressive', 'lightning', 'quick'],
        'G': ['green', 'elf', 'forest', 'strong', 'heavy', 'hitters', 'big', 'dinosaur']
    }

    user_input = user_input.lower()
    included_colors = []

    for color, keywords in color_keywords.items():
        if any(keyword in user_input for keyword in keywords):
            included_colors.append(color)

    return included_colors


# Refactor Scoring Functions
def score_card(card: pd.Series, keywords: list, primary_color: str, selected_cards: pd.DataFrame) -> Dict[str, float]:
    text = card['Text'].lower()

    # Theme Score
    token_keywords = ['create', 'token', 'tokens', 'creature tokens']
    theme_score = sum([text.count(keyword.lower()) for keyword in keywords]) + \
                  sum([text.count(token_keyword) * 5 for token_keyword in token_keywords])

    # Mana Curve Score
    try:
        mana_cost = float(card['Mana Cost'])
        mana_curve_score = 1 / mana_cost
    except ValueError:
        mana_curve_score = 0

    # Color Consistency Score
    colors = ['W', 'U', 'B', 'R', 'G']
    color_score = sum([1 for color in colors if color in card['Mana Cost'] and color == primary_color])

    # Synergy Score
    synergy_score = 0
    for _, selected_card in selected_cards.iterrows():
        selected_card_text = selected_card['Text'].lower()
        shared_keywords = set(text.split()).intersection(set(selected_card_text.split()))
        synergy_score += len(shared_keywords)
        # Increase synergy score if the selected card also focuses on tokens
        if any(token_keyword in selected_card_text for token_keyword in token_keywords):
            synergy_score += 5

    return {
        'Theme Score': theme_score,
        'Mana Curve Score': mana_curve_score,
        'Color Score': color_score,
        'Synergy Score': synergy_score
    }


def calculate_land_distribution(selected_cards: pd.DataFrame, deck_size: int) -> Dict[str, int]:
    """
    Calculate land distribution based on the mana symbols in the mana costs of the selected cards.
    """
    # Count the total occurrences of each mana symbol in the selected cards' mana costs
    mana_symbols_count = {'W': 0, 'U': 0, 'B': 0, 'R': 0, 'G': 0}

    for _, card in selected_cards.iterrows():
        for symbol, count in mana_symbols_count.items():
            mana_symbols_count[symbol] += card['Mana Cost'].count(symbol)

    # Calculate the total number of mana symbols
    total_symbols = sum(mana_symbols_count.values())

    # Calculate the number of lands to add
    total_lands = deck_size - len(selected_cards)

    # Distribute the lands based on the proportion of each mana symbol
    land_distribution = {}
    for symbol, count in mana_symbols_count.items():
        land_distribution[letter_to_color(symbol)] = int(total_lands * (count / total_symbols))

    return land_distribution


def build_deck(user_input: str, cards_df: pd.DataFrame, deck_size=60, max_copies_per_card=4) -> dict:
    # Extract keywords from user input
    keywords = extract_keywords_from_input(user_input, keywords_df)

    # Determine the included colors based on user input
    included_colors = determine_colors(user_input)

    # Convert letters to full color names for filtering
    included_color_names = [letter_to_color(color) for color in included_colors]

    # Prepare a dictionary to track card counts to ensure we don't exceed max_copies_per_card
    card_counts = {}

    # Prepare a DataFrame to store selected cards
    selected_cards_df = pd.DataFrame()

    # Filter cards based on included colors and exclude cards that require other colors
    valid_cards_df = cards_df[cards_df['Mana Cost'].fillna('').apply(
        lambda x: all(color in x for color in included_colors) and all(
            color not in x for color in ['W', 'U', 'B', 'R', 'G'] if color not in included_colors))].copy()

    # Score the cards
    scores_df = valid_cards_df.apply(lambda card: score_card(card, keywords, included_colors, selected_cards_df),
                                     axis=1, result_type='expand')
    valid_cards_df = pd.concat([valid_cards_df, scores_df], axis=1)
    valid_cards_df['Total Score'] = valid_cards_df[
        ['Theme Score', 'Mana Curve Score', 'Color Score', 'Synergy Score']].sum(axis=1)

    # Sort cards by Total Score in descending order for selection
    valid_cards_df = valid_cards_df.sort_values(by='Total Score', ascending=False)

    for _, card in valid_cards_df.iterrows():
        if len(selected_cards_df) >= (deck_size - 24):  # Reserve space for approximately 24 lands
            break

        card_name = card['Name']
        if card_name not in card_counts:
            card_counts[card_name] = 0

        if card_counts[card_name] < max_copies_per_card:
            card_counts[card_name] += 1
            selected_cards_df = pd.concat([selected_cards_df, card.to_frame().T], ignore_index=True)

    # Calculate land distribution
    land_distribution = calculate_land_distribution(selected_cards_df, deck_size)

    # Adjust the land count based on the average mana cost of the selected cards
    average_mana_cost = selected_cards_df['Mana Cost'].str.count('[WUBRGC]').mean()
    total_land_count = int(20 + (4 * average_mana_cost))

    for land, count in land_distribution.items():
        difference = total_land_count - sum(land_distribution.values())
        land_distribution[land] += min(difference, count)

    # Prepare the final deck dictionary with card counts
    deck_dict = {}
    for _, card in selected_cards_df.iterrows():
        card_name = card['Name']
        if card_name in deck_dict:
            deck_dict[card_name] += 1
        else:
            deck_dict[card_name] = 1

    # Convert color names to actual land names
    color_to_land_map = {
        "White": "Plains",
        "Blue": "Island",
        "Black": "Swamp",
        "Red": "Mountain",
        "Green": "Forest"
    }
    for color, land_name in color_to_land_map.items():
        if color in included_color_names:
            deck_dict[land_name] = deck_dict.get(land_name, 0) + land_distribution[color]

    return deck_dict
