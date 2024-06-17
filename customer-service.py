from langchain.text_splitter import RecursiveCharacterTextSplitter
#from langchain.document_loaders import WebBaseLoader
#from langchain.embeddings import OpenAIEmbeddings
#from langchain.vectorstores import Chroma
from langchain.schema.document  import Document
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders.sql_database import SQLDatabaseLoader
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import dotenv
dotenv.load_dotenv()
import streamlit as st
import time
import os
import psycopg2
#from langchain.chat_models import ChatOpenAI
from langchain_community.chat_models import ChatOpenAI
from langchain.sql_database import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("MY_DB_PASSWORD")
## 수동 연결
# # PostgreSQL 데이터베이스에 연결
# conn = psycopg2.connect(
#     host=db_host,
#     port=db_port,
#     database=db_name,
#     user=db_user,
#     password=db_password
# )


# # 커서 생성
# cur = conn.cursor()

# # 모든 테이블 이름을 조회
# cur.execute("""
# SELECT table_name 
# FROM information_schema.tables
# WHERE table_schema = 'public'
# """)

# tables = cur.fetchall()
# #print("Tables in the database:", tables)

# documents = []
# for table in tables:
#     table_name = table[0]
#     cur.execute(f"SELECT * FROM {table_name};")
#     rows = cur.fetchall()
#     for row in rows:
#         # 각 row에서 필요한 데이터를 추출하여 Document 형태로 변환
#         # 여기서는 첫 번째 열을 id로, 두 번째 열을 content로 가정
#         doc_content = str(row[1]) if len(row) > 1 and row[1] is not None else ""
#         documents.append(Document(page_content=doc_content, metadata={"table": table_name, "id": row[0]}))

# cur.close()
# conn.close()

#loader = WebBaseLoader("https://dalpha.so/ko/howtouse?scrollTo=custom")
#loader = WebBaseLoader("https://www.coupang.com/np/policies/loyalty")

#data = loader.load()
database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
# SQLDatabaseLoader를 사용하여 데이터베이스에서 데이터 로드
db = SQLDatabase.from_uri(database_url)
db.get_usable_table_names()
query = "SELECT * FROM seller_product;"
loader = SQLDatabaseLoader(db=db, query=query)
documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size = 500, chunk_overlap = 0)

all_splits = text_splitter.split_documents(documents)

vectorstore = Chroma.from_documents(documents=all_splits, embedding=OpenAIEmbeddings())

retriever = vectorstore.as_retriever()

from langchain.agents.agent_toolkits import create_retriever_tool

tool = create_retriever_tool(
    retriever,
    "PostgreSQL_database_retriever",
    "Searches and returns information from the PostgreSQL database.",
    # "Dalpha_customer_service_guide",
    # "Searches and returns information regarding the customer service guide.",
)
tools = [tool]

llm = ChatOpenAI(temperature=0)
chain = create_sql_query_chain(llm,db)

# This is needed for both the memory and the prompt
memory_key = "history"

from langchain.agents.openai_functions_agent.agent_token_buffer_memory import (
    AgentTokenBufferMemory,
)

memory = AgentTokenBufferMemory(memory_key=memory_key, llm=llm)

from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent
from langchain.schema.messages import SystemMessage
from langchain.prompts import MessagesPlaceholder

system_message = SystemMessage(
    content=(
        "You are a nice customer service agent."
        "Do your best to answer the questions. "
        "Feel free to use any tools available to look up "
        "relevant information, only if necessary"
        "If you don't know the answer, just say you don't know. Don't try to make up an answer."
        "Make sure to answer in Korean"
    )
)

prompt = OpenAIFunctionsAgent.create_prompt(
    system_message=system_message,
    extra_prompt_messages=[MessagesPlaceholder(variable_name=memory_key)],
)

agent = OpenAIFunctionsAgent(llm=llm, tools=tools, prompt=prompt)

from langchain.agents import AgentExecutor

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True,
    return_intermediate_steps=True,
)

# result = agent_executor({"input": "어떻게 Dalpha AI를 사용하나요?"})
# result["output"]

st.title("AI 고객 서비스 상담원")

# Set a default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        result = agent_executor({"input": prompt})
        for chunk in result['output'].split():
            full_response += chunk + " "
            time.sleep(0.05)

            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})