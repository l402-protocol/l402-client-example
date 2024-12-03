import os
import sys
import requests

from dotenv import load_dotenv

from openai import OpenAI
from lightspark import LightsparkSyncClient

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

client, node_id = setup_lightspark_client()

# Setup L402 client
BASE_URL = "http://stock.l402.org"

def signup():
    response = requests.get(f"{BASE_URL}/signup")
    return response.json()["id"]

def get_headers(user_id):
    return {"Authorization": f"Bearer {user_id}"}

user_id = signup()
headers = get_headers(user_id)

# Function that OpenAI can call
def get_stock_price(symbol: str) -> str:
    try:
        response = requests.get(f"{BASE_URL}/ticker/{symbol}", headers=headers)
        if response.status_code == 402:
            # Get payment info from response
            offer = response.json()["offers"][0]
            invoice = offer["payment_methods"][0]["payment_details"]["payment_request"]
            
            # Pay the invoice
            payment = client.pay_invoice(
                node_id=node_id,
                encoded_invoice=invoice,
                timeout_secs=10,
                maximum_fees_msats=1000,
            )
            
            # Retry the request
            response = requests.get(f"{BASE_URL}/ticker/{symbol}", headers=headers)
        
        data = response.json()
        return f"Stock data for {symbol}: {data}"
    except Exception as e:
        return f"Failed to get stock price: {str(e)}"

# Define the function for OpenAI
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": "Get stock price information",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "The stock symbol to get price information for"
                    }
                },
                "required": ["symbol"]
            }
        }
    }
]

if __name__ == "__main__":
    prompt = sys.argv[1] if len(sys.argv) > 1 else "Compare the stock prices of Microsoft and Nvidia"

    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    messages = [
        {"role": "system", "content": "You are a helpful assistant that can get stock price information."},
        {"role": "user", "content": prompt}
    ]

    while True:
        # Get AI response
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        message = response.choices[0].message
        messages.append(message)

        # Break if no tool calls
        if not message.tool_calls:
            print(message.content)
            break

        # Handle tool calls
        for tool_call in message.tool_calls:
            function_args = eval(tool_call.function.arguments)
            result = get_stock_price(function_args['symbol'])
            messages.append({
                "role": "tool",
                "content": result,
                "tool_call_id": tool_call.id
            })
