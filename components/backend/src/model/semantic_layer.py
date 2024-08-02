import logging
from semantic_router import Route, RouteLayer
from semantic_router.encoders import OpenAIEncoder
from config import Config


logger = logging.getLogger("main")


class SemanticLayer:
    def __init__(self, retriever):
        self.retriever = retriever
        self.routes = self._initialize_routes()
        self.route_layer = RouteLayer(
            encoder=OpenAIEncoder(
                name=Config.Retriever.EMBEDDING_MODEL,
                openai_api_key=Config.OpenAI.API_KEY,
                score_threshold=Config.Retriever.EMBEDDING_THRESHOLD
            ),
            routes=self.routes
        )

    def _initialize_routes(self):
        recommendation_route = Route(
            name="get_list_of_movies",
            utterances=[
                "Show me some movies",
                "Do you have 2020 movies?",
                "I want batman movie",
                "I want Drama movies",
            ]
        )
        return [recommendation_route]

    def process_query(self, query):
        route = self.route_layer(query)
        extra = ""
        logger.info(f"Tool name: {route.name}" )
        if route.name == "get_list_of_movies":
            retrieved_docs = self.retriever.retrieve(query)
            logger.info(f"Number of retrieved documents: {len(retrieved_docs)}")
            formatted_docs = SemanticLayer.format_docs(retrieved_docs)

            extra = f"You can recommend to the user from this list only:\n{formatted_docs}"
        return extra

    @staticmethod
    def format_docs(docs):
        return "\n\n".join([d.page_content for d in docs])