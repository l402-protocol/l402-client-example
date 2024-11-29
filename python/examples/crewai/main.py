import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from lightspark import LightsparkSyncClient
from crewai_tools import BaseTool

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

# Simple tool implementations
class CreateInvoiceTool(BaseTool):
    name: str = "create_invoice"
    description: str = "Create a Lightning Network test invoice"

    def _run(self, amount_msats: int = 50000, memo: str = "Test Payment"):
        return client.create_test_mode_invoice(
            local_node_id=node_id,
            amount_msats=amount_msats,
            memo=memo,
        )

class PayInvoiceTool(BaseTool):
    name: str = "pay_invoice"
    description: str = "Pay a Lightning Network invoice"

    def _run(self, invoice: str):
        return client.pay_invoice(
            node_id=node_id,
            encoded_invoice=invoice,
            timeout_secs=60,
            maximum_fees_msats=1000,
        )

# Create agents
invoice_creator = Agent(
    role="Invoice Creator",
    goal="Create Lightning Network invoices for payments",
    backstory="You are an expert at creating Lightning Network invoices.",
    tools=[CreateInvoiceTool()],
    verbose=True,
)

invoice_payer = Agent(
    role="Invoice Payer",
    goal="Process Lightning Network payments efficiently",
    backstory="You are specialized in processing Lightning Network payments.",
    tools=[PayInvoiceTool()],
    verbose=True,
)

# Create tasks
create_invoice_task = Task(
    description="Create a test invoice for 20 sats with the memo 'Test Payment'",
    expected_output="A Lightning Network invoice string",
    agent=invoice_creator
)

pay_invoice_task = Task(
    description="Pay the Lightning Network invoice that was created",
    expected_output="Payment confirmation details",
    agent=invoice_payer
)

# Run the crew
crew = Crew(
    agents=[invoice_creator, invoice_payer],
    tasks=[create_invoice_task, pay_invoice_task],
    verbose=True
)

result = crew.kickoff()