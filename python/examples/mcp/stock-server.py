import os
import aiohttp

import mcp.types as types
import mcp.server.stdio
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions

from lightspark import LightsparkSyncClient

from dotenv import load_dotenv

# load_dotenv()
load_dotenv('/Users/pengren/go/github.com/l402-protocol/l402-client-example/mcp/.env')

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


# Create server instance
server = Server("stock-l402-server")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="signup",
            description="Create a new user account for the stock API",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="get_stock",
            description="Get financial data for a specific stock symbol",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., AAPL)"
                    },
                    "bearer_token": {
                        "type": "string",
                        "description": "Bearer token obtained from signup"
                    }
                },
                "required": ["ticker", "bearer_token"]
            }
        ),
        types.Tool(
            name="get_user_info",
            description="Get current user information including credit balance",
            inputSchema={
                "type": "object",
                "properties": {
                    "bearer_token": {
                        "type": "string",
                        "description": "Bearer token obtained from signup"
                    }
                },
                "required": ["bearer_token"]
            }
        ),
        types.Tool(
            name="pay_lightning",
            description="Pay a Lightning Network invoice using Lightspark",
            inputSchema={
                "type": "object",
                "properties": {
                    "payment_request": {
                        "type": "string",
                        "description": "The Lightning Network payment request/invoice to pay"
                    }
                },
                "required": ["payment_request"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "signup":
        async with aiohttp.ClientSession() as session:
            async with session.get('https://stock.l402.org/signup') as response:
                data = await response.json()
                return [types.TextContent(
                    type="text",
                    text=f"Successfully created account. Your bearer token is: {data['id']}"
                )]

    elif name == "get_stock":
        ticker = arguments["ticker"]
        bearer_token = arguments["bearer_token"]
        headers = {
            "Authorization": f"Bearer {bearer_token}"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://stock.l402.org/ticker/{ticker}', headers=headers) as response:
                data = await response.json()
                return [types.TextContent(
                    type="text",
                    text=f"Response status: {response.status}\nResponse data: {data}"
                )]
    elif name == "get_user_info":
        bearer_token = arguments["bearer_token"]
        headers = {
            "Authorization": f"Bearer {bearer_token}"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get('https://stock.l402.org/info', headers=headers) as response:
                data = await response.json()
                return [types.TextContent(
                    type="text",
                    text=f"User Info: {data}"
                )]
    elif name == "pay_lightning":
        payment_request = arguments["payment_request"]
        
        client, node_id = setup_lightspark_client()
        
        result = client.pay_invoice(
            node_id=node_id,
            encoded_invoice=payment_request,
            timeout_secs=10,
            maximum_fees_msats=1000,
        )
        
        return [types.TextContent(
            type="text",
                text=f"Payment successful! Payment ID: {result.id}"
            )]
            

async def run():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="stock-l402",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                )
            )
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(run())