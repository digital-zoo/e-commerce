from langchain_community.utilities import SQLDatabase
from langchain.chains.sql_database.query import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from operator import itemgetter
import os
from langchain_community.chat_models import ChatOpenAI
import dotenv
dotenv.load_dotenv()

db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("MY_DB_PASSWORD")

database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

db = SQLDatabase.from_uri(database_url)

llm = ChatOpenAI(temperature=0)  # gpt-4-turbo

def write_query(question: str) -> str:
    messages = [{"role": "user", "content": question}]
    response = llm(messages=messages)
    return response["choices"][0]["message"]["content"] if "choices" in response and len(response["choices"]) > 0 else ""

write_query = create_sql_query_chain(llm, db)

execute_query = QuerySQLDataBaseTool(db=db)

answer_prompt = PromptTemplate.from_template(
    """주어진 유저 질문에 대해서, corresponding SQL query, and SQL result, answer the user question.
    Question: {question}
    SQL Query: {query}
    SQL Result: {result}
    Answer: 
    "You are a nice customer service agent."
    "Do your best to answer the questions. "
    "Feel free to use any tools available to look up "
    "relevant information, only if necessary"
    "If you don't know the answer, just say you don't know. Don't try to make up an answer."
    "Make sure to answer in Korean"

    """
)

parser = StrOutputParser()

answer = answer_prompt | llm | parser

chain = (
    RunnablePassthrough.assign(query=write_query).assign(
        result=itemgetter("query") | execute_query
    )
    | answer
)

def ask_question(question: str) -> str:
    try:
        response = chain.invoke({"question": question})
        if isinstance(response, dict) and 'Answer' in response:
            return response['Answer']
        elif isinstance(response, str):
            return response
    except ValueError as e:
        return str(e)  # 접근할 수 없는 테이블에 접근하려고 하면 예외 메시지를 반환합니다.
    except Exception as e:
        return "An unexpected error occurred: " + str(e)
    return "Unexpected response format"