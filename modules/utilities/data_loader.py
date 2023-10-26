# data_loader.py

import pandas as pd


def load_data(file_path: str) -> pd.DataFrame:
    """
    Load card data from the given CSV file path.

    Parameters:
    - file_path (str): Path to the CSV file containing card data.

    Returns:
    - pd.DataFrame: DataFrame containing the card data.
    """
    cards_df = pd.read_csv(file_path)
    # Handle missing values and other preprocessing steps if needed
    # For now, we'll just fill missing values with a placeholder string.
    cards_df.fillna("Unknown", inplace=True)
    return cards_df
