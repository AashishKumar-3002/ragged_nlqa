
from ragged_nlqs.ingestion.staging_ingestion import process_ingest
from ragged_nlqs.retrieval.staging_retrival import process_retrival
import json

def main():
    # Ingest data
    # url , output_file_path , scrape_sublinks=True , max_workers=5 , encoding="utf-8" , autodetect_encoding=True, use_sizeoverlap=False, chunk_size=1000, chunk_overlap=100 , add_start_index=True , allow_chunk_oversize=False , spacy_model='en_core_web_md', embedding_model="sentence-transformers/all-mpnet-base-v2" , collection_name="Standford_embedding" , qdrant_url=None , qdrant_api_key=None, db_path="./db/qdrant_standford_embedding"
    url = "https://en.wikipedia.org/wiki/Paris"
    output_file_path = "data.json"
    scrape_sublinks = True
    add_start_index = False
    collection_name = "data"
    qdrant_url = None
    qdrant_api_key = None
    db_path = "data.db"
    res = process_ingest(url=url, output_file_path=output_file_path, scrape_sublinks=scrape_sublinks, add_start_index=add_start_index, collection_name=collection_name, qdrant_url=qdrant_url, qdrant_api_key=qdrant_api_key, db_path=db_path)

    # Retrieve data
    query = "What are the effects of llms on the environment?"
    title_filters = ["Introduction" , "Environmental Impact"]
    output_file_path = "output.json"
    k = 10
    filter_params = "metadata.title"
    reranking_model = "medium"
    chat_model_type = "hf"
    api_key = "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"
    res_ret = process_retrival(db_path=db_path ,collection_name=collection_name, output_retrival_path=output_file_path, query=query , k=k , filter_params=filter_params, title_filters=title_filters , reranking_model=reranking_model, chat_model_type=chat_model_type, api_key=api_key)
    print(res_ret)