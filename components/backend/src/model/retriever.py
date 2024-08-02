from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

from config import Config


class MovieRetriever:
    def __init__(self, documents, k=50):
        self.k = k
        self.embeddings = OpenAIEmbeddings(
            model=Config.Retriever.EMBEDDING_MODEL,
            api_key=Config.OpenAI.API_KEY
        )
        self.db = FAISS.from_documents(documents, self.embeddings)
        self.retriever = self.db.as_retriever(search_kwargs={"k": self.k})

    def retrieve(self, query):
        return self.retriever.invoke(query)