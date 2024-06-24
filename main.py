
from ragged_nlqs.ingestion.staging_ingestion import process_ingest
from ragged_nlqs.retrieval.staging_retrival import process_retrival
import json

def main():
    # Ingest data
    process_ingest(db_path="data.db", collection_name="data", data_path="data.json")

    # Retrieve data
    query = "What is the capital of France?"
    title_filters = ["capital of France"]
    process_retrival(db_path="data.db", collection_name="data", output_retrival_path="retrieval_results.json", query=query, title_filters=title_filters)