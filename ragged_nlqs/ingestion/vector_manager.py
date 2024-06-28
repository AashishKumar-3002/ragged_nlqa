from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient
from langchain_huggingface import HuggingFaceEmbeddings
import json

from ragged_nlqs.ingestion.uni_chunker import UniTextLoader, UniTextProcessor

class VectorManager:
    def __init__(self, path: str, collection_name: str, model_name: str , qdrant_url: str = None , qdrant_api_key: str = None):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
        )
        self.url = qdrant_url
        self.api_key = qdrant_api_key
        self.path = path
        self.collection_name = collection_name

    def upsert_documents(self, documents):
        try:
            # Count how many of these variables are not None
            specified = sum([self.url is not None, self.path is not None])

            # Ensure only one of the variables is specified
            if specified != 1:
                raise ValueError("Only one of <url>, <host>, or <path> should be specified.")

            if self.path is not None:
                qdrant = Qdrant.from_documents(
                    documents,
                    self.embeddings,
                    path=self.path,
                    collection_name=self.collection_name,
                )
            elif self.url is not None and self.api_key is not None:
                qdrant = Qdrant.from_documents(
                    documents,
                    self.embeddings,
                    url=self.url,
                    api_key=self.api_key,
                    collection_name=self.collection_name,
                )
            else:
                raise ValueError("Either URL and API key or path must be provided.")
            return qdrant
        except Exception as e:
            print(e)

if __name__ == "__main__":
    model_name="sentence-transformers/all-mpnet-base-v2"
    collection_name = "Standford_embedding"
    qdrant_url= None
    qdrant_api_key= None
    db_path= "db/local_qdrant_all_full"
    vector_manager = VectorManager(path=db_path, collection_name=collection_name, model_name=model_name , qdrant_url=qdrant_url , qdrant_api_key=qdrant_api_key)

    loader = UniTextLoader("final_result.json", encoding="utf-8", autodetect_encoding=True)
    text_processor = UniTextProcessor(loader, use_sizeoverlap=False, chunk_size=1000, chunk_overlap=100 , add_start_index=False , allow_chunk_oversize=False)
    processed_chunks = text_processor.spacy_process_documents()
    
    qdrant = vector_manager.upsert_documents(processed_chunks)

    print(qdrant)