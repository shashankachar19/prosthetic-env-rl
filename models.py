from pydantic import BaseModel

class ProstheticAction(BaseModel):
    # Action: -1 (loosen grip), 0 (hold), 1 (tighten grip)
    force_change: int

class ProstheticObservation(BaseModel):
    # What the AI sees
    current_grip: int
    target_grip: int
    done: bool
    reward: float