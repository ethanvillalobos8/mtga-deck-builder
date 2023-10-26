import pandas as pd

def append_deck_to_csv(deck: dict, filename: str):
    """
    Append the deck to an existing CSV file.

    Args:
    - deck: The dictionary of the deck built by our deck builder.
    - filename: The name of the CSV file to append to.
    """
    # Convert the deck dictionary to a DataFrame
    deck_df = pd.DataFrame(list(deck.items()), columns=['Card Name', 'Count'])

    # Check if the file already exists
    try:
        existing_df = pd.read_csv(filename)
        combined_df = pd.concat([existing_df, deck_df], ignore_index=True)
    except FileNotFoundError:
        combined_df = deck_df

    # Save (or overwrite) the DataFrame to the CSV file
    combined_df.to_csv(filename, index=False)
