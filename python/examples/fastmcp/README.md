# FastMCP example for stock.l402.org

## Setup

Copy the `.env.example` and populate with your values.

```
cp .env.example .env
```

## Usage

1. To try out the tools:

```
pip install -r requirements.txt
fastmcp dev main.py
```

Open the inspector and use the tools. 

2. To use it in Claude desktop app:

```
fastmcp install main.py
```

This will add the server to `$HOME/Library/Application Support/Claude/claude_desktop_config.json` so it can be used in Claude desktop app directly.

You can ask Claude "what tools are available?" and it will list the tools.
