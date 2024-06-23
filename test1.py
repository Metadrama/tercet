from fastapi import FastAPI
from pydantic import BaseModel
import subprocess

app = FastAPI()

class Query(BaseModel):
    text: str

@app.post("/generate")
async def generate(query: Query):
    prompt = query.text
    result = subprocess.run(
        ["./main", "-m", "dolphin-2.7-mixtral-8x7b.Q5_K_M.gguf", "-p", prompt],
        capture_output=True,
        text=True,
        check=True
    )
    return {"response": result.stdout}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
