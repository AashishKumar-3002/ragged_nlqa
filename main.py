
from ragged_nlqs.ingestion.staging_ingestion import process_ingest
from ragged_nlqs.ingestion.uni_chunker import UniTextLoader, UniTextProcessor
from ragged_nlqs.ingestion.vector_manager import VectorManager
from ragged_nlqs.retrieval.staging_retrival import process_retrival
from utils.config_utils import load_config
import json

# Load config
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
retrieval_reranking_model_path = config_value['retrieval']['search']['reranking_model_path']
retrieval_chat_model_type = config_value['retrieval']['search']['chat_model_type']
retrieval_api_key = config_value['retrieval']['search']['api_key']

def main(type="ingestion"):
    if type == "ingestion":
        res = process_ingest(
            url=ingest_url,
            output_file_path=ingest_output_path,
            scrape_sublinks=ingest_scrape_sublinks,
            add_start_index=ingest_add_start_index,
            collection_name=ingest_collection_name,
            qdrant_url=ingest_qdrant_url,
            qdrant_api_key=ingest_qdrant_api_key,
            db_path=ingest_db_path
        )
        print(res)

    elif type == "retrieval":
        res_ret = process_retrival(
            db_path=retrieval_db_path,
            collection_name=retrieval_collection_name,
            output_retrival_path=ingest_output_path,
            query=retrieval_query,
            k=retrieval_top_k,
            filter_params=retrieval_filters,
            title_filters=retrieval_filter_values,
            reranking_model=retrieval_reranking_model,
            chat_model_type=retrieval_chat_model_type,
            reranking_model_path=retrieval_reranking_model_path,
            api_key=retrieval_api_key
        )
        print(res_ret)
    else:
        raise ValueError("Invalid type. Please select one of the following: ingestion, retrieval")

if __name__ == "__main__":
    main("retrieval")