from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from graph import travelApp

app = FastAPI()

class TravelChatRequest(BaseModel):
    user_query: str
    session_id: str
    
class TravelFeebackRequest(BaseModel):
    session_id: str
    feedback: str
    chat_id: int

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
    
@app.post("/travel-feedback")
def userTravelFeedback(request: TravelFeebackRequest):
    #save_feedback(request.chat_id, request.session_id, request.feedback)
    return {
        "success": "success",
        "feedback": request.feedback
    }

@app.post("/travel-request")
def usertraveRequest(request: TravelChatRequest):
    
    result = travelApp.invoke({
        "user_query": request.user_query,
        "session_id": request.session_id,
        "destination": "",
        "source": "",
        "minimum_budget": 0,
        "maximum_budget": 0,
        "destination_latitude": "",
        "destination_longitude": "",
        "destination_display_name": "",
        "result": ""
    }) 
    return {
        "user_query": request.user_query,
        "answer": result["itinerary"]
    } 
    