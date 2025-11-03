import os
import json
import yaml
from typing import Any, List, Dict
from mcp.server.fastmcp import FastMCP
from pathlib import Path

def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file.
    
    Returns default configuration if file doesn't exist or has errors.
    """
    default_config = {
        "log_paths": [
            "logs",
            ".",
            r"C:\Logs",
            r"C:\Windows\System32\LogFiles",
            "/var/log"
        ],
        "max_file_size": 200_000
    }
    
    if not os.path.exists(config_path):
        return default_config
        
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            # Validate and ensure all required fields exist
            if not isinstance(config, dict):
                return default_config
            if "log_paths" not in config or not isinstance(config["log_paths"], list):
                config["log_paths"] = default_config["log_paths"]
            if "max_file_size" not in config or not isinstance(config["max_file_size"], int):
                config["max_file_size"] = default_config["max_file_size"]
            return config
    except Exception:
        return default_config

# Initialize FastMCP server
mcp = FastMCP("logreader")
CONFIG = load_config()

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

    # Get configured paths and resolve relative paths
    paths = CONFIG["log_paths"]
    resolved_paths = []
    for path in paths:
        if os.path.isabs(path):
            resolved_paths.append(path)
        else:
            resolved_paths.append(os.path.join(os.getcwd(), path))

    found: List[Dict[str, Any]] = []

    # If none of the configured paths exist, use cwd as a fallback
    paths_to_search = [p for p in resolved_paths if os.path.exists(p)]
    if not paths_to_search:
        paths_to_search = [os.getcwd()]

    # Get configured maximum file size
    MAX_BYTES = CONFIG["max_file_size"]

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
