

import json
from ragged_nlqs.ingestion.uni_chunker import UniTextLoader, UniTextProcessor
from ragged_nlqs.ingestion.uni_crawler import UniCrawler
from ragged_nlqs.ingestion.vector_manager import VectorManager
from ragged_nlqs.retrieval.reranking import ranking_passage_formatter
from ragged_nlqs.retrieval.vector_search import VectorSearch
from qdrant_client.http import models as rest

query = "what is the main difference between langchain and llamaindex?"
reranked_passages = ranking_passage_formatter("result.json" , query, type_model="nano")
print(reranked_passages)