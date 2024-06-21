import logging
from typing import List, Optional
from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader
from langchain_community.document_loaders.helpers import detect_file_encodings
from ragged_nlqs.ingestion.spacy_splitter import UniSplitter
import json

logger = logging.getLogger(__name__)

class UniTextLoader(BaseLoader):
    def __init__(self, file_path: str, encoding: Optional[str] = None, autodetect_encoding: bool = False):
        self.file_path = file_path
        self.encoding = encoding
        self.autodetect_encoding = autodetect_encoding

    def load(self) -> List[Document]:
        documents = []
        try:
            with open(self.file_path, "r", encoding=self.encoding) as f:
                data = json.load(f)
                for file_data in data:
                    title = file_data['title']
                    text = file_data['text']
                    author = file_data.get('author', '')
                    hostname = file_data.get('hostname', '')
                    date = file_data.get('date', '')
                    fingerprint = file_data.get('fingerprint', '')
                    source = file_data.get('source', '')
                    source_hostname = file_data.get('source-hostname', '')
                    excerpt = file_data.get('excerpt', '')
                    sublinks = file_data.get('metadata', '')

                    metadata = {
                        "title": title,
                        "author": author,
                        "hostname": hostname,
                        "date": date,
                        "fingerprint": fingerprint,
                        "source": source,
                        "source_hostname": source_hostname,
                        "excerpt": excerpt,
                        "sublinks": str(sublinks)
                    }
                    document = Document(page_content=text, metadata=metadata)
                    documents.append(document)
        except UnicodeDecodeError as e:
            if self.autodetect_encoding:
                detected_encodings = detect_file_encodings(self.file_path)
                for encoding in detected_encodings:
                    logger.debug("Trying encoding: ", encoding.encoding)
                    try:
                        with open(self.file_path, "r", encoding=encoding.encoding) as f:
                            data = json.load(f)
                            for file_data in data:
                                title = file_data['title']
                                text = file_data['text']
                                author = file_data.get('author', '')
                                hostname = file_data.get('hostname', '')
                                date = file_data.get('date', '')
                                fingerprint = file_data.get('fingerprint', '')
                                source = file_data.get('source', '')
                                source_hostname = file_data.get('source-hostname', '')
                                excerpt = file_data.get('excerpt', '')
                                sublinks = file_data.get('metadata', '')

                                metadata = {
                                    "title": title,
                                    "author": author,
                                    "hostname": hostname,
                                    "date": date,
                                    "fingerprint": fingerprint,
                                    "source": source,
                                    "source_hostname": source_hostname,
                                    "excerpt": excerpt,
                                    "sublinks": str(sublinks)
                                }
                                document = Document(page_content=text, metadata=metadata)
                                documents.append(document)
                        break
                    except UnicodeDecodeError:
                        continue
            else:
                raise RuntimeError(f"Error loading {self.file_path}") from e
        except Exception as e:
            raise RuntimeError(f"Error loading {self.file_path}") from e

        return documents


class UniTextProcessor:
    def __init__(self, loader: BaseLoader, chunk_size: Optional[int] = None, chunk_overlap: Optional[int] = None, use_sizeoverlap: Optional[bool] = False , add_start_index: Optional[bool] = False , allow_chunk_oversize: Optional[bool] = False , spacy_model: str = 'en_core_web_md') -> None:
        self.loader = loader
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.use_sizeoverlap = use_sizeoverlap
        self.add_start_index = add_start_index
        self.allow_chunk_oversize = allow_chunk_oversize
        self.spacy_model = spacy_model

    def spacy_process_documents(self) -> List[str]:
        documents = self.loader.load()
        spacy_text_splitter = UniSplitter(
            chunk_size=self.chunk_size, 
            chunk_overlap=self.chunk_overlap, 
            use_sizeoverlap=self.use_sizeoverlap,
            add_start_index=self.add_start_index,
            allow_chunk_oversize=self.allow_chunk_oversize,
            model_name=self.spacy_model
        )
        chunks_store = []
        for doc in documents:
            new_doc = [Document(page_content=doc.page_content, metadata=doc.metadata)]
            doc_text = spacy_text_splitter.split_spacy_documents(new_doc)
            chunks_store.extend(doc_text)
        return chunks_store

# Usage example:
if __name__ == "__main__":
    loader = UniTextLoader("final_result.json", encoding="utf-8", autodetect_encoding=True)
    text_processor = UniTextProcessor(loader, use_sizeoverlap=False, chunk_size=1000, chunk_overlap=100 , add_start_index=True , allow_chunk_oversize=False , spacy_model='en_core_web_md')
    processed_chunks = text_processor.spacy_process_documents()

    print(processed_chunks)
    print(len(processed_chunks))
    print([d.page_content for d in processed_chunks])
    print([d.metadata for d in processed_chunks])

    # save the above processed data into a json file
    with open("processed_data.json", "w") as f:
        json.dump(processed_chunks, f, default=lambda x: x.__dict__)
