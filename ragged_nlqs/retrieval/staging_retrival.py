
import json
from urllib.parse import urljoin
from qdrant_client.http import models as rest
from ragged_nlqs.retrieval.reranking import ranking_passage_formatter
from ragged_nlqs.retrieval.vector_search import VectorSearch
from ragged_nlqs.retrieval.token_counter import get_token_count
from ragged_nlqs.retrieval.chat_model import ChatModel


def process_retrival(db_path ,collection_name, output_retrival_path, query , k=7 , filter_params="metadata.title", title_filters=None , reranking_model="nano", chat_model_type=None, api_key="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"):
    search = VectorSearch(path=db_path , collection_name=collection_name)
    filter_values = []
    for title_filter in title_filters:
       filter_values.append(rest.FieldCondition(key=filter_params, match=rest.MatchValue(value=title_filter)))

    filter = rest.Filter(should=filter_values)
    found_docs = search.search(query, k=10 , filter=filter)

    # Convert the found docs to json
    retrival_results = json.dumps(found_docs, default=lambda x: x.__dict__)

    reranked_passages = ranking_passage_formatter( retrival_results, query, type_model=reranking_model)

    text_sublinks = []
    for context in reranked_passages:
        text = context['text']
        sublinks = context['meta']['sublinks']
        title = context['meta']['title']
        author = context['meta']['author']
        host = context['meta']['hostname']
        source = context['meta']['source']
        final_text = "Title: " + title + "\n" + "Author: " + author + "\n" + "Host: " + host + "\n" + "Source: " + source + "\n" + "Here is the main text for refrence: " + text + "\n" + "Here are the citation and refreces links: " + str(sublinks)
        text_sublinks.append(final_text)
    
    #write a fn to check the token of text_sublinks and adjust it according to the selected chat model
    len_text_sublinks = len(text_sublinks)
    if chat_model_type == "hf":
        if get_token_count(text_sublinks) > 9516:
            text_sublinks = text_sublinks[:int(len_text_sublinks-1)-1]
    elif chat_model_type == "groq":
        if get_token_count(text_sublinks) > 7168:
            text_sublinks = text_sublinks[:int(len_text_sublinks-1)-1]
    elif chat_model_type == "replicate":
        if get_token_count(text_sublinks) > 9516:
            text_sublinks = text_sublinks[:int(len_text_sublinks-1)-1]
    else:
        raise ValueError("Invalid chat model type. Please select one of the following: hf, groq, replicate")
    
    if chat_model_type == "hf":
        context = str(text_sublinks)
        # Call the hf chat model
        ChatModel(model_name="mistralai/Mistral-7B-Instruct-v0.2", api_key=api_key)
        ChatModel.HuggingFaceInferenceClient(context=context , query=query)
    elif chat_model_type == "groq":
        context = str(text_sublinks)
        # Call the groq chat model
        ChatModel(model_name="llama3-8b-8192", api_key=api_key)
        ChatModel.GroqClientLlm(context=context , query=query)
    elif chat_model_type == "replicate":
        context = str(text_sublinks)
        # Call the replicate chat model
        ChatModel(model_name="mistralai/mixtral-8x7b-instruct-v0.1", api_key=api_key)
        ChatModel.replicateChatLlm(context=context , query=query)
    else:
        raise ValueError("Invalid chat model type. Please select one of the following: hf, groq, replicate")