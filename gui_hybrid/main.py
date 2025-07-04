import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gui_hybrid.action_router import ActionRouter
from gui_hybrid.llm_planner import LLMPlanner
from agents.hybrid_llm_connector import HybridLLMConnector

def main():
    """
    Demo: prompt user for intent, run hybrid GUI automation pipeline with Ollama LLM.
    """
    llm_connector = HybridLLMConnector({})
    planner = LLMPlanner(llm=llm_connector)
    router = ActionRouter()
    router.planner = planner  # Inject the LLM-connected planner
    user_intent = input("What do you want nexus to do? ")
    router.run_action(user_intent)

if __name__ == "__main__":
    main() 