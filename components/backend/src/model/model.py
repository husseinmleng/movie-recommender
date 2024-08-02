import os
import time
import pathlib
import logging
from langchain.prompts import load_prompt
from langchain_core.output_parsers.string import StrOutputParser
from langchain_core.messages import AIMessage, HumanMessage
from utils import handle_message

from utils import find_and_split_on_substring, substrings


logger = logging.getLogger("main")
root_path = pathlib.Path(__file__).parent.parent


class MovieRecommendationAssistant:
    def __init__(self, semantic_layer, llm):
        self.semantic_layer = semantic_layer
        self.llm = llm
        self.chat_history = []
        self.prompt = load_prompt(
            os.path.join(root_path, "prompts", "chatbot_recommender.yaml")
        )
        self.chain = self.prompt | self.llm | StrOutputParser()

    async def astream(self, query, k=2):
        before_route = time.monotonic_ns()
        extra = self.semantic_layer.process_query(query)
        after_route = time.monotonic_ns()
        total_route_time = (after_route - before_route) / 1_000_000.0
        logger.info(f"Route tool time: {total_route_time:.2f} ms")

        text = ""
        ai_message = ""
        async for chunk in self.chain.astream({"query": query, 
                                        "chat_history": self.chat_history,
                                        "extra": extra,
                                        "k": k}):
            ai_message += chunk
            text += chunk
            sentence, text = find_and_split_on_substring(text, substrings)
            if sentence:
                yield handle_message(sentence, is_final=False)
         
        if text:
            # Yield the remaining text if any after the loop ends
            yield handle_message(text, is_final=True)       

        self.chat_history.extend(
            [
                HumanMessage(content=query),
                AIMessage(content=ai_message),
            ]
        )
        
    def reset_chat_history(self):
        self.chat_history = []  
