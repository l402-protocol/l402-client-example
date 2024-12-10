# MCP example for stock.l402.org

## Setup

Copy the `.env.example` and populate with your values.

```
cp .env.example .env
```

## Usage

Install the dependencies:

```
pip install -r requirements.txt
```

Make the server available in Claude desktop app by adding it to the `mcpServers` section in `claude_desktop_config.json`.

```
echo "$HOME/Library/Application Support/Claude/claude_desktop_config.json"
{
  "mcpServers": {
    "stock": {
      "command": "/Users/pengren/go/github.com/l402-protocol/l402-client-example/mcp/venv/bin/python",
      "args": [
        "/Users/pengren/go/github.com/l402-protocol/l402-client-example/mcp/stock-server.py"
      ]
    }
  }
}
```

You can ask Claude "what tools are available?" and it will list the tools.
