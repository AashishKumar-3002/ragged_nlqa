import tiktoken

def get_token_count(messages):
    # Get the encoding for the GPT-3.5 Turbo model
    encoding = tiktoken.encoding_for_model("gpt-2")

    # Encode the text
    text = str(messages)
    encoded_text = encoding.encode(text)

    # Count the number of tokens
    num_tokens = len(encoded_text)

    # Print the result
    return num_tokens