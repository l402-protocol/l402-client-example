from fastmcp import FastMCP
import aiohttp
import os
from lightspark import LightsparkSyncClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastMCP server instance
mcp = FastMCP("Stock L402 Server", dependencies=["aiohttp", "lightspark-sdk", "python-dotenv"])

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

@mcp.tool()
async def signup() -> str:
    """Create a new user account for the stock API"""
    async with aiohttp.ClientSession() as session:
        async with session.get('https://stock.l402.org/signup') as response:
            data = await response.json()
            return f"Successfully created account. Your bearer token is: {data['id']}"

@mcp.tool()
async def get_stock(ticker: str, bearer_token: str) -> str:
    """
    Get financial data for a specific stock symbol
    
    Args:
        ticker: Stock ticker symbol (e.g., AAPL)
        bearer_token: Bearer token obtained from signup
    """
    headers = {"Authorization": f"Bearer {bearer_token}"}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://stock.l402.org/ticker/{ticker}', headers=headers) as response:
            data = await response.json()
            return f"Response status: {response.status}\nResponse data: {data}"

@mcp.tool()
async def get_user_info(bearer_token: str) -> str:
    """
    Get current user information including credit balance
    
    Args:
        bearer_token: Bearer token obtained from signup
    """
    headers = {"Authorization": f"Bearer {bearer_token}"}
    
    async with aiohttp.ClientSession() as session:
        async with session.get('https://stock.l402.org/info', headers=headers) as response:
            data = await response.json()
            return f"User Info: {data}"

@mcp.tool()
async def pay_lightning(payment_request: str) -> str:
    """
    Pay a Lightning Network invoice using Lightspark
    
    Args:
        payment_request: The Lightning Network payment request/invoice to pay
    """
    client, node_id = setup_lightspark_client()
    
    result = client.pay_invoice(
        node_id=node_id,
        encoded_invoice=payment_request,
        timeout_secs=10,
        maximum_fees_msats=1000,
    )
    
    return f"Payment successful! Payment ID: {result.id}"

if __name__ == "__main__":
    mcp.run()