from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 필요에 따라 특정 도메인만 허용하도록 수정 가능
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": request.message}
            ]
        )
        return {"response": response.choices[0].message['content']}
    except openai.error.OpenAIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI Error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected Error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
