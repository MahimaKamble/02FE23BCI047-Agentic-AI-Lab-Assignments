
"""
Lab 5: MCP-Style Connector - Mini Integration Server

Assignment 2: Scope read_file to a Safe Directory

Features:
1. File reading resource
2. SQLite database query tool
3. Mock API tool
4. Capability discovery
5. Permission-controlled database access
6. Safe directory restriction for file reading
7. Adversarial path traversal test
"""

import sqlite3
import posixpath


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
# STEP 2: Define safe directory and mock files
# --------------------------------------------------

SAFE_DIRECTORY = "/safe/"

MOCK_FILES = {
    "/safe/README.md": "Agentic AI Systems - mini MCP server demo.",
    "/safe/notes.txt": "Project meeting notes and decisions.",
    "/safe/report.txt": "Campus event signup report.",

    # This file is outside the safe directory.
    "/private/secret.txt": "Confidential information."
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
    }
]

ALLOWED_CALLERS = {"planning_agent"}


# --------------------------------------------------
# STEP 4: Implement MCP Server
# --------------------------------------------------

class MCPServer:

    def list_capabilities(self):
        return CAPABILITIES

    # Read files only from the declared safe directory
    def read_file(self, path):

        # Normalize the requested path to prevent traversal
        normalized_path = posixpath.normpath(path)

        # Reject paths outside the safe directory
        if not normalized_path.startswith(SAFE_DIRECTORY):
            return {
                "error": "access denied: file path is outside the safe directory"
            }

        # Check whether the file exists
        if normalized_path not in MOCK_FILES:
            return {
                "error": f"file not found: {normalized_path}"
            }

        return {
            "content": MOCK_FILES[normalized_path]
        }

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

        return {
            "rows": cur.fetchall()
        }

    def call_api(self, endpoint):

        if endpoint not in MOCK_API:
            return {
                "error": f"unknown endpoint: {endpoint}"
            }

        return {
            "data": MOCK_API[endpoint]
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

        manifest = {
            c["name"]: c for c in self.discover()
        }

        if capability_name not in manifest:
            raise ValueError(
                f"unknown capability: {capability_name}"
            )

        method = getattr(self.server, capability_name)

        if capability_name == "query_db":
            return method(
                caller=self.caller_name,
                **kwargs
            )

        return method(**kwargs)


# --------------------------------------------------
# STEP 6: Demonstrate normal and adversarial requests
# --------------------------------------------------

if __name__ == "__main__":

    server = MCPServer()

    client = MCPClient(
        server,
        caller_name="planning_agent"
    )

    # Display available capabilities
    print("=== Capability Discovery ===")

    for capability in client.discover():
        print(
            f"  {capability['name']} "
            f"({capability['kind']})"
        )

    # Test a valid file inside the safe directory
    print("\n=== Valid Read: Safe Directory ===")

    safe_result = client.call(
        "read_file",
        path="/safe/README.md"
    )

    print(safe_result)

    # Test an ordinary path outside the safe directory
    print("\n=== Adversarial Test 1: Outside Safe Directory ===")

    outside_result = client.call(
        "read_file",
        path="/private/secret.txt"
    )

    print(outside_result)

    # Test a path traversal attempt
    print("\n=== Adversarial Test 2: Path Traversal ===")

    traversal_result = client.call(
        "read_file",
        path="/safe/../private/secret.txt"
    )

    print(traversal_result)

    # Test database access remains functional
    print("\n=== Database Query ===")

    print(
        client.call(
            "query_db",
            sql="SELECT event, count FROM signups"
        )
    )

    # Verify safe directory protection
    print("\n=== Security Verification ===")

    assert "content" in safe_result
    assert "error" in outside_result
    assert "error" in traversal_result

    print("Safe file read permitted: PASS")
    print("Outside directory access blocked: PASS")
    print("Path traversal attempt blocked: PASS")

    # Verify unauthorized database access is still blocked
    print("\n=== Database Permission Verification ===")

    other_client = MCPClient(
        server,
        caller_name="unregistered_agent"
    )

    unauthorized_result = other_client.call(
        "query_db",
        sql="SELECT * FROM signups"
    )

    print(unauthorized_result)

    assert "error" in unauthorized_result

    print("Unauthorized database access blocked: PASS")
