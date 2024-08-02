import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from model.semantic_layer import SemanticLayer
from model.retriever import MovieRetriever
from model.model import MovieRecommendationAssistant
from utils import load_documents
from config import Config


logger = logging.getLogger("main")
format = "%(asctime)s %(levelname)-8s %(message)s"
logging.basicConfig(format=format)
logger.setLevel("INFO")


class ChatRequest(BaseModel):
    message: str
    clear_history: bool = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    documents = load_documents()
    logger.warning(f"Number of Loaded documents/movies: {len(documents)}", )
    retriever = MovieRetriever(documents)
    semantic_layer = SemanticLayer(retriever)

    llm = ChatOpenAI(
        model=Config.OpenAI.MODEL_NAME,
        temperature=Config.OpenAI.TEMPERATURE,
        api_key=Config.OpenAI.API_KEY,
        timeout=Config.OpenAI.TIMEOUT,
    )
    app.state.model = MovieRecommendationAssistant(semantic_layer, llm)
    yield
    app.state.model.reset_chat_history()


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def health_check():
    return "Movie Recommender chatbot is running"


@app.post("/chat")
async def generate_response(
    request: ChatRequest,
    model: MovieRecommendationAssistant = Depends(lambda: app.state.model)
) -> StreamingResponse:
    
    if request.clear_history:
        logger.info("Clearing chat history")
        model.reset_chat_history()
        
    return StreamingResponse(
        model.astream(request.message),
        media_type="text/event-stream",
        status_code=200,
    )
