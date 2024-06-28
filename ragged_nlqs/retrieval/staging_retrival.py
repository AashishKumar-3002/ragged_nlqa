
import json
from urllib.parse import urljoin
from qdrant_client.http import models as rest
from ragged_nlqs.retrieval.reranking import ranking_passage_formatter
from ragged_nlqs.retrieval.vector_search import VectorSearch
from ragged_nlqs.retrieval.token_counter import get_token_count
from ragged_nlqs.retrieval.chat_model import ChatModel


def process_retrival(db_path ,collection_name, output_retrival_path, reranking_model_path , query , k=7 , filter_params="metadata.title", title_filters=None , reranking_model="nano", chat_model_type="hf", api_key="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"):
    search = VectorSearch(path=db_path , collection_name=collection_name)
    filter_values = []

    if title_filters:
        for title_filter in title_filters:
            filter_values.append(rest.FieldCondition(key=filter_params, match=rest.MatchValue(value=title_filter)))

        filter = rest.Filter(should=filter_values)
        found_docs = search.search(query, k=10 , filter=filter)
    else:
        found_docs = search.search(query, k=10)

    # Convert the found docs to json
    retrival_results = json.dumps(found_docs, default=lambda x: x.__dict__)
    if not retrival_results:
        raise ValueError("No data found")

    reranked_passages = ranking_passage_formatter( retrival_results, query, reranking_model_path, type_model=reranking_model)

    text_sublinks = []
    for context in reranked_passages:
        text = context['text']
        sublinks = context['meta']['sublinks']
        title = context['meta']['title']
        author = context['meta']['author']
        host = context['meta']['hostname']
        source = context['meta']['source']
        #find the one that is NoneType
        if author is None:
            author = "Not Available"
        if host is None:
            host = "Not Available"
        if source is None:
            source = "Not Available"
        if sublinks is None:
            sublinks = "Not Available"
        if title is None:
            title = "Not Available"
        if text is None:
            text = "Not Available"
        final_text = "Title: " + title + "\n" + "Author: " + author + "\n" + "Host: " + host + "\n" + "Source: " + source + "\n" + "Here is the main text for refrence: " + text + "\n" + "Here are the citation and refreces links: " + str(sublinks)
        text_sublinks.append(final_text)
    
    non_ref_text_sublinks = text_sublinks
    final_input_token = 0
    #write a fn to check the token of text_sublinks and adjust it according to the selected chat model
    while True:
        len_text_sublinks = len(text_sublinks)
        if chat_model_type == "hf":
            if get_token_count(text_sublinks) > 9516:
                text_sublinks = text_sublinks[:int(len_text_sublinks-1)]
                final_input_token = get_token_count(text_sublinks)
            else:
                text_sublinks = non_ref_text_sublinks[:int(len_text_sublinks+1)]
                if get_token_count(text_sublinks) > 9516 and get_token_count(text_sublinks) < 27000:
                    final_input_token = get_token_count(text_sublinks)
                    break
                else:
                    text_sublinks = text_sublinks[:int(len_text_sublinks-1)]
                    final_input_token = get_token_count(text_sublinks)
                    break
        elif chat_model_type == "groq":
            if get_token_count(text_sublinks) > 7168:
                text_sublinks = text_sublinks[:int(len_text_sublinks-1)]
            else:
                final_input_token = get_token_count(text_sublinks)
                break
        elif chat_model_type == "replicate":
            if get_token_count(text_sublinks) > 9516:
                text_sublinks = text_sublinks[:int(len_text_sublinks-1)]
            else:
                final_input_token = get_token_count(text_sublinks)
                break
        else:
            raise ValueError("Invalid chat model type. Please select one of the following: hf, groq, replicate")
    print("Final input token count: ", final_input_token)
    max_tokens = 28000 - final_input_token
    print("Max tokens: ", max_tokens)
    if chat_model_type == "hf":
        context = str(text_sublinks)
        # Call the hf chat model
        hf_instance = ChatModel(model_name="mistralai/Mistral-7B-Instruct-v0.2", api_key=api_key)
        res = hf_instance.HuggingFaceInferenceClient(context=context , max_tokens=max_tokens, query=query)
    elif chat_model_type == "groq":
        context = str(text_sublinks)
        # Call the groq chat model
        groq_instance = ChatModel(model_name="llama3-8b-8192", api_key=api_key)
        res = groq_instance.GroqClientLlm(context=context , query=query)
    elif chat_model_type == "replicate":
        context = str(text_sublinks)
        # Call the replicate chat model
        replicate_instance = ChatModel(model_name="mistralai/mixtral-8x7b-instruct-v0.1", api_key=api_key)
        res = replicate_instance.replicateChatLlm(context=context , max_tokens=max_tokens, query=query)
    else:
        raise ValueError("Invalid chat model type. Please select one of the following: hf, groq, replicate")

    return res