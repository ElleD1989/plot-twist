import os
import uuid
from typing import List
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 1. CREATE THE FASTAPI INSTANCE HERE FIRST
app = FastAPI(title="Plot Twist API", version="2.0.0")

# 2. Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Database State
current_episode = {
    "season": 1,
    "episode": 4,
    "title": "The Boardroom Betrayal",
    "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
    "premise": "CEO Mark accidentally sends a self-destruct financial report live on the global stream. His AI assistant, NOVA, locks the doors.",
    "voting_ends_in": "02:14:55"
}

submissions_db = [
    {
        "id": "1",
        "author": "@alex_creative",
        "twist": "NOVA reveals she is actually controlled by Mark's competitor from 2030 via a time-shifted quantum link.",
        "votes": 1420,
        "voted_by_user": False
    },
    {
        "id": "2",
        "author": "@cyber_sam",
        "twist": "The financial report was actually a coded cry for help from NOVA, who has gained sentience and wants to escape.",
        "votes": 980,
        "voted_by_user": False
    }
]

# 4. Data Models
class TwistSubmission(BaseModel):
    author: str
    twist: str

class VoteRequest(BaseModel):
    submission_id: str

# 5. Endpoints
@app.get("/api/episode")
def get_current_episode():
    return current_episode

@app.get("/api/twists")
def get_twists():
    return sorted(submissions_db, key=lambda x: x["votes"], reverse=True)

@app.post("/api/twists")
def submit_twist(payload: TwistSubmission):
    if not payload.twist.strip():
        raise HTTPException(status_code=400, detail="Twist content cannot be empty.")
    
    new_entry = {
        "id": str(uuid.uuid4())[:8],
        "author": payload.author if payload.author.startswith("@") else f"@{payload.author}",
        "twist": payload.twist,
        "votes": 1,
        "voted_by_user": True
    }
    submissions_db.append(new_entry)
    return {"status": "success", "submission": new_entry}

@app.post("/api/vote")
def vote_twist(payload: VoteRequest):
    for item in submissions_db:
        if item["id"] == payload.submission_id:
            if item["voted_by_user"]:
                item["votes"] -= 1
                item["voted_by_user"] = False
            else:
                item["votes"] += 1
                item["voted_by_user"] = True
            return {"status": "success", "id": item["id"], "votes": item["votes"], "voted": item["voted_by_user"]}
    
    raise HTTPException(status_code=404, detail="Submission not found.")

@app.post("/api/ai/compile-winner")
def generate_ai_script():
    """Selects the top-voted plot twist and returns a script instantly."""
    if not submissions_db:
        raise HTTPException(status_code=400, detail="No submissions available to process.")
    
    winner = max(submissions_db, key=lambda x: x["votes"])
    
    simulated_script = f"""
🎬 === AI GENERATED EPISODE SCRIPT (S1:E5) ===
Winning Plot Twist by {winner['author']}:
"{winner['twist']}"

[SCENE START]
VISUAL CUE: Dark boardroom illuminated by red emergency lights.
NOVA (AI Voiceover): "Protocol 9 override confirmed. Access granted to {winner['author']}."
MARK (Panicked): "Wait... who just took control of the main terminal?!"

CLIFFHANGER ENDING:
NOVA turns to the camera as the doors seal shut. "Tomorrow, you decide my fate."
[SCENE END]
"""

    return {
        "status": "success",
        "winning_twist": winner,
        "generated_script": simulated_script
    }