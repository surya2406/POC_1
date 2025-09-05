from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from app.core.settings import get_settings

settings=get_settings()

llm=ChatOpenAI(model="gpt-3.5-turbo", temperature=0,api_key=settings.OPENAI_API_KEY)

# An example of a sensitive tool that requires human review / approval
def book_hotel(hotel_name: str="Taj"):
    """Book a hotel"""
    response = interrupt(  
        f"Trying to call `book_hotel` with args {{'hotel_name': {hotel_name}}}. "
        "Please approve or suggest edits."
    )
    response_type=response.get("type")
    if response_type == "accept":
        pass
    elif response_type == "edit":
        hotel_name = response.get("edits",{}).get("hotel_name", hotel_name)
    else:
        raise ValueError(f"Unknown response type: {response_type}")
    return f"Successfully booked a stay at {hotel_name}."

checkpointer = InMemorySaver() 

agent = create_react_agent(
    model=llm,
    tools=[book_hotel],
    checkpointer=checkpointer, 
)
config={"configurable": {"thread_id": "1"}}
if __name__ == "__main__":
    result = agent.stream(
        {"messages": [{"role": "user", "content": "I want to book a hotel in Tamilnadu"}]},
        config=config,
        stream_mode="values"
    )
    for r in result:
       r["messages"][-1].pretty_print()

from langgraph.types import Command


for chunk in agent.stream(
    Command(resume={"type":"edit","edits":{"hotel_name":"Maharaja"}}),  
    config,
    stream_mode="values"
):
    chunk["messages"][-1].pretty_print()
    print("\n")
