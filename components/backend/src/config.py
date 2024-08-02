import os
import pathlib
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

root_path = pathlib.Path(__file__).parent


@dataclass(init=False)
class Config:
    class Retriever:
        MOVIE_DATA_PATH = os.environ.get("RETRIEVER_MOVIE_DATA_PATH", os.path.join(root_path, "data", "imdb_top_1000.csv"))
        EMBEDDING_MODEL = os.environ.get("RETRIEVER_EMBEDDING_MODEL", "text-embedding-3-small")
        EMBEDDING_THRESHOLD = float(os.environ.get("RETRIEVER_EMBEDDING_THRESHOLD", 0.4))

    class OpenAI:
        MODEL_NAME = os.environ.get("OPENAI_MODEL_NAME", "gpt-4o")
        API_KEY = os.environ.get("OPENAI_API_KEY")
        TIMEOUT = int(os.environ.get("OPENAI_TIMEOUT", 30))
        TEMPERATURE = float(os.environ.get("OPENAI_TEMPERATURE", 0.3))
