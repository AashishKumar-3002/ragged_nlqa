import json
import copy
from typing import Iterable, List, Optional
import spacy.cli
from langchain.text_splitter import SpacyTextSplitter
from langchain_core.documents import Document

class UniSplitter:
    def __init__(
        self,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        add_start_index: bool = False,
        use_sizeoverlap: Optional[bool] = False,
        allow_chunk_oversize: Optional[bool] = False,
        model_name: str = "en_core_web_md",
    ) -> None:
        """Initialize with chunk size and overlap."""
        self.chunk_size = int(chunk_size) if chunk_size is not None else None
        self.chunk_overlap = int(chunk_overlap) if chunk_overlap is not None else None
        self.use_sizeoverlap = use_sizeoverlap
        self._add_start_index = add_start_index
        self._allow_chunk_oversize = allow_chunk_oversize
        self.model_name = model_name
        #try to load the model if not available then download it
        try:
            spacy.load(model_name)
        except OSError:
            spacy.cli.download(model_name)
        except Exception as e:
            print(f"An error occurred: {e}")


    def split_text_in_json(self, texts: List[str], metadatas: Optional[List[dict]] = None) -> List[Document]:
        """
        Splits the text in the JSON file into chunks using SpacyTextSplitter and saves the result.
        
        Parameters:
            model_name (str): The name of the Spacy model to use. Defaults to 'en_core_web_md'.
        """
        # Download the Spacy model if not available
        try:
            # Initialize the SpacyTextSplitter
            if self.use_sizeoverlap and self.chunk_size and self.chunk_overlap and self._allow_chunk_oversize:
                text_splitter = SpacyTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap, pipeline=self.model_name)
            else:
                text_splitter = SpacyTextSplitter(pipeline=self.model_name)
            
            # Process each item in the json data
            _metadatas = metadatas or [{}] * len(texts)
            all_texts = []
            for i, text in enumerate(texts):
                index = 0
                previous_chunk_len = 0
                chunks = text_splitter.split_text(text)

                # Further split chunks if they exceed the chunk_size
                if self.chunk_size and not self._allow_chunk_oversize and self.use_sizeoverlap:
                    chunks = self._split_large_chunks(chunks)

                for chunk in chunks:
                    metadata = copy.deepcopy(_metadatas[i])
                    if self._add_start_index:
                        offset = index + previous_chunk_len - (self.chunk_overlap if self.chunk_overlap else 0)
                        index = text.find(chunk, max(0, offset))
                        metadata['start_index'] = index
                        previous_chunk_len = len(chunk)
                    new_doc = Document(page_content=chunk, metadata=metadata)
                    all_texts.append(new_doc)
            
            print(f"Processed {len(all_texts)} items.")
            return all_texts
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
    
    def _split_large_chunks(self, chunks: List[str]) -> List[str]:
        """Split large chunks into smaller ones based on the specified chunk size."""
        split_chunks = []
        for chunk in chunks:
            if len(chunk) > self.chunk_size:
                start = 0
                while start < len(chunk):
                    end = start + self.chunk_size
                    split_chunks.append(chunk[start:end])
                    start += self.chunk_size - (self.chunk_overlap if self.chunk_overlap else 0)
            else:
                split_chunks.append(chunk)
        return split_chunks

    def split_spacy_documents(self, documents: Iterable[Document]) -> List[Document]:
        """split the spacy documents into chunks
        
        Parameters:
            documents (list): A list of Document objects containing page content and metadata.
        """
        texts, metadatas = [], []
        for doc in documents:
            texts.append(doc.page_content)
            metadatas.append(doc.metadata)
        
        return self.split_text_in_json(texts, metadatas)
