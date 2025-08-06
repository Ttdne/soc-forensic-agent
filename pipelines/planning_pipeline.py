from agents.plan_agent import PlanAgent
from agents.contexts.planning_state import PlanningState

def run_planning_pipeline(user_input: str, planning_state: PlanningState):
    agent = PlanAgent(role_name="Product_Owner")    # Example only
    result = agent.run(user_input)
    state_dir = agent.state_dir
    return result, state_dir
