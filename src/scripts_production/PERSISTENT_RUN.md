# Running the Watchdog Persistently with Windows Task Scheduler

This guide explains how to make `watchdog.py` start automatically when you log in to
Windows and restart itself automatically if it ever crashes — with no developer tools
required after the initial setup.

> **Technical audit:** For a detailed production-readiness assessment of the supervision
> system, see [`docs/AUDIT.md`](../../docs/AUDIT.md).

---

## Table of Contents

1. [Overview](#1-overview)
2. [Prerequisites](#2-prerequisites)
3. [The Action Tab — Exact Values](#3-the-action-tab--exact-values)
4. [Step-by-Step Task Scheduler Setup](#4-step-by-step-task-scheduler-setup)
5. [Verifying the Setup](#5-verifying-the-setup)
6. [Troubleshooting](#6-troubleshooting)
7. [Supervision & Recovery Architecture](#7-supervision--recovery-architecture)
8. [Logging Architecture](#8-logging-architecture)
9. [Operational Parameters](#9-operational-parameters)

---

## 1. Overview

The system uses a **three-layer supervision hierarchy**:

```
Windows Task Scheduler  (every 30 s)
  └── checker.py --config-name watchdog_cmd_01    ← ephemeral; checks watchdog health
        └── watchdog.py --config-name watchdog_cmd_01  ← long-running daemon
              ├── cmd_status_print_01.py (cmd_01-01)   ← worker process
              ├── cmd_status_print_01.py (cmd_01-02)   ← worker process
              └── cmd_status_print_02.py (cmd_02-01)   ← worker process
```

- **Windows Task Scheduler** invokes `checker.py` every 30 seconds. The checker is an
  ephemeral process — it runs, evaluates the watchdog's health, and exits. This "outer
  sentinel" design avoids the "who watches the watchman" problem because there is no
  long-running monitor to crash.
- **`checker.py`** reads the watchdog's `.pid` and `.hb` files. It verifies that the PID
  is alive **and** that the process command line matches the expected `watchdog.py`
  instance (via WMIC), guarding against PID recycling on Windows. If the watchdog is
  unhealthy, `checker.py` performs a [4-step recovery](#71-recovery-logic-checkerpy).
- **`watchdog.py`** is the long-running daemon that manages workers. It polls every
  `CHECK_INTERVAL` (30 s) for crashed or frozen workers and restarts them using a
  [graceful shutdown](#72-graceful-worker-shutdown-watchdogpy) pattern.
- **`--config-name`** is a mandatory argument that selects the HOCON configuration file
  (e.g. `watchdog_cmd_01.conf`) defining which workers to manage, their scripts,
  arguments, and heartbeat timeouts. Both `checker.py` and `watchdog.py` require it.
- **Heartbeat and PID files** — each watchdog instance writes its files to an isolated
  `heartbeats_<config_name>/` folder (e.g. `heartbeats_watchdog_cmd_01/`) located
  alongside `watchdog.py`. This allows multiple watchdog configurations to run side by
  side without interfering.
- **Worker subprocesses** receive a mandatory `--heartbeat-folder` argument pointing to
  the same directory, which they pass to `write_pid()` to store their own PID files in
  the correct location.
- **Path resolution** — both `checker.py` and `watchdog.py` use
  `Path(__file__).resolve().parent` to compute all paths relative to their own location
  on disk. This means scripts can be invoked from **any working directory** (including
  Windows Task Scheduler's default `C:\WINDOWS\system32`) without path errors. The
  **Start in** field in Task Scheduler is no longer functionally required but is retained
  as a best-practice convention.

---

## 2. Prerequisites

Before starting, confirm the following:

- **The project is set up.** The virtual environment exists at `.venv` inside the
  project folder (e.g. `D:\TEMP\test\.venv`). If you are unsure, open the project
  folder in File Explorer and check that a `.venv` folder is present.
- **You know the full project path.** You will need to type it during setup. Example:
  `D:\TEMP\test`. Find it by opening File Explorer, navigating to the project folder,
  and clicking the address bar at the top — it will show the full path.
- **You are logged in as an administrator**, or can provide administrator credentials
  when prompted. Task Scheduler requires elevated permissions to create tasks.

---

## 3. The Action Tab — Exact Values

This is the most important part of the configuration. Task Scheduler needs to know
exactly which Python to use and where the script is. Using the wrong Python (e.g. a
system-wide installation) will cause the task to fail because the required libraries
(`winotify` and others) are only installed inside the project's virtual environment.

Replace `D:\TEMP\test` with your actual project path in all three fields below.

| Field | Value |
|---|---|
| **Program / script** | `D:\TEMP\test\.venv\Scripts\python.exe` |
| **Add arguments** | `-u D:\TEMP\test\src\scripts\watchdog.py --config-name watchdog_cmd_01` |
| **Start in** | `D:\TEMP\test\src\scripts` |

**Why each value:**

- **Program / script** — Points to `python.exe` inside `.venv\Scripts\`. This is the
  virtual environment's Python, which has all project dependencies installed.
- **Add arguments** — The `-u` flag disables output buffering so log messages appear
  immediately. The full path to `watchdog.py` follows. `--config-name` is mandatory and
  selects which `.conf` configuration file to load (e.g. `watchdog_cmd_01` loads
  `configurations/watchdog_cmd_01.conf`). The script exits immediately with an error if
  this argument is omitted or blank.
- **Start in** — Sets the working directory to the scripts folder. Both `checker.py`
  and `watchdog.py` now use `Path(__file__).resolve().parent` to resolve all paths
  relative to the script's own location, so the **Start in** field is no longer strictly
  required for correct operation. It is retained as a best-practice default.

> ⚠️ **Do not use `python` or `python.exe` alone in the Program/script field.** This
> would use the system Python, which does not have `winotify` installed, and the task
> will fail with `ModuleNotFoundError`.

---

## 4. Step-by-Step Task Scheduler Setup

### Open Task Scheduler

1. Press **Win + S** to open the search bar.
2. Type `Task Scheduler` and press **Enter**.
3. If Windows asks for administrator permission, click **Yes**.

### Create a new task

4. In the right-hand **Actions** panel, click **Create Task…**
   > ⚠️ Choose **Create Task…**, not "Create Basic Task…". The basic wizard does not
   > expose all the settings needed.

A dialog box with several tabs will open. Work through each tab below.


### General tab

5. **Name:** Enter a descriptive name, e.g. `Watchdog – Windows Notifications`.
6. **Description** *(optional)*: e.g. `Starts and supervises the notification watchdog process.`
7. **Security options:**
   - Select **Run only when user is logged on**.

   > ⚠️ **Do not select "Run whether user is logged in or not".** That option runs the
   > process in Windows Session 0 — an invisible background session that is isolated
   > from your desktop. Windows toast notifications are delivered to your desktop
   > session and will be completely invisible when the task runs in Session 0. Always
   > use "Run only when user is logged on" for any task that needs to show
   > notifications.

8. Tick **Run with highest privileges**.

### Triggers tab

9. Click **New…** to add a trigger.
10. In the **Begin the task** dropdown, select **At log on**.
11. Under **Settings**, select **Specific user** and confirm your Windows username is
    shown. This ensures the watchdog starts in your own desktop session.
12. Leave **Delay task for** unchecked.
13. Ensure **Enabled** is ticked at the bottom of the dialog.
14. Click **OK**.

### Actions tab

15. Click **New…** to add an action.
16. **Action:** Leave as `Start a program`.
17. Fill in the three fields with the values from [Section 3](#3-the-action-tab--exact-values):
    - **Program / script:** `D:\TEMP\test\.venv\Scripts\python.exe`
    - **Add arguments:** `-u D:\TEMP\test\src\scripts\watchdog.py --config-name watchdog_cmd_01`
    - **Start in:** `D:\TEMP\test\src\scripts`
18. Click **OK**.

### Conditions tab

19. Under **Power**, untick **Start the task only if the computer is on AC power**.

    > This setting is ticked by default on laptops. If left on, the watchdog will stop
    > running when you unplug from mains power and will not restart until you plug back
    > in. Untick it so the watchdog runs regardless of power source.

### Settings tab

20. Tick **If the task fails, restart every:** and set the value to **1 minute**.
21. Set **Attempt to restart up to:** to **999 times**.
22. **Untick "Stop the task if it runs longer than"** and clear any value in that field.

    > ⚠️ This setting is **enabled by default** with a limit of 3 days. If left on,
    > Task Scheduler will silently kill the watchdog after exactly 3 days of continuous
    > running. Because the watchdog is designed to run indefinitely, this limit must be
    > removed.

23. In the **If the task is already running, then the following rule applies** dropdown,
    select **Do not start a new instance**.
24. Click **OK** to save the task.
25. If prompted, enter your Windows password and click **OK**.

---

## 5. Verifying the Setup

### Check the task appears in the list

After clicking OK, the Task Scheduler library (the main panel) should now show your
new task. If you do not see it, click **Task Scheduler Library** in the left-hand tree
to refresh the view.

### Run the task manually to test it

26. Right-click the task in the list and choose **Run**.
27. The **Last Run Result** column should update to `0x0` within a few seconds.
    - `0x0` means the task started successfully.
    - Any other value (e.g. `0x1`, `0x41301`) indicates an error — see
      [Section 6](#6-troubleshooting).

### Confirm the Python process is running

28. Press **Ctrl + Shift + Esc** to open Task Manager.
29. Click the **Details** tab.
30. Look for `python.exe` in the list. If the watchdog is running, you should see at
    least one `python.exe` entry per configured worker, plus one for the watchdog
    itself.

    > **Tip:** Right-click a `python.exe` entry and choose **Open file location** to
    > confirm it points to `.venv\Scripts\python.exe` and not a system Python
    > installation.

### Test restart behaviour

31. In Task Manager → Details tab, select the `python.exe` process that is the watchdog
    (the parent process) and click **End task**.
32. Wait about 60 seconds, then check Task Manager again. Task Scheduler should have
    restarted the watchdog automatically and a new `python.exe` process will appear.

---

## 6. Troubleshooting

### Last Run Result is not `0x0`

Open Task Scheduler, right-click your task, and choose **Properties**. Go to the
**History** tab. If the tab is empty, first click **Enable All Tasks History** in the
right-hand Actions panel, then run the task again. Each run is listed with a detailed
event log entry.

Common result codes:

| Result code | Likely cause | Fix |
|---|---|---|
| `0x1` | Script exited with an error immediately on start | Run the command manually first — see below |
| `0x41D` | Task was forcefully stopped after the time limit | Disable "Stop the task if it runs longer than" (step 22) |
| `0x41306` | Task could not start at all | Verify the Program/script path points to the venv `python.exe` |

### Test the command manually before relying on Task Scheduler

Open a **Command Prompt** (search for `cmd` in the Start menu) and run the exact
command that Task Scheduler will use, with your actual project path substituted in:

```
"D:\TEMP\test\.venv\Scripts\python.exe" -u "D:\TEMP\test\src\scripts\watchdog.py" --config-name watchdog_cmd_01
```

If this command fails, Task Scheduler will also fail. Fix any errors shown in the
terminal window before continuing.

### The task runs but no notifications appear

This almost always means the task is running under the wrong session option. Open the
task Properties, go to the **General** tab, and confirm **Run only when user is logged
on** is selected. If **Run whether user is logged in or not** is selected, change it
and save — see step 7 for the explanation.

### Checking which Python interpreter is being used

In Task Manager → Details tab, right-click any `python.exe` → **Open file location**.
The folder that opens should be `D:\TEMP\test\.venv\Scripts\`. If it opens a different
location (e.g. `C:\Python312\` or somewhere under `AppData\Local\Programs\Python\`),
the task is using the wrong Python. Open the task Properties, go to the **Actions**
tab, edit the action, and update the **Program / script** field to the correct venv
path as shown in [Section 3](#3-the-action-tab--exact-values).

---

## 7. Supervision & Recovery Architecture

### 7.1 Recovery Logic (`checker.py`)

When `checker.py` determines the watchdog is unhealthy (PID missing, process dead, PID
recycled to a different process, or heartbeat stale beyond the threshold), it executes a
**4-step recovery sequence**:

1. **Kill the watchdog process tree.** Uses `taskkill /PID <pid> /T /F` to terminate the
   watchdog and all its child processes (workers) in one operation.
2. **Clean up zombie workers.** Iterates over all `.pid` files in the heartbeat directory
   and kills any remaining processes whose PIDs differ from the watchdog's — catching
   orphaned workers that survived the tree kill.
3. **Wait for OS reclamation (2.0 s).** A `time.sleep(2.0)` pause gives the Windows
   kernel time to fully terminate the killed processes, release file handles on `.pid`
   and `.hb` files, and reclaim PID numbers. Without this delay, the new watchdog
   instance could collide with zombie entries or fail to acquire file handles.
4. **Restart the watchdog.** Launches a new `watchdog.py` process via `subprocess.Popen`
   with the same `--config-name`, then exits.

### 7.2 PID Recycling Mitigation (`checker.py`)

A simple `os.kill(pid, 0)` check only confirms that *some* process with that PID exists.
On Windows, PIDs are aggressively recycled — after a reboot or crash, an unrelated
process may inherit the old PID, causing the checker to incorrectly report the watchdog
as "healthy".

To prevent this, `checker.py` performs a two-layer verification:

1. **Existence check:** `os.kill(pid, 0)` — fast short-circuit for dead PIDs.
2. **Identity check:** Queries `wmic process where ProcessId={pid} get CommandLine` and
   confirms the command line contains both `watchdog.py` and the expected
   `--config-name` value.

If WMIC fails (transient WMI service error), the function **falls back** to the basic
alive check and logs a warning, rather than triggering a false recovery.

### 7.3 Graceful Worker Shutdown (`watchdog.py`)

When the watchdog needs to stop a worker (frozen detection or shutdown signal), it uses a
two-phase escalation pattern:

1. **Graceful phase:** `process.terminate()` sends `CTRL_BREAK_EVENT` on Windows,
   allowing the worker to execute `finally` blocks (e.g. `hc_heartbeat.stop()`, log
   flushing). The watchdog then calls `process.wait(timeout=5)`.
2. **Forced phase:** If the worker does not exit within 5 seconds, the watchdog catches
   `subprocess.TimeoutExpired` and calls `process.kill()` (`TerminateProcess` — cannot
   be caught by the worker), followed by `process.wait()` to collect the exit status.

This ensures workers have a chance to clean up before being forcefully terminated.

---

## 8. Logging Architecture

Both `checker.py` and `watchdog.py` use the project's centralized
[`src.utils.logger.Logger`](../utils/logger.py) singleton for all log output. This
provides a consistent logging interface across the entire codebase.

### Dual-handler design

On startup, each script calls `_add_script_file_handler(config_name)`, which attaches a
supplemental `RotatingFileHandler` to the `Logger` singleton. Log messages are therefore
written to **three destinations simultaneously**:

| Destination | Source | Rotation |
|---|---|---|
| Console (`stdout`) | `Logger` singleton's default `StreamHandler` | None |
| `logs/python_log_file_limit_console.log` | `Logger` singleton's default `RotatingFileHandler` | 5 MB, 2 backups |
| `logs/checker_{config_name}.log` or `logs/watchdog_{config_name}.log` | Supplemental `RotatingFileHandler` added at startup | 5 MB, 3 backups |

The per-script log file uses the format `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
(matching the project convention) and is stored in the `logs/` directory at the project root.

### Exception tracebacks

The `Logger` wrapper's `.error()` method accepts only a `message: str` argument. For
exception-handling sites that require full stack traces, the scripts access the
underlying stdlib logger via `Logger().get().error(msg, exc_info=True)`. This pattern
appears in the watchdog's monitoring loop and startup sequence.

---

## 9. Operational Parameters

| Parameter | Value | Location | Purpose |
|---|---|---|---|
| `SCHEDULER_INTERVAL` | 30 s | `checker.py` | How often Task Scheduler invokes the checker |
| `HEARTBEAT_THRESHOLD` | 90 s | `checker.py` | Max allowed age of `watchdog.hb` before recovery. Computed as `(SCHEDULER_INTERVAL × 2) × 1.5` |
| `CHECK_INTERVAL` | 30 s | `watchdog.py` | How often the watchdog polls workers for crashes / freezes |
| `STARTUP_GRACE_PERIOD` | 5 s | `watchdog.py` | Delay after spawning workers, before the first monitoring poll |
| `WATCHDOG_HEALTHCHECK_INTERVAL` | 60 s | `watchdog.py` | How often the watchdog pings Healthchecks.io |
| Worker `timeout` | 90–360 s | `.conf` files | Per-worker heartbeat freshness threshold |
| Worker `--delay` | 1–5 min | `.conf` files | Sleep duration between worker action cycles |

### Startup Grace Period

The `STARTUP_GRACE_PERIOD` (5 s) is critical for preventing false-positive "frozen"
detections on boot. When the watchdog starts, workers need time to initialize, execute
their first action, and create their `.hb` heartbeat files. The watchdog spawns all
workers **first**, then sleeps for the grace period **before** entering the monitoring
loop. Without this ordering, the first poll would see no `.hb` files and immediately flag
every worker as frozen — triggering unnecessary restart churn.

### CHECK_INTERVAL tuning

The `CHECK_INTERVAL` (30 s) is sized at `min(worker_timeout) / 3` = `90 / 3` = 30 s.
This ensures at least 3 polling cycles occur within the shortest worker timeout window,
providing reliable crash and freeze detection without excessive filesystem I/O. The
previous value (5 s) caused 12–60 unnecessary `stat()` calls per worker per minute.
