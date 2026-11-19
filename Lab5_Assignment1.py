
"""
Lab 5: MCP-Style Connector - Mini Integration Server

Assignment 1: Add a Fourth, Discoverable Capability

Features:
1. File reading resource
2. SQLite database query tool
3. Mock API tool
4. Capability discovery
5. Permission-controlled database access
6. Fourth capability: list_files
"""

import sqlite3


# --------------------------------------------------
# STEP 1: Set up an in-memory SQLite database
# --------------------------------------------------

conn = sqlite3.connect(":memory:")

conn.execute(
    "CREATE TABLE signups (event TEXT, count INTEGER)"
)

conn.executemany(
    "INSERT INTO signups VALUES (?, ?)",
    [
        ("AI Club Talk", 12),
        ("Hackathon Kickoff", 9),
        ("Robotics Demo", 15),
    ],
)

conn.commit()


# --------------------------------------------------
# STEP 2: Define mock resources
# --------------------------------------------------

MOCK_FILES = {
    "README.md": "Agentic AI Systems - mini MCP server demo.",
    "notes.txt": "Project meeting notes and decisions.",
    "report.txt": "Campus event signup report."
}

MOCK_API = {
    "events_today": ["AI Club Talk", "Robotics Demo"]
}


# --------------------------------------------------
# STEP 3: Define capability manifest
# --------------------------------------------------

CAPABILITIES = [
    {
        "name": "read_file",
        "kind": "resource",
        "input": {"path": "str"},
        "output": {"content": "str"}
    },
    {
        "name": "query_db",
        "kind": "tool",
        "input": {"sql": "str"},
        "output": {"rows": "list"}
    },
    {
        "name": "call_api",
        "kind": "tool",
        "input": {"endpoint": "str"},
        "output": {"data": "any"}
    },

    # NEW FOURTH CAPABILITY
    {
        "name": "list_files",
        "kind": "resource",
        "input": {},
        "output": {"files": "list"}
    }
]


# Only registered planning agents can query the database
ALLOWED_CALLERS = {"planning_agent"}


# --------------------------------------------------
# STEP 4: Implement MCP Server
# --------------------------------------------------

class MCPServer:

    def list_capabilities(self):
        return CAPABILITIES

    def read_file(self, path):

        if path not in MOCK_FILES:
            return {"error": f"file not found: {path}"}

        return {"content": MOCK_FILES[path]}

    def query_db(self, sql, caller):

        if caller not in ALLOWED_CALLERS:
            return {
                "error": f"caller '{caller}' is not permitted to use query_db"
            }

        if not sql.strip().upper().startswith("SELECT"):
            return {
                "error": "only SELECT statements are permitted through this tool"
            }

        cur = conn.execute(sql)

        return {"rows": cur.fetchall()}

    def call_api(self, endpoint):

        if endpoint not in MOCK_API:
            return {"error": f"unknown endpoint: {endpoint}"}

        return {"data": MOCK_API[endpoint]}

    # NEW METHOD: List available files
    def list_files(self):

        return {
            "files": list(MOCK_FILES.keys())
        }


# --------------------------------------------------
# STEP 5: Implement MCP Client
# --------------------------------------------------

class MCPClient:

    def __init__(self, server, caller_name):
        self.server = server
        self.caller_name = caller_name

    def discover(self):
        return self.server.list_capabilities()

    def call(self, capability_name, **kwargs):

        # Discover capabilities dynamically
        manifest = {
            c["name"]: c for c in self.discover()
        }

        if capability_name not in manifest:
            raise ValueError(
                f"unknown capability: {capability_name}"
            )

        # Dynamically locate the server method
        method = getattr(self.server, capability_name)

        if capability_name == "query_db":
            return method(
                caller=self.caller_name,
                **kwargs
            )

        return method(**kwargs)


# --------------------------------------------------
# STEP 6: Demonstrate capability discovery and calls
# --------------------------------------------------

if __name__ == "__main__":

    server = MCPServer()

    client = MCPClient(
        server,
        caller_name="planning_agent"
    )

    # Display all available capabilities
    print("=== Capability Discovery ===")

    for capability in client.discover():

        print(
            f"  {capability['name']} "
            f"({capability['kind']}) "
            f"input={capability['input']} "
            f"output={capability['output']}"
        )

    # Original capability 1: Read file
    print("\n=== Call 1: read_file (resource) ===")

    print(
        client.call(
            "read_file",
            path="README.md"
        )
    )

    # Original capability 2: Query database
    print("\n=== Call 2: query_db (tool) ===")

    print(
        client.call(
            "query_db",
            sql="SELECT event, count FROM signups"
        )
    )

    # Original capability 3: Call API
    print("\n=== Call 3: call_api (tool) ===")

    print(
        client.call(
            "call_api",
            endpoint="events_today"
        )
    )

    # NEW capability 4: List files
    print("\n=== Call 4: list_files (new resource) ===")

    print(
        client.call("list_files")
    )

    # Test rejection of disallowed SQL statement
    print("\n=== Rejection Path: Disallowed Statement ===")

    print(
        client.call(
            "query_db",
            sql="DELETE FROM signups"
        )
    )

    # Test rejection of unauthorized caller
    print("\n=== Rejection Path: Disallowed Caller ===")

    other_client = MCPClient(
        server,
        caller_name="unregistered_agent"
    )

    print(
        other_client.call(
            "query_db",
            sql="SELECT * FROM signups"
        )
    )

    # Verify that the new capability was discovered and called
    print("\n=== New Capability Verification ===")

    discovered_names = [
        capability["name"]
        for capability in client.discover()
    ]

    assert "list_files" in discovered_names

    file_result = client.call("list_files")

    assert "README.md" in file_result["files"]
    assert "notes.txt" in file_result["files"]
    assert "report.txt" in file_result["files"]

    print("list_files discovered successfully: PASS")
    print("list_files called successfully: PASS")
    print("File listing returned correctly: PASS")
