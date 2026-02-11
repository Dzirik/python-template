"""
Functions for supporting notebook functionality.
"""

from json import loads
from logging import getLogger
from re import search

from ipykernel.connect import get_connection_file
from IPython.display import HTML
from notebook.notebookapp import list_running_servers
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
            except Exception:  # pylint: disable=broad-except
                getLogger().exception("Failed to get notebook name")
    return "NAME"


def create_button() -> HTML:
    """
    Creates a button which hides the code.

    :return: HTML. The button.
    """
    return HTML("""<script>
    code_show=true;
    function code_toggle() {
    if (code_show){
    $('div.input').hide();
    } else {
    $('div.input').show();

    }
    code_show = !code_show
    }
    $( document ).ready(code_toggle);
    </script>
    <form action="javascript:code_toggle()"><input type="submit" value="Show/Hide code"></form>""")  # type: ignore[no-untyped-call]
