import os
from dotenv import load_dotenv
from lightspark import LightsparkSyncClient
from openai import OpenAI

load_dotenv()

# Setup Lightspark client
client = LightsparkSyncClient(
    api_token_client_id=os.getenv("LIGHTSPARK_API_TOKEN_CLIENT_ID"),
    api_token_client_secret=os.getenv("LIGHTSPARK_API_TOKEN_CLIENT_SECRET"),
)
node_id = os.getenv("LIGHTSPARK_NODE_ID")
node_password = os.getenv("LIGHTSPARK_NODE_PASSWORD")
signing_key = client.recover_node_signing_key(node_id, node_password)
client.load_node_signing_key(node_id, signing_key)

# Create a test invoice
test_invoice = client.create_test_mode_invoice(
    local_node_id=node_id,
    amount_msats=42000,
    memo="Pizza!",
)

# Setup OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Function that OpenAI can call
def pay_invoice(invoice: str) -> str:
    try:
        payment = client.pay_invoice(
            node_id=node_id,
            encoded_invoice=invoice,
            timeout_secs=60,
            maximum_fees_msats=1000,
        )
        return f"Payment successful: {payment}"
    except Exception as e:
        return f"Payment failed: {str(e)}"

# Define the function for OpenAI
tools = [
    {
        "type": "function",
        "function": {
            "name": "pay_invoice",
            "description": "Pay a Lightning Network invoice",
            "parameters": {
                "type": "object",
                "properties": {
                    "invoice": {
                        "type": "string",
                        "description": "The Lightning Network invoice to pay"
                    }
                },
                "required": ["invoice"]
            }
        }
    }
]

# Create conversation with the AI
messages = [
    {"role": "system", "content": "You are a helpful assistant that can pay Lightning Network invoices."},
    {"role": "user", "content": f"Please pay this Lightning invoice: {test_invoice}"}
]

# Get AI response
response = openai_client.chat.completions.create(
    model="gpt-4",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)

# Handle the response
message = response.choices[0].message
if message.tool_calls:
    # Execute the function call
    function_call = message.tool_calls[0]
    function_args = eval(function_call.function.arguments)
    result = pay_invoice(function_args['invoice'])
    
    # Get final response from AI
    messages.append(message)
    messages.append({"role": "tool", "content": result, "tool_call_id": function_call.id})
    final_response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )
    print(final_response.choices[0].message.content)
