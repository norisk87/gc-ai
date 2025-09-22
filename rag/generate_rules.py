from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.vectorstores import FAISS

def generate_rules():
    # 벡터 DB 로드
    db = FAISS.load_local("faiss_index", OpenAIEmbeddings(model="text-embedding-3-large"))
    retriever = db.as_retriever(search_kwargs={"k":4})

    # LLM 연결
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

    # 규칙 생성 프롬프트
    prompt = """
    JVM GC 튜닝 규칙을 YAML DSL로 만들어라.
    각 규칙은 id, when, severity, advice 필드를 가져야 한다.
    """
    res = qa.run(prompt)

    with open("rules/rules.yaml","w",encoding="utf-8") as f:
        f.write(res)

    print("✅ 규칙 생성 완료 → rules/rules.yaml")

if __name__ == "__main__":
    generate_rules()
