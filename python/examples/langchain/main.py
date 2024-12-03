import os
from dotenv import load_dotenv
from lightspark import LightsparkSyncClient
import requests
import sys

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain.tools import StructuredTool

from pydantic import BaseModel

load_dotenv()

def setup_lightspark_client():
    # Initialize client
    client = LightsparkSyncClient(
        api_token_client_id=os.getenv("LIGHTSPARK_API_TOKEN_CLIENT_ID"),
        api_token_client_secret=os.getenv("LIGHTSPARK_API_TOKEN_CLIENT_SECRET"),
    )
    
    # Load node credentials
    node_id = os.getenv("LIGHTSPARK_NODE_ID")
    node_password = os.getenv("LIGHTSPARK_NODE_PASSWORD")
    
    # Recover and load signing key
    signing_key = client.recover_node_signing_key(node_id, node_password)
    client.load_node_signing_key(node_id, signing_key)
    
    return client, node_id

# Setup client and node before LangChain initialization
lightspark_client, default_node_id = setup_lightspark_client()

BASE_URL = "http://stock.l402.org"

def signup():
    response = requests.get(f"{BASE_URL}/signup")
    user_id = response.json()["id"]
    return user_id

def get_headers(user_id):
    return {"Authorization": f"Bearer {user_id}"}

user_id = signup()
headers = get_headers(user_id)



# Create a tool for getting stock prices
def get_stock_price(symbol: str):
    response = requests.get(f"{BASE_URL}/ticker/{symbol}", headers=headers)
    if response.status_code == 402:
        # Get the first offer to pay 1 credit
        offer = response.json()["offers"][0]
        # Get the invoice from the first payment method (lightning)
        invoice = offer["payment_methods"][0]["payment_details"]["payment_request"]
        
        # Pay the invoice using our existing lightspark client
        lightspark_client.pay_invoice(
            node_id=default_node_id,
            encoded_invoice=invoice,
            timeout_secs=10,
            maximum_fees_msats=1000
        )
        
        # Retry the ticker request
        response = requests.get(f"{BASE_URL}/ticker/{symbol}", headers=headers)
    
    return response.json()

class StockPriceSchema(BaseModel):
    symbol: str

stock_price_tool = StructuredTool(
    name="get_stock_price",
    description="Get the current price of a stock by its ticker symbol (e.g., TSLA, MSFT)",
    func=get_stock_price,
    args_schema=StockPriceSchema
)

# Initialize LLM and agent
llm = ChatOpenAI(model="gpt-4o", verbose=True)

# Update tools list
tools = [stock_price_tool]
langgraph_agent_executor = create_react_agent(llm, tools)

if __name__ == "__main__":  
    # Example usage
    # python main.py "Compare the stock prices of Tesla (TSLA) and Microsoft (MSFT)."
    prompt = sys.argv[1] if len(sys.argv) > 1 else """Compare the stock prices of Tesla (TSLA) and Microsoft (MSFT)."""

    input_state = {
        "messages": prompt
    }

    output_state = langgraph_agent_executor.invoke(input_state)
    print(output_state["messages"][-1].content)
