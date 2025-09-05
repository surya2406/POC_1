from typing import Iterator, Dict, Any
from pydantic import BaseModel
from langgraph.types import Command





def run_agent(agent, req):
    cfg = {"configurable": {"thread_id": req.thread_id}}
 
    # Load state history
    state_history = list(agent.get_state(config=cfg))
 
    try:
        if state_history[-1][0].value:
            print("try")
            human_response = {"status": "resumed"}
            if req.feedback:
                human_response["feedback"] = req.feedback
 
            for step in agent.stream(Command(resume=human_response), config=cfg):
                print("⚠️ Unknown step:", step["messages"][-1])
 
            state_history = list(agent.get_state(config=cfg))
 
            try:
                if state_history[-1][0].value:
                    print("try")
                    return {"state":"interrupted","result": state_history[-1][0].value}
            except:
                if state_history[0]['messages'][-1].content:
                    print("except")
                    return {"state":"tool","result": state_history[0]['messages'][-1].content}
    except:
        if req.query:
            print("except")
            for step in agent.stream({"messages": [("user", req.query)]}, config=cfg, stream_mode="values"):
                print("⚠️ Unknown step:", step["messages"][-1])
           
            state_history = list(agent.get_state(config=cfg))
 
            try:
                if state_history[-1][0].value:
                    print("try")
                    return {"state":"interrupted","result": state_history[-1][0].value}
            except:
                if state_history[0]['messages'][-1].content:
                    print("except")
                    return {"state":"tool","result": state_history[0]['messages'][-1].content}
