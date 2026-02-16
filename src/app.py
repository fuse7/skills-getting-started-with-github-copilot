"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(
    title="Mergington High School API",
    description="API for viewing and signing up for extracurricular activities"
)

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(current_dir, "static")),
    name="static"
)

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },

    # ✅ Sports
    "Soccer Team": {
        "description": "Practice soccer skills and compete with other schools",
        "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participants": []
    },
    "Basketball Team": {
        "description": "Train and play competitive basketball games",
        "schedule": "Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": []
    },

    # ✅ Artistic
    "Art Club": {
        "description": "Create paintings, drawings, and digital art",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": []
    },
    "Drama Club": {
        "description": "Acting, improvisation, and stage performances",
        "schedule": "Mondays, 4:00 PM - 5:30 PM",
        "max_participants": 14,
        "participants": []
    },

    # ✅ Intellectual
    "Math Club": {
        "description": "Solve challenging math problems and puzzles",
        "schedule": "Fridays, 2:30 PM - 3:30 PM",
        "max_participants": 12,
        "participants": []
    },
    "Robotics Club": {
        "description": "Build and program robots",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": []
    }
}



@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""

    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        return {"message": "Student already signed up for this activity"}

    # Add student
    activity["participants"].append(email)

    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/remove")
def remove_participant(activity_name: str, email: str):
    """Remove a student from an activity"""

    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Check if participant is registered
    if email not in activity["participants"]:
        raise HTTPException(status_code=404, detail="Participant not found in this activity")

    # Remove student
    activity["participants"].remove(email)

    return {"message": f"Removed {email} from {activity_name}"}
