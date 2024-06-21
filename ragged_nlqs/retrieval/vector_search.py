import json
from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client.http import models as rest

class VectorSearch:
    
    def __init__(self , path: str , collection_name: str):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2",
        )
        self.client = QdrantClient(path=path)
        self.collection_name = collection_name
        self.qdrant = Qdrant(self.client, self.collection_name, self.embeddings)

    def search(self, query: str , k: int = 7 , filter: rest.Filter = None):
        emb = self.embeddings.embed_query(query)
        found_docs = self.qdrant.similarity_search_with_score_by_vector(emb, k=k , filter=filter)
        return found_docs

    def mrm_search(self, query: str , k: int = 7 , fetch_k: int = 10 , filter: rest.Filter = None):
        found_docs = self.qdrant.max_marginal_relevance_search(query, k=k, fetch_k=fetch_k , filter=filter)
        return found_docs

    def as_retriever(self):
        return self.qdrant.as_retriever()

if __name__ == "__main__":
    search = VectorSearch(path="./db/standford_embedding" , collection_name="Standford_embedding")
    query = "what are the major environmental risk by llms?"
    filter = rest.Filter(should=[rest.FieldCondition(key="metadata.title", match=rest.MatchValue(value="Environmental impact")), rest.FieldCondition(key="metadata.title", match=rest.MatchValue(value="Introduction"))])
    found_docs = search.search(query, k=7 , filter=filter)

    with open("result.json", "w") as f:
        json.dump(found_docs, f, default=lambda x: x.__dict__)

    # print(found_docs)
    # found_docs = search.mrm_search(query, k=4, fetch_k=10)
    # print(found_docs)
    # retriever = search.as_retriever()
    # print(retriever)