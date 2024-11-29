import os
from dotenv import load_dotenv
from lightspark import LightsparkSyncClient

from langchain import hub
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

# Create a tool for paying Lightning invoices
def pay_lightning_invoice(encoded_invoice: str, amount_msats: int = None):
    return lightspark_client.pay_invoice(
        node_id=default_node_id,
        encoded_invoice=encoded_invoice,
        timeout_secs=60,
        maximum_fees_msats=1000,
        amount_msats=amount_msats
    )

class LightningPaySchema(BaseModel):
    encoded_invoice: str

lightning_pay_tool = StructuredTool(
    name="pay_lightning_invoice",
    description="Pay a Lightning Network invoice",
    func=pay_lightning_invoice,
    args_schema=LightningPaySchema
)

# Initialize LLM and agent
llm = ChatOpenAI(model="gpt-4")

tools = [lightning_pay_tool]
langgraph_agent_executor = create_react_agent(llm, tools)

# Let's manually create a test invoice
test_invoice = lightspark_client.create_test_mode_invoice(
    local_node_id=default_node_id,
    amount_msats=42000,
    memo="Pizza!",
)


# Example usage
input_state = {
    "messages": f"""
        Pay this Lightning invoice:
        {test_invoice}
    """
}


output_state = langgraph_agent_executor.invoke(input_state)
print(output_state["messages"][-1].content)
