import os
import json
from typing import Any, List, Dict
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("logreader")

@mcp.tool()
async def get_logfiles(filename_search_string: str = "") -> str:
    """Get logfiles from the local system.

    Args:
        filename_search_string: the filename search string to look for in logfiles (optional)
    """
    # Assumptions made:
    # - There are a few pre-configured paths to search for log files. If none exist
    #   we will search the current working directory recursively.
    # - Returned value should be a JSON-serializable string describing found files
    #   and their contents (this is mcp-friendly).
    # - If no search string is provided, all log files will be returned

    # Pre-configured search paths (common locations for logs on Windows/Linux
    # plus a ./logs folder and the current working directory).
    default_paths: List[str] = [
        os.path.join(os.getcwd(), "logs"),
        os.getcwd(),
        r"C:\Logs",
        r"C:\Windows\System32\LogFiles",
        "/var/log",
    ]

    found: List[Dict[str, Any]] = []

    # If none of the default paths exist, we'll still search cwd as a fallback
    paths_to_search = [p for p in default_paths if os.path.exists(p)]
    if not paths_to_search:
        paths_to_search = [os.getcwd()]

    # Limit per-file read size to avoid returning huge payloads (bytes)
    MAX_BYTES = 200_000

    for base in paths_to_search:
        if os.path.isfile(base):
            # If a file path was given directly, check it
            fname = os.path.basename(base)
            if not filename_search_string or filename_search_string in fname:
                try:
                    with open(base, "r", encoding="utf-8", errors="replace") as fh:
                        data = fh.read(MAX_BYTES)
                    truncated = os.path.getsize(base) > MAX_BYTES
                    found.append({"path": base, "content": data, "truncated": truncated})
                except Exception as e:
                    found.append({"path": base, "error": str(e)})
            continue

        for dirpath, _dirs, files in os.walk(base):
            for fn in files:
                    # Include file if no search string or if search string matches filename
                if not filename_search_string or filename_search_string in fn:
                    full = os.path.join(dirpath, fn)
                    try:
                        # Try text read with utf-8, replace errors
                        with open(full, "r", encoding="utf-8", errors="replace") as fh:
                            data = fh.read(MAX_BYTES)
                        truncated = os.path.getsize(full) > MAX_BYTES
                        found.append({"path": full, "content": data, "truncated": truncated})
                    except Exception as e:
                        # Report error for this file but continue
                        found.append({"path": full, "error": str(e)})

    return json.dumps({"files": found}, ensure_ascii=False)

def main():
    print("Starting up logreader-mcp server now!")
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
