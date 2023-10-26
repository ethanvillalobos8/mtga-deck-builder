import pandas as pd


def load_keywords(file_path: str) -> pd.DataFrame:
    """
    Load keywords data from the given CSV file path.

    Parameters:
    - file_path (str): Path to the CSV file containing keyword data.

    Returns:
    - pd.DataFrame: DataFrame containing the keyword data.
    """
    return pd.read_csv(file_path)


# Load keywords DataFrame when the module is imported
keywords_df = load_keywords('data/all_mtg_keywords.csv')


def extract_keywords_from_input(user_input: str, keywords_df: pd.DataFrame) -> list:
    """
    Extract relevant MTG keywords from user input.

    Parameters:
    - user_input (str): User's description of their deck theme or goal.
    - keywords_df (pd.DataFrame): DataFrame containing MTG keywords.

    Returns:
    - list: Extracted keywords.
    """

    user_input = user_input.lower()
    found_keywords = []

    for _, row in keywords_df.iterrows():
        keyword = row['Keyword'].lower()
        if keyword in user_input:
            found_keywords.append(keyword)

    return found_keywords
