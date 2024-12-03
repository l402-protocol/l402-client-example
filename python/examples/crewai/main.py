import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from lightspark import LightsparkSyncClient
from crewai_tools import BaseTool
import requests
import sys

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
client, node_id = setup_lightspark_client()

BASE_URL = "http://stock.l402.org"

def signup():
    response = requests.get(f"{BASE_URL}/signup")
    user_id = response.json()["id"]
    return user_id

def get_headers(user_id):
    return {"Authorization": f"Bearer {user_id}"}

user_id = signup()
headers = get_headers(user_id)


class GetTickerTool(BaseTool):
    name: str = "get_ticker"
    description: str = "Get the current price of a stock"

    def _run(self, symbol: str):
        response = requests.get(f"{BASE_URL}/ticker/{symbol}", headers=headers)
        if response.status_code == 402:
            # Get the lightning invoice from the first offer (cheapest)
            payment_info = response.json()["offers"][0]
            lightning_payment = next(
                pm for pm in payment_info["payment_methods"] 
                if pm["payment_type"] == "lightning"
            )
            invoice = lightning_payment["payment_details"]["payment_request"]
            
            # Pay the invoice
            client.pay_invoice(
                node_id=node_id,
                encoded_invoice=invoice,
                timeout_secs=10,
                maximum_fees_msats=1000
            )
            
            # Retry the ticker request
            response = requests.get(f"{BASE_URL}/ticker/{symbol}", headers=headers)
        
        return response.json()

# Create an agent that can compare stock prices
financial_analyst = Agent(
    name="Financial Analyst",
    role="Analyze financial data and provide insights",
    goal="Analyze the financial data and provide insights",
    backstory="An AI agent specialized in financial analysis",
    tools=[GetTickerTool()],
)

if __name__ == "__main__":
    # Example usage
    # python main.py "Compare the stock prices of Tesla (TSLA) and Microsoft (MSFT)."
    task_description = sys.argv[1] if len(sys.argv) > 1 else """Compare the stock prices of Tesla and Microsoft."""

    task = Task(
        description=task_description,
        expected_output="Analysis result",
        agent=financial_analyst
    )

    # Create and run the crew
    crew = Crew(
        agents=[financial_analyst],
        tasks=[task],
        verbose=True,
    )

    result = crew.kickoff()
    print(result)


