from fastapi import FastAPI

app = FastAPI(title="Underwater Target Detection System")


@app.get("/")
def root() -> dict:
    return {"message": "Backend is running."}
