# Jupyter Ecosystem Upgrade Documentation

**Created:** February 12, 2026
**Version:** 2.0.0 (Notebook 7 Migration)
**Status:** Changelog / Reference Document

## Overview

This document describes the migration from the legacy Jupyter Notebook 6.x ecosystem to the modern Notebook 7.x architecture, which is built on JupyterLab components.

---

## Changelog: Library Version Upgrades

### Core Jupyter Components

| Package | Previous Version | New Version | Notes |
|---------|-----------------|-------------|-------|
| `notebook` | 6.5.7 | ≥7.5.2 | **Major upgrade** - JupyterLab-based |
| `jupyter_server` | ≥1.24.0,<2.0.0 | ≥2.14.0 | Required for Notebook 7 |
| `jupyterlab` | (not required) | ≥4.5.2 | Required for anchor navigation fix (PR #18208) |
| `nbclassic` | ≥1.0.0 | **Removed** | No longer needed |

### Jupytext & Notebook Execution

| Package | Previous Version | New Version | Notes |
|---------|-----------------|-------------|-------|
| `jupytext` | ≥1.14.0 | ≥1.19.0 | Full Notebook 7/JupyterLab 4 support |
| `papermill` | ≥2.4.0 | ≥2.6.0 | Latest stable |
| `ipykernel` | 6.29.5 (pinned) | ≥7.0.0 | **Major upgrade** - Python 3.10+ |

### Supporting Libraries

| Package | Previous Version | New Version |
|---------|-----------------|-------------|
| `jupyter-client` | ≥7.0.0 | ≥8.0.0 |
| `jupyter-core` | ≥5.0.0 | ≥5.7.0 |
| `nbclient` | ≥0.7.0 | ≥0.10.0 |
| `nbconvert` | ≥7.0.0 | ≥7.16.0 |
| `nbformat` | ≥5.7.0 | ≥5.10.0 |
| `ipython` | ≥8.12.0 | ≥8.20.0 |
| `ipywidgets` | ≥8.0.0 | ≥8.1.0 |
| `traitlets` | ≥5.9.0 | ≥5.14.0 |
| `pyzmq` | ≥25.0.0 | ≥26.0.0 |
| `mistune` | ≥2.0.0 | ≥3.0.0 |
| `tornado` | ≥6.2 | ≥6.4 |
| `debugpy` | ≥1.6.6 | ≥1.8.0 |

---

## Code Changes

### 1. Makefile Update

The `make jupyter` command now uses Notebook 7 directly instead of nbclassic:

```makefile
# Before (Notebook 6.x with nbclassic shim)
@uv run --no-project python -m nbclassic

# After (Notebook 7)
@uv run --no-project python -m notebook
```

### 2. notebook_support_functions.py Update

The `list_running_servers` import changed from `notebook.notebookapp` to `jupyter_server.serverapp`:

```python
# Before (Notebook 6.x)
from notebook.notebookapp import list_running_servers

# After (Notebook 7)
from jupyter_server.serverapp import list_running_servers
```

---

## New Features in Notebook 7

### JupyterLab-Based Interface
- **Modern UI**: Notebook 7 uses JupyterLab's frontend components
- **Improved performance**: Faster rendering and better memory management
- **Dark mode**: Built-in theme support (light/dark)
- **Real-time collaboration**: Optional collaborative editing (requires jupyter-collaboration)

### Enhanced Debugging
- **Visual debugger**: Built-in debugger with breakpoints, variable inspection
- **Step-through execution**: Debug cells line by line

### Better Extension Support
- **JupyterLab extensions**: Compatible with JupyterLab 4.x extensions
- **Prebuilt extensions**: Faster installation, no build step required

---

## New Features in Jupytext 1.19.x

### Enhanced Format Support
- **MyST Markdown frontmatter mapping**: Better integration with Jupyter Book
- **py:marimo format**: Support for Marimo notebook format
- **Pairing groups**: Organize paired notebooks in groups

### Improved Contents Manager
- **Async contents manager**: Better performance for large notebooks
- **Improved synchronization**: More reliable .ipynb ↔ .py sync

### JupyterLab 4 Integration
- **Native JupyterLab extension**: Prebuilt extension for JupyterLab 4
- **Command palette integration**: Pair notebooks directly from JupyterLab

---

## Preserved Features

The following critical features remain fully functional:

### ✅ Automatic .ipynb ↔ .py Synchronization
- Jupytext `py:light` format continues to work
- Paired notebooks sync automatically on save
- `jupytext.read()` and `jupytext.write()` APIs unchanged

### ⚠️ Hyperlinks in Notebooks (Known Limitations)

**Current Status:** In-notebook anchor links (Table of Contents links) have known issues in Notebook 7/JupyterLab 4.

#### What Works:
- ✅ **HTML export** - Anchor links work correctly in exported HTML files
- ✅ **Built-in Table of Contents panel** - Use **View → Table of Contents** or the ToC icon in the left sidebar
- ✅ **Ctrl+Click** - Opens link in new window and navigates correctly

#### What Doesn't Work:
- ❌ **Regular click on anchor links** - Does not scroll to target section in Notebook 7

#### Technical Background:
- JupyterLab's HTML sanitizer replaces `id` attributes with `data-jupyter-id` for XSS protection
- The navigation code was looking for `id` attributes, causing links to fail
- A fix was merged in JupyterLab 4.5.2 (PR [#18208](https://github.com/jupyterlab/jupyterlab/pull/18208))
- However, the fix may not work in all environments

#### Recommended Workaround:
**Use the built-in Table of Contents panel** for navigation:
1. Click **View → Table of Contents** in the menu, OR
2. Click the ToC icon (list icon) in the left sidebar
3. Click on any heading to navigate directly

#### Link Format (for HTML export):
- Use heading-based anchors: `[Link Text](#heading-text-lowercase-with-hyphens)`
- Example: `# General Settings` → link with `(#general-settings)`
- **Note:** The old `<a name="anchor">` syntax does NOT work - these tags are stripped by HTML sanitization

### ✅ Automatic Notebook Execution Scripts
- `notebooks_executioner.py` fully compatible
- Papermill parameterized execution unchanged
- HTML conversion via nbconvert works as before

---

## Migration Notes

### Breaking Changes
1. **nbclassic removed**: If you have scripts referencing `nbclassic`, update them to use `notebook`
2. **Import path change**: `notebook.notebookapp` → `jupyter_server.serverapp`
3. **Python version**: ipykernel 7.x requires Python ≥3.10

### Recommendations
1. **Clear virtual environment**: Run `uv sync` to reinstall all dependencies
2. **Test notebook execution**: Run `make jupyter` to verify the new interface
3. **Test parameterized execution**: Verify papermill workflows still function

---

## Configuration Files Added

### jupytext.toml
A `jupytext.toml` configuration file has been added to the repository root to enable global pairing:

```toml
# Pair all notebooks in the repository to py:light format
formats = "ipynb,py:light"
```

### jupyter_server_config.py
A jupyter server configuration file has been added to `.venv/etc/jupyter/jupyter_server_config.py` to enable the jupytext contents manager:

```python
# Use jupytext's TextFileContentsManager to handle .py files as notebooks
c.ServerApp.contents_manager_class = "jupytext.TextFileContentsManager"
```

This configuration allows `.py` files with jupytext headers to be opened directly as notebooks in Notebook 7.

---

## Troubleshooting

### Opening .py Files as Notebooks

In Notebook 7, `.py` files with jupytext headers can be opened as notebooks. Here are the methods:

#### Method 1: Right-Click Context Menu (Recommended)
1. In the Jupyter file browser, **right-click** on the `.py` file
2. Select **"Open With"** → **"Notebook"**

This is the most reliable method and works regardless of configuration.

#### Method 2: Contents Manager Configuration
If you want `.py` files to open as notebooks by default (double-click):

1. **Verify the contents manager is configured:**
   ```bash
   # Check that jupyter_server_config.py exists
   cat .venv/etc/jupyter/jupyter_server_config.py
   # Should contain: c.ServerApp.contents_manager_class = "jupytext.TextFileContentsManager"
   ```

2. **If missing, create it:**
   ```bash
   mkdir -p .venv/etc/jupyter
   echo 'c.ServerApp.contents_manager_class = "jupytext.TextFileContentsManager"' > .venv/etc/jupyter/jupyter_server_config.py
   ```

3. **Restart Jupyter** after creating the config

**Note:** This configuration may not work reliably in all environments. Use Method 1 (right-click) if double-click doesn't work.

#### Method 3: Command Palette
1. Press `Ctrl+Shift+C` to open Command Palette
2. Search for "Jupytext" commands

### Kernel Connection Issues
If kernels fail to connect after upgrade:
```bash
# Reinstall ipykernel
uv run python -m ipykernel install --user --name python3
```

### Extension Compatibility
Notebook 7 uses JupyterLab 4 extensions. Classic notebook extensions (for Notebook 6.x) are not compatible. Check for JupyterLab 4 versions of any extensions you use.

### Jupytext Pairing Issues
If paired notebooks don't sync:
```bash
# Force sync from .py to .ipynb
uv run jupytext --sync notebook.py
```

### Re-creating the Contents Manager Configuration
If the `.venv` is recreated, you need to re-add the jupyter_server_config.py:
```bash
# Create the config directory if it doesn't exist
mkdir -p .venv/etc/jupyter

# Add the contents manager configuration
echo 'c.ServerApp.contents_manager_class = "jupytext.TextFileContentsManager"' > .venv/etc/jupyter/jupyter_server_config.py
```

### Anchor Links Not Working in template version 2.0 (Table of Contents Links)

This is a **known limitation** in Notebook 7/JupyterLab 4. See the "Hyperlinks in Notebooks" section above for details.

**Quick Solution:** Use the **built-in Table of Contents panel**:
- Click **View → Table of Contents** in the menu, OR
- Click the ToC icon (list icon) in the left sidebar

**Note:** Anchor links work correctly in HTML exports.

### SQLite History Errors
If you see "Failed to open SQLite history" errors in the console:

1. **Delete the corrupted history file:**
   - Windows: `del %USERPROFILE%\.ipython\profile_default\history.sqlite`
   - Linux/Mac: `rm ~/.ipython/profile_default/history.sqlite`

2. **Or disable history permanently** by creating `~/.ipython/profile_default/ipython_config.py`:
   ```python
   c.HistoryManager.enabled = False
   ```

