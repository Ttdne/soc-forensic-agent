from agents.contexts.planning_state import PlanningState
from pipelines.planning_pipeline import run_planning_pipeline

def run_full_planning(user_input: str):
    planning_state = PlanningState()  # can be loaded from config
    result, state_dir = run_planning_pipeline(user_input, planning_state)
    return result, state_dir
