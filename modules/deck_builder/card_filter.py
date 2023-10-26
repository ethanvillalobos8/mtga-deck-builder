# card_filter.py

import pandas as pd


def filter_cards_based_on_keywords(cards_df: pd.DataFrame, keywords: list, card_type_preference: str) -> pd.DataFrame:
    """
    Filter cards based on the provided list of keywords and card type preference.

    Parameters:
    - cards_df (pd.DataFrame): DataFrame containing card data.
    - keywords (list): List of desired keywords.
    - card_type_preference (str): Type of card preference: "creature", "non-creature", or "both".

    Returns:
    - pd.DataFrame: Filtered cards based on the keywords.
    """

    # Filter based on card type preference
    if card_type_preference == "creature":
        cards_df = cards_df[cards_df['Type'].str.contains('Creature', case=False, na=False)]
    elif card_type_preference == "non-creature":
        cards_df = cards_df[~cards_df['Type'].str.contains('Creature', case=False, na=False)]

    # Use a lambda function to check if any keyword is present in the card text
    mask = cards_df['Text'].apply(lambda text: any(keyword.lower() in str(text).lower() for keyword in keywords))
    return cards_df[mask]


def extract_card_type_preference(user_input: str) -> str:
    """
    Extract the card type preference from the user's input.

    Parameters:
    - user_input (str): User's description of their deck theme or goal.

    Returns:
    - str: Card type preference: "creature", "non-creature", or "both".
    """
    if "creature" in user_input.lower():
        return "creature"
    elif "non-creature" in user_input.lower():
        return "non-creature"
    else:
        return "both"


def calculate_card_score(card: pd.Series) -> float:
    """
    Calculate a score for a card based on various criteria.

    Parameters:
    - card (pd.Series): A row from the card dataframe.

    Returns:
    - float: Computed score for the card.
    """

    score = 0

    # Adjust score based on power-to-cost ratio for creatures
    if "Creature" in card["Type"]:
        try:
            # Extract power and toughness as integers
            power = int(card["Power"])
            toughness = int(card["Toughness"])
            # Assuming mana cost is a numeric column (e.g., converted mana cost)
            mana_cost = int(card["Mana Cost"])

            # Add the power-to-cost ratio to the score
            score += (power + toughness) / (mana_cost + 0.001)
        except (ValueError, TypeError):
            # If there's an error in extracting values, skip this adjustment
            pass

    # Slight bonus for non-creature cards to ensure variety
    if "Creature" not in card["Type"]:
        score += 1

    return score


def get_top_scored_cards(cards_df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Get the top scored cards from the provided DataFrame.

    Parameters:
    - cards_df (pd.DataFrame): DataFrame containing card data.
    - top_n (int): Number of top cards to retrieve.

    Returns:
    - pd.DataFrame: Top N scored cards.
    """

    # Calculate scores for the cards
    cards_df['Score'] = cards_df.apply(calculate_card_score, axis=1)

    # Return the top N cards based on score
    return cards_df.nlargest(top_n, 'Score')
