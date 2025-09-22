import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS

def build_index(docs_path="wiki_docs/"):
    # 문서 로드
    loader = DirectoryLoader(docs_path, glob="*.md", loader_cls=TextLoader)
    documents = loader.load()

    # 분할
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_documents(documents)

    # 임베딩
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    db = FAISS.from_documents(chunks, embeddings)
    db.save_local("faiss_index")
    print("✅ 위키 문서 인덱싱 완료, faiss_index/ 에 저장됨")

if __name__ == "__main__":
    build_index()
