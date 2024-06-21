import json
from ragged_nlqs.ingestion.uni_chunker import UniTextLoader, UniTextProcessor
from ragged_nlqs.ingestion.uni_crawler import UniCrawler
from urllib.parse import urljoin

from ragged_nlqs.ingestion.vector_manager import VectorManager

def staging_ingestion(url , output_file_path , scrape_sublinks=True , max_workers=5 , encoding="utf-8" , autodetect_encoding=True, use_sizeoverlap=False, chunk_size=1000, chunk_overlap=100 , add_start_index=True , allow_chunk_oversize=False , spacy_model='en_core_web_md', embedding_model="sentence-transformers/all-mpnet-base-v2" , collection_name="Standford_embedding" , qdrant_url=None , qdrant_api_key=None, db_path="./db/qdrant_standford_embedding"):
    crawler = UniCrawler(url)
    
    final_json = crawler.uni_crawler(scrape_sublinks=scrape_sublinks, max_workers=max_workers)
    final_path = urljoin(output_file_path, "final_result.json")
    if final_json:
        with open(final_path, 'w') as outfile:
            json.dump(final_json, outfile)
    else:
        raise Exception("No data found")
    
    loader = UniTextLoader(final_path, encoding=encoding, autodetect_encoding=autodetect_encoding)
    text_processor = UniTextProcessor(loader, use_sizeoverlap=use_sizeoverlap, chunk_size=chunk_size, chunk_overlap=chunk_overlap , add_start_index=add_start_index , allow_chunk_oversize=allow_chunk_oversize , spacy_model=spacy_model)
    processed_chunks = text_processor.spacy_process_documents()


    print(len(processed_chunks))
    
    vector_manager = VectorManager(path=db_path, collection_name=collection_name, model_name=embedding_model , qdrant_url=qdrant_url , qdrant_api=qdrant_api_key)

    qdrant = vector_manager.upsert_documents(processed_chunks)

    return qdrant
