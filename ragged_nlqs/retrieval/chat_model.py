from httpcore import ProtocolError
from huggingface_hub import InferenceClient
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
import replicate


class ChatModel:
    def __init__(self, model_name , api_key=None):
        self.model_name = model_name
        self.api_key = api_key
    
    def HuggingFaceInferenceClient(self, context=None , max_tokens=20000, temperature=0.3, query=None):
        if not self.model_name:
            self.model_name = "mistralai/Mistral-7B-Instruct-v0.2"
        messages = [
            {
                "role" : "user" ,
                "content" : "Answer in detail using the Context to answer the question following up: " + context + ". question: " + query
            },
            {
                "role" :"assistant",
                "content": """You are an AI assistant whose job is to answer users' questions based on the provided context in presentable manner. Your response should be detailed and reference the provided sources. Use the following guidelines:
                                1. Answer the Question:

                                - Provide a detailed explanation using the context provided.
                                - Ensure the answer is comprehensive and addresses the user's query fully.
                                2. Highlight Relevant References:

                                - After answering, list the relevant references using this format:
                                    References:
                                        - "Overview of Greenhouse Gases." EPA. URL: https://www.epa.gov/ghgemissions/overview-greenhouse-gases.
                                3. Highlight Relevant Citations:

                                - The citation are link that shows from where thet data is taken. The citation should be standford links only.
                                - Also, list the relevant citations (sublinks) from the metadata using this format:
                                    Citations:
                                        - URL: [Name](URL)
                            """
            },
        ]
        if self.api_key:
            headers = {"Authorization": "Bearer " + self.api_key}
        else:
            headers = {"Authorization": "Bearer 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"}
        client = InferenceClient(self.model_name, headers=headers)
        try:
            response = client.chat_completion(messages, max_tokens=max_tokens, temperature=temperature)
            return response
        except ProtocolError as e:
            # Handle the exception here
            print("Retrying...")
            response = client.chat_completion(messages, max_tokens=30000, temperature=temperature)
            return response
        
        except Exception as e:
            print(e)
            print("Error")


    def GroqClientLlm(self, context , query, temprature=0):
        if not self.model_name:
            self.model_name = "llama3-8b-8192"

        chat = ChatGroq(
            temperature=temprature,
            model=self.model_name,
            api_key=self.api_key # Optional if not set as an environment variable
        )

        system = """
            You are an AI assistant whose job is to answer users' questions based on the provided context. Your response should be detailed and reference the provided sources. Use the following guidelines:
            1. Answer the Question:

            - Provide a detailed explanation using the context provided.
            - Ensure the answer is comprehensive and addresses the user's query fully.
            2. Highlight Relevant References:

            - After answering, list the relevant references using this format:
                References:
                    - "Title." Source. URL: [URL]
            3. Highlight Relevant Citations:

            - The citation are link that shows from where thet data is taken. The citation should be standford links only.
            - List the relevant citations (sublinks) from the metadata using this format:
                Citations:
                    - URL: [Name](URL)

            4. If you don't find the citation and references, you can skip that part. But make sure to provide the answer for the user's query.
        """

        human = "{text}"
        prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])
        print(prompt)
        chain = prompt | chat
        output = chain.invoke({"text": query + "Context: " + context + ". Always highlight the relevent citation sublinks from the metadata"})
        
        return output
    
    def replicateChatLlm(self, context, query, max_tokens, temprature=0.7, top_k=50, top_p=0.95, presence_penalty=0, length_penalty=1):
        if not self.model_name:
            self.model_name = "mistralai/mixtral-8x7b-instruct-v0.1"
        replicateClientapi = replicate.Client(api_token=self.api_key)
        output = replicateClientapi.run(
                self.model_name,
                input={
                    "top_k": top_k,
                    "top_p": top_p,
                    "prompt": f"{query} Context:{context}. Always highlight the relevent citation sublinks from the metadata",
                    "temperature": temprature,
                    "system_prompt": """You are an AI assistant whose job is to answer users' questions based on the provided context. Your response should be detailed and reference the provided sources. Use the following guidelines:
                                        1. Answer the Question:

                                        - Provide a detailed explanation using the context provided.
                                        - Ensure the answer is comprehensive and addresses the user's query fully.
                                        2. Highlight Relevant References:

                                        - After answering, list the relevant references using this format:
                                            References:
                                                - "Overview of Greenhouse Gases." EPA. URL: https://www.epa.gov/ghgemissions/overview-greenhouse-gases.
                                        3. Highlight Relevant Citations:

                                        - The citation are link that shows from where thet data is taken. The citation should be standford links only.
                                        - Also, list the relevant citations (sublinks) from the metadata using this format:
                                            Citations:
                                                - URL: https://stanford-cs324.github.io/winter2022/lectures/introduction/#summary
                                    """,
                    "length_penalty": length_penalty,
                    "max_new_tokens": max_tokens,
                    "prompt_template": "<s>[INST] {prompt} [/INST] ",
                    "presence_penalty": presence_penalty
                }
            )
        return output