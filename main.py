
from ragged_nlqs.ingestion.staging_ingestion import process_ingest
from ragged_nlqs.retrieval.staging_retrival import process_retrival
from utils.config_utils import load_config
import json

# def main():
#     # Ingest data
#     # url , output_file_path , scrape_sublinks=True , max_workers=5 , encoding="utf-8" , autodetect_encoding=True, use_sizeoverlap=False, chunk_size=1000, chunk_overlap=100 , add_start_index=True , allow_chunk_oversize=False , spacy_model='en_core_web_md', embedding_model="sentence-transformers/all-mpnet-base-v2" , collection_name="Standford_embedding" , qdrant_url=None , qdrant_api_key=None, db_path="./db/qdrant_standford_embedding"
#     url = "https://en.wikipedia.org/wiki/Paris"
#     output_file_path = "data.json"
#     scrape_sublinks = True
#     add_start_index = False
#     collection_name = "data"
#     qdrant_url = None
#     qdrant_api_key = None
#     db_path = "data.db"
#     res = process_ingest(url=url, output_file_path=output_file_path, scrape_sublinks=scrape_sublinks, add_start_index=add_start_index, collection_name=collection_name, qdrant_url=qdrant_url, qdrant_api_key=qdrant_api_key, db_path=db_path)

#     # Retrieve data
#     query = "What are the effects of llms on the environment?"
#     title_filters = ["Introduction" , "Environmental Impact"]
#     output_file_path = "output.json"
#     k = 10
#     filter_params = "metadata.title"
#     reranking_model = "medium"
#     chat_model_type = "hf"
#     api_key = "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"
#     res_ret = process_retrival(db_path=db_path ,collection_name=collection_name, output_retrival_path=output_file_path, query=query , k=k , filter_params=filter_params, title_filters=title_filters , reranking_model=reranking_model, chat_model_type=chat_model_type, api_key=api_key)
#     print(res_ret)
config_value = load_config()['nlqa']

# Ingestion
ingest_url = config_value['ingestion']['url']
ingest_output_path = config_value['ingestion']['output_path']
ingest_scrape_sublinks = config_value['ingestion']['preprocessing']['scrape_sublinks']
ingest_max_workers = config_value['ingestion']['preprocessing']['max_workers']
ingest_encoding = config_value['ingestion']['preprocessing']['encoding']
ingest_auto_detect_encoding = config_value['ingestion']['preprocessing']['auto_detect_encoding']
ingest_size_overlap = config_value['ingestion']['preprocessing']['size_overlap']
ingest_chunk_size = config_value['ingestion']['preprocessing']['chunk_size']
ingest_chunk_overlap = config_value['ingestion']['preprocessing']['chunk_overlap']
ingest_add_start_index = config_value['ingestion']['preprocessing']['add_start_index']
ingest_allow_chunk_overlap = config_value['ingestion']['preprocessing']['allow_chunk_overlap']
ingest_spacy_model = config_value['ingestion']['preprocessing']['spacy_model']
ingest_embedding_model = config_value['ingestion']['config']['embedding_model']
ingest_collection_name = config_value['ingestion']['config']['collection_name']
ingest_qdrant_url = config_value['ingestion']['config']['qdrant_url']
ingest_qdrant_api_key = config_value['ingestion']['config']['qdrant_api_key']
ingest_db_path = config_value['ingestion']['config']['db_path']

# Retrieval
retrieval_embedding_model = config_value['retrieval']['config']['embedding_model']
retrieval_collection_name = config_value['retrieval']['config']['collection_name']
retrieval_qdrant_url = config_value['retrieval']['config']['qdrant_url']
retrieval_qdrant_api_key = config_value['retrieval']['config']['qdrant_api_key']
retrieval_db_path = config_value['retrieval']['config']['db_path']
retrieval_query = config_value['retrieval']['search']['query']
retrieval_top_k = config_value['retrieval']['search']['top_k']
retrieval_filters = config_value['retrieval']['search']['filters']
retrieval_filter_values = config_value['retrieval']['search']['filter_values']
retrieval_reranking_model = config_value['retrieval']['search']['reranking_model']
retrieval_chat_model_type = config_value['retrieval']['search']['chat_model_type']
retrieval_api_key = config_value['retrieval']['search']['api_key']