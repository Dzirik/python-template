"""
Functions for supporting notebook functionality.

Updated for Notebook 7 (JupyterLab-based) compatibility.
Uses jupyter_server.serverapp instead of notebook.notebookapp.
"""

from json import loads
from logging import getLogger
from re import search

from ipykernel.connect import get_connection_file
from jupyter_server.serverapp import list_running_servers
from requests import get


def get_notebook_name() -> str:
    """
    Return the full path of the jupyter notebook.

    :return: str. Notebok name.
    """
    kernel_id = search("kernel-(.*).json", get_connection_file()).group(1)  # type: ignore[union-attr]
    servers = list_running_servers()
    for server in servers:
        response = get(f"{server['url']}api/sessions", params={"token": server.get("token", "")}, timeout=5)
        for load in loads(response.text):
            try:
                if load["kernel"]["id"] == kernel_id:
                    relative_path = load["notebook"]["path"]
                    return str(relative_path.split("/")[-1])
            except Exception:
                getLogger().exception("Failed to get notebook name")
    return "NAME"
