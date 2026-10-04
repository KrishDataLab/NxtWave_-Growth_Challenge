from fastapi import FastAPI

app = FastAPI()

@app.get("/api/v1/health")
@app.get("/v1/health")
@app.get("/health")
def health():
    return {"status": "healthy", "service": "NxtWave Growth Challenge API", "version": "1.0.0"}
