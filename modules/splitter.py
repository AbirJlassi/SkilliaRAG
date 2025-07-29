# modules/splitter.py

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from typing import List

def splitdocuments(documents: List[Document],
                    chunk_size: int = 1000,
                    chunk_overlap: int = 150) -> List[Document]:
    """
    Découpe une liste de documents en chunks avec overlap pour la vectorisation.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " "]
    )
    return splitter.split_documents(documents)
