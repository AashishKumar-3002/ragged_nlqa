import json
from flashrank import Ranker , RerankRequest

def rerank_passages(query, passages, type="nano" , cache_dir="~/.cache/ranking_model" , max_length=10000):
    # Nano (~4MB), blazing fast model & competitive performance (ranking precision).
    if type=="nano":
        ranker = Ranker()

    # Small (~34MB), slightly slower & best performance (ranking precision).
    elif type=="small":
        ranker = Ranker(model_name="ms-marco-MiniLM-L-12-v2", cache_dir=cache_dir)

    # Medium (~110MB), slower model with best zeroshot performance (ranking precision) on out of domain data.
    elif type=="medium":
        ranker = Ranker(model_name="rank-T5-flan", cache_dir=cache_dir)

    # Medium (~150MB), slower model with competitive performance (ranking precision) for 100+ languages  (don't use for english)
    elif type=="medium-multi":
        ranker = Ranker(model_name="ms-marco-MultiBERT-L-12")

    elif type=="large":
        ranker = Ranker(model_name="rank_zephyr_7b_v1_full", max_length=max_length) # adjust max_length based on your passage length
        
    else:
        ranker = Ranker()
    return ranker.rerank(RerankRequest(query=query, passages=passages))

def ranking_passage_formatter(data , query, cache_dir, type_model="nano"):

    # Parse the JSON string back to Python objects
    data = json.loads(data)

    json_reranking = []
    for i , docs in enumerate(data):
        score = docs[1]
        doc = docs[0]
        reranking = {
            "id" : i+1,
            "text": doc['page_content'],
            "meta" : doc['metadata'],
            "score" : score
        }
        json_reranking.append(reranking)

    reranked_passages = rerank_passages(query, json_reranking , type=type_model , cache_dir=cache_dir , max_length=10000)
    print(len(reranked_passages))
    print(type(reranked_passages))
    return reranked_passages

if __name__ == "__main__":
    # Example usage
    query = "what are the major environmental risk by llms?"
    with open("temp/result.json") as f:
        data = json.load(f.read())
    reranked_passages = ranking_passage_formatter( data, query, type_model="nano")
    print(reranked_passages)