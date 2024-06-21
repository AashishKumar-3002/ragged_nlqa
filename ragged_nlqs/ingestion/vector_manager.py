from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient
from langchain_huggingface import HuggingFaceEmbeddings
import json

from ragged_nlqs.ingestion.uni_chunker import UniTextLoader, UniTextProcessor

class VectorManager:
    def __init__(self, path: str, collection_name: str, model_name: str , url: str = None , api_key: str = None):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
        )
        self.url = url
        self.api_key = api_key
        self.path = path
        self.collection_name = collection_name

    def upsert_documents(self, documents):
        try:
            if self.url is None or self.api_key is None and self.path is not None:
                qdrant = Qdrant.from_documents(
                    documents,
                    self.embeddings,
                    path=self.path,
                    collection_name=self.collection_name,
                )
            elif self.url is not None and self.api_key is not None and self.path is None:
                qdrant = Qdrant.from_documents(
                    documents,
                    self.embeddings,
                    url=self.url,
                    api_key=self.api_key,
                    collection_name=self.collection_name,
                )
            elif self.url is not None and self.api_key is not None and self.path is not None:
                qdrant = Qdrant.from_documents(
                    documents,
                    self.embeddings,
                    url=self.url,
                    api_key=self.api_key,
                    path=self.path,
                    collection_name=self.collection_name,
                )
            else:
                raise ValueError("Either URL and API key or path must be provided")
            return qdrant
        except Exception as e:
            print(e)

if __name__ == "__main__":
    model_name="sentence-transformers/all-mpnet-base-v2"
    path = "./db/standford_embedding"
    collection_name = "Standford_embedding"
    vector_manager = VectorManager(path=path, collection_name=collection_name, model_name=model_name)

    loader = UniTextLoader("final_result.json", encoding="utf-8", autodetect_encoding=True)
    text_processor = UniTextProcessor(loader, use_sizeoverlap=False, chunk_size=1000, chunk_overlap=100 , add_start_index=False , allow_chunk_oversize=False)
    processed_chunks = text_processor.spacy_process_documents()
    
    qdrant = vector_manager.upsert_documents(processed_chunks)

    print(qdrant)