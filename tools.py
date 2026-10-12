BANK_DATABASE = {
    "chk_1042": {
        "name": "Everyday Checking",
        "balance": 2073.04,
        "recent_transactions": [
            {"date": "2026-10-12", "description": "Metro Fuel", "amount": -12.50},
            {"date": "2026-10-10", "description": "Oak Street Kitchen", "amount": -42.80},
            {"date": "2026-10-09", "description": "Transfer to Savings", "amount": -400.00},
            {"date": "2026-10-08", "description": "Streaming subscription", "amount": -15.99},
            {"date": "2026-10-07", "description": "City Electric", "amount": -75.25},
        ],
    },
    "sav_8871": {
        "name": "Emergency Savings",
        "balance": 5406.25,
        "recent_transactions": [
            {"date": "2026-10-11", "description": "Interest payment", "amount": 6.25},
            {"date": "2026-10-09", "description": "Transfer from Checking", "amount": 400.00},
            {"date": "2026-10-01", "description": "Savings deposit", "amount": 250.00},
        ],
    },
    "trv_3307": {
        "name": "Travel Fund",
        "balance": 875.50,
        "recent_transactions": [
            {"date": "2026-10-10", "description": "Hotel reservation", "amount": -124.50},
            {"date": "2026-10-05", "description": "Travel deposit", "amount": 300.00},
            {"date": "2026-10-02", "description": "Train tickets", "amount": -45.00},
        ],
    },
}


TOOL_DEFINITIONS = [
    {
        "name": "list_accounts",
        "description": "List bank account IDs and names. Use this to select an account before checking its balance or recent transactions.",
        "inputSchema": {
            "type": "object", 
            "additionalProperties": False
        },
    },
    {
        "name": "check_bank_balance",
        "description": "Return the current balance of a bank account in USD.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "account_id": {
                    "type": "string", 
                    "description": "An account ID returned by list_accounts."
                },
            },
            "required": ["account_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "get_recent_transactions",
        "description": "Return a bank account's recent transactions, newest first. Amounts are in USD; credits are positive and debits negative.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "account_id": {
                    "type": "string", 
                    "description": "An account ID returned by list_accounts."
                },
                "limit": {
                    "type": "integer", 
                    "minimum": 1, 
                    "description": "Number of transactions to request; defaults to 5."
                },
            },
            "required": ["account_id"],
            "additionalProperties": False,
        },
    },
]


def list_accounts() -> dict:
    return {
        "accounts": [
            {"account_id": account_id, "name": account["name"]}
            for account_id, account in BANK_DATABASE.items()
        ]
    }


def check_bank_balance(account_id: str) -> dict:
    if not isinstance(account_id, str) or account_id not in BANK_DATABASE:
        raise ValueError("Unknown account_id. Call list_accounts to find a valid account ID.")
    account = BANK_DATABASE[account_id]
    return {
        "account_id": account_id, 
        "name": account["name"], 
        "balance": account["balance"], 
        "currency": "USD"
    }


def get_recent_transactions(account_id: str, limit: int = 5) -> dict:
    if not isinstance(account_id, str) or account_id not in BANK_DATABASE:
        raise ValueError("Unknown account_id. Call list_accounts to find a valid account ID.")
    if type(limit) is not int or limit < 1:
        raise ValueError("limit must be a positive integer")
    if limit > 5:
        raise ValueError(
            f"Requested limit={limit}, but at most 5 transactions are allowed per call. "
            "Retry get_recent_transactions with the same account_id and limit=5."
        )
    return {
        "account_id": account_id,
        "currency": "USD",
        "transactions": BANK_DATABASE[account_id]["recent_transactions"][:limit],
    }


'''
Native tools exposed by bundled Codex 0.162.1 with gpt-6-luna (code mode).
Availability varies by model, configuration, and enabled features.

Directly exposed tools:
- functions.exec: Run JavaScript that calls native tools and displays results.
- functions.wait: Wait for a running functions.exec cell to produce output.
- functions.request_user_input: Ask structured questions and wait for answers
  when the current collaboration mode permits it.
- functions.request_user_input_async: Ask questions while continuing work.
- clock.sleep: Pause until a timeout or new user input arrives.
- collaboration.spawn_agent: Start a sub-agent with an assigned task.
- collaboration.send_message: Send a message to an existing sub-agent.
- collaboration.followup_task: Assign follow-up work to an existing sub-agent.
- collaboration.interrupt_agent: Interrupt a sub-agent's current work.
- collaboration.list_agents: Inspect the agents in the current team.
- collaboration.wait_agent: Wait for an agent update or new user input.

Native operations called inside functions.exec through the tools object:
- exec_command: Execute shell commands and return output or a running session.
- write_stdin: Send input to, or collect output from, a running shell session.
- apply_patch: Create, edit, move, or delete files using patch instructions.
- view_image: Inspect an image stored on the local filesystem.
- create_goal: Create a persistent work goal when explicitly requested.
- get_goal: Read the current goal's status and budget usage.
- update_goal: Update the current goal's completion, pause, or blocked status.
- list_mcp_resources: Discover resources exposed by connected MCP servers.
- list_mcp_resource_templates: Discover parameterized MCP resource templates.
- read_mcp_resource: Read a resource from a connected MCP server.
- clock__curr_time: Read the current UTC time.

'''

