import os
import json
import pandas as pd
from langchain.schema import Document
from config import Config


substrings = [
  "... ",
  ". ",
  "? ",
  "!!! ",
  "\n",
  "\n\n",
  "\r",
  "\n",
  "\r\n",
]


def load_documents():
    df = pd.read_csv(Config.Retriever.MOVIE_DATA_PATH)
    movie_df = df[['Series_Title', 'Released_Year', 'Runtime', 'Genre', 'Overview', 'IMDB_Rating', 'Director', 'Star1', 'Star2', 'Star3', 'Star4', 'No_of_Votes']]
    documents = [Document(page_content=item) for item in movie_df.apply(lambda row: ', '.join([f'{col_name}: {row[col_name]}' for col_name in movie_df.columns]), axis=1).tolist()]
    return documents


def handle_message(message, is_final):
    payload = {"streamed_text": message, "is_final": is_final}
    event = f"data: {json.dumps(payload)}\n\n"
    return event


def find_and_split_on_substring(text, substrings):
    # Initialize the position and marker variables
    pos = len(text)
    selected_marker = None

    # Find the position of the first occurrence of any marker
    for marker in substrings:
        marker_pos = text.find(marker)
        if marker_pos != -1 and marker_pos < pos:
            pos = marker_pos
            selected_marker = marker

    # If a marker was found, split the text
    if selected_marker is not None:
        # Include the marker in the sentence
        pos += len(selected_marker)
        sentence = text[:pos]
        remaining_text = text[pos:]
        return sentence, remaining_text

    # If no marker was found, return None
    return None, text
