# Configuring Windows Task Scheduler for checker.py (Outer Sentinel)

This guide explains how to configure Windows Task Scheduler to run `checker.py` as the
**outer sentinel** of the supervision system — the process that watches the watchdog and
restarts it automatically if it crashes or freezes.

> **Related guide:** For setting up the long-running `watchdog.py` daemon in Task
> Scheduler, see [`docs/tutorials/PERSISTENT_RUN.md`](PERSISTENT_RUN.md).

---

## Table of Contents

1. [System Architecture Overview](#1-system-architecture-overview)
2. [Prerequisites](#2-prerequisites)
3. [The Action Tab — Exact Values](#3-the-action-tab--exact-values)
4. [Step-by-Step Task Scheduler Setup](#4-step-by-step-task-scheduler-setup)
5. [Recovery Logic & Timing](#5-recovery-logic--timing)
6. [Verifying the Setup](#6-verifying-the-setup)
7. [Troubleshooting](#7-troubleshooting)
8. [Operational Parameters](#8-operational-parameters)

---

## 1. System Architecture Overview

The full supervision hierarchy is:

```
Windows Task Scheduler  (every 60 s, via XML-configured trigger)
  └── checker.py --config-name <config_name>        ← ephemeral outer sentinel
        └── watchdog.py --config-name <config_name> ← long-running daemon
              ├── worker_script_01.py (worker-01)    ← worker process
              ├── worker_script_01.py (worker-02)    ← worker process
              └── worker_script_02.py (worker-03)    ← worker process
```

### Why checker.py is ephemeral

The classic "who watches the watchman?" problem arises when the component responsible for
supervising a process is itself a long-running daemon — if *it* crashes, nothing remains
to restart it.

`checker.py` is designed to be **ephemeral**: it starts, evaluates the watchdog's health,
takes action if required, and exits. Windows Task Scheduler — an OS-level service that
runs independently of any user process — invokes it on a 60-second cycle. Because
`checker.py` is not a long-running process, it cannot crash in a way that disables
supervision. If a single invocation fails (e.g. due to a transient error), the next
scheduled invocation runs as normal.

### Component responsibilities

| Component | Role | Lifetime |
|---|---|---|
| **Windows Task Scheduler** | Invokes `checker.py` every 60 seconds | Permanent (OS service) |
| **`checker.py`** | Checks watchdog health; triggers recovery if unhealthy | Ephemeral (seconds) |
| **`watchdog.py`** | Monitors and restarts crashed or frozen workers | Long-running daemon |
| **Worker scripts** | Perform application tasks; write heartbeat files | Long-running |

---

## 2. Prerequisites

Before starting, confirm the following:

- **Virtual environment is set up.** The `.venv` folder must exist inside the project
  root (e.g. `D:\TEMP\pt\.venv`). Verify this by opening the project folder in File
  Explorer and checking for the `.venv` directory.
- **You know the full project path.** You will need to type it during setup. To find it,
  open File Explorer, navigate to the project folder, and click the address bar — it will
  display the complete path (e.g. `D:\TEMP\pt`).
- **A valid TOML configuration file exists** in the `configurations/` directory at the
  project root (e.g. `configurations/watchdogs/watchdog_cmd_02.toml`). The `--config-name` argument
  passed to `checker.py` must match the filename without the `.toml` extension. See
  [`docs/tutorials/CONF_TO_TOML.md`](CONF_TO_TOML.md) if you are migrating an older
  `.conf`/HOCON profile.
- **Administrator access.** Task Scheduler requires elevated permissions to create tasks.

---

## 3. The Action Tab — Exact Values

Replace `D:\TEMP\pt` with your actual project path in all three fields below, and replace
`<your_config_name>` with the name of your TOML configuration (e.g. `watchdog_cmd_02`).

| Field | Value |
|---|---|
| **Program / script** | `D:\TEMP\pt\.venv\Scripts\python.exe` |
| **Add arguments** | `-u D:\TEMP\pt\src\scripts_production\checker.py --config-name <your_config_name>` |
| **Start in** | `D:\TEMP\pt\src\scripts_production` |

**Why each value:**

- **Program / script** — Points to `python.exe` inside `.venv\Scripts\`. This is the
  virtual environment's Python interpreter, which has all project dependencies installed.
  Using the system Python will cause a `ModuleNotFoundError` at runtime.
- **Add arguments** — The `-u` flag disables output buffering so log messages are written
  to log files immediately. The full path to `checker.py` follows. `--config-name` is
  mandatory — the script exits with an error if it is omitted or blank. It selects the
  TOML configuration file (e.g. `watchdog_cmd_02` loads
  `configurations/watchdogs/watchdog_cmd_02.toml`) and determines which heartbeat directory and
  watchdog instance the checker monitors.
- **Start in** — Sets the working directory to the `scripts_production` folder. Both
  `checker.py` and `watchdog.py` use `Path(__file__).resolve().parent` to resolve all
  paths relative to their own location on disk, so the **Start in** value is not strictly
  required for correct operation. It is retained as a best-practice convention.

> ⚠️ **Do not use `python` or `python.exe` alone in the Program/script field.** This
> would invoke the system Python, which does not have project dependencies installed, and
> the task will fail with `ModuleNotFoundError`.

---

## 4. Step-by-Step Task Scheduler Setup

### Open Task Scheduler

1. Press **Win + S** to open the search bar.
2. Type `Task Scheduler` and press **Enter**.
3. If Windows requests administrator permission, click **Yes**.

### Create a new task

4. In the right-hand **Actions** panel, click **Create Task…**
   > ⚠️ Choose **Create Task…**, not "Create Basic Task…". The basic wizard does not
   > expose the repeat-interval settings needed for the 1-minute cycle.

A dialog with several tabs will open. Work through each tab below.

### General tab

5. **Name:** Enter a descriptive name, e.g. `Checker – watchdog_cmd_02`.
6. **Description** *(optional)*: e.g.
   `Outer sentinel for watchdog_cmd_02. Runs every 60 s; restarts watchdog if unhealthy.`
7. **Security options:**
   - Select **Run only when user is logged on**.

   > ⚠️ **Do not select "Run whether user is logged in or not".** That option places the
   > process in Windows Session 0 — an isolated background session invisible to the
   > desktop. Toast notifications delivered by `winotify` require a desktop session and
   > will be silently suppressed in Session 0. Always use "Run only when user is logged
   > on" for every task in this supervision chain.

8. Tick **Run with highest privileges**.

### Triggers tab

> ⚠️ **GUI limitation:** The Windows Task Scheduler repeat-interval dropdown enforces a
> minimum of **5 minutes**, and the XML import validator rejects intervals shorter than
> 1 minute. A basic Daily trigger is added here; the 1-minute repeat interval is applied
> via XML editing after the task is first saved — see
> [Set the 1-minute repeat interval via XML](#set-the-1-minute-repeat-interval-via-xml)
> below.

9.  Click **New…** to add a trigger.
10. In the **Begin the task** dropdown, select **On a schedule**.
11. Select **Daily**. Leave **Repeat task every** unchecked — the repeat interval will be
    configured via XML after the task is initially saved.
12. Ensure **Enabled** is ticked at the bottom of the dialog.
13. Click **OK**.

### Actions tab

14. Click **New…** to add an action.
15. **Action:** Leave as `Start a program`.
16. Fill in the three fields with the values from [Section 3](#3-the-action-tab--exact-values):
    - **Program / script:** `D:\TEMP\pt\.venv\Scripts\python.exe`
    - **Add arguments:** `-u D:\TEMP\pt\src\scripts_production\checker.py --config-name watchdog_cmd_02`
    - **Start in:** `D:\TEMP\pt\src\scripts_production`
17. Click **OK**.

### Conditions tab

18. Under **Power**, untick **Start the task only if the computer is on AC power**.

    > This is enabled by default on laptops. If left on, `checker.py` will stop being
    > invoked when the machine is running on battery and supervision will cease entirely
    > until mains power is restored.

### Settings tab

19. **Untick "Stop the task if it runs longer than"** and clear any value in that field.

    > ⚠️ This is **enabled by default** (typically 3 days). While `checker.py` is
    > ephemeral and exits within seconds under normal conditions, leaving this enabled can
    > cause Task Scheduler to flag the task erroneously if timing interactions accumulate.
    > Clear it as a precaution.

20. In the **If the task is already running, then the following rule applies** dropdown,
    select **Do not start a new instance**.

    > This prevents concurrent `checker.py` invocations in the unlikely event that one
    > run takes longer than 1 minute (e.g. during a recovery sequence that includes the
    > mandatory 2-second OS-reclamation sleep and a `taskkill` call).

21. Click **OK** to save the task.
22. If prompted, enter your Windows password and click **OK**.

### Set the 1-minute repeat interval via XML

The Task Scheduler GUI enforces a minimum repeat interval of 5 minutes, and the XML
import validator rejects intervals shorter than 1 minute. A 1-minute repeat — the
shortest interval the validator accepts — must therefore be applied by editing the task's
underlying XML definition. This is a one-time step performed immediately after the
initial save.

**Export the task**

23. In the Task Scheduler library, right-click the task you just saved and choose
    **Export…**
24. Save the file to a convenient location (e.g. `checker_task.xml` on your Desktop).

**Edit the XML**

25. Open `checker_task.xml` in Notepad (or any plain-text editor — do not use Word or
    WordPad, as they may alter the encoding).
26. Locate the `<CalendarTrigger>` block. It will look similar to:

    ```xml
    <CalendarTrigger>
      <StartBoundary>2026-01-01T00:00:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
    ```

27. Insert a `<Repetition>` element **inside** the `<CalendarTrigger>` block, immediately
    after the `<Enabled>` line, so the block reads:

    ```xml
    <CalendarTrigger>
      <StartBoundary>2026-01-01T00:00:00</StartBoundary>
      <Enabled>true</Enabled>
      <Repetition>
        <Interval>PT1M</Interval>
        <StopAtDurationEnd>false</StopAtDurationEnd>
      </Repetition>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
    ```

    `PT1M` is the ISO 8601 duration for 1 minute. The `<Duration>` element is omitted
    entirely — when absent, Task Scheduler repeats the task indefinitely.
    `StopAtDurationEnd` is set to `false` as an explicit safeguard.

28. Save the XML file.

**Delete the original task and import the edited XML**

29. In Task Scheduler, right-click the original task and choose **Delete**. Confirm when
    prompted.
30. In the right-hand **Actions** panel, click **Import Task…**
31. Select your edited `checker_task.xml` and click **Open**.
32. The task reappears with all settings intact. Open its **Properties → Triggers** tab
    and confirm the entry now reads **Repeat every 1 minute for Indefinitely**.
    Click **OK**.

---

## 5. Recovery Logic & Timing

### 5.1 How checker.py evaluates watchdog health

On each invocation, `checker.py` performs two checks:

1. **Process identity** — reads the PID from `heartbeats_<config_name>/watchdog.pid` and
   verifies via `os.kill(pid, 0)` that a process with that PID is running. It then
   queries `wmic process where ProcessId=<pid> get CommandLine` to confirm that the
   process is actually `watchdog.py` running with the expected `--config-name`. This
   two-layer check guards against PID recycling on Windows, where a crashed watchdog's
   PID may be reassigned to an unrelated process that would otherwise appear healthy.
   If the WMIC query fails transiently (e.g. the WMI service is temporarily unavailable),
   the checker falls back to the basic alive check and logs a warning rather than
   triggering a false recovery.

2. **Heartbeat freshness** — checks the modification time of
   `heartbeats_<config_name>/watchdog.hb`. If the file is older than `HEARTBEAT_THRESHOLD`
   (90 s), the watchdog is considered frozen and recovery is initiated.

### 5.2 Timing interaction

| Event | Period |
|---|---|
| Task Scheduler fires `checker.py` | Every ≈60 s (via XML-configured trigger) |
| `watchdog.py` updates `watchdog.hb` | Every 30 s (`CHECK_INTERVAL`) |
| `HEARTBEAT_THRESHOLD` | 90 s |

With a 60-second check cycle and a 90-second `HEARTBEAT_THRESHOLD`, a failed watchdog is
detected within **1–2 checker invocations** (60–120 seconds). Because `watchdog.py`
updates `watchdog.hb` every 30 seconds (`CHECK_INTERVAL`), the heartbeat file is always
fresh at the start of each 60-second window under normal operation. If the watchdog
fails, the heartbeat goes stale and crosses the 90-second threshold within the first or
second subsequent checker cycle, at which point recovery is triggered. This remains well
within safe operational margins.

### 5.3 Recovery sequence

When `checker.py` determines the watchdog is unhealthy, it performs a 4-step sequence:

1. **Kill the watchdog process tree.** Issues `taskkill /PID <pid> /T /F` to terminate
   the watchdog and all its child worker processes in a single operation.
2. **Clean up orphaned workers.** Iterates over all `.pid` files in the heartbeat
   directory and kills any remaining processes whose PID differs from the watchdog's PID
   — catching workers that survived the tree kill.
3. **Wait 2 seconds.** Allows the Windows kernel to fully reclaim the terminated processes
   and release file handles on the `.pid` and `.hb` files before the new watchdog starts.
4. **Restart the watchdog.** Launches a new `watchdog.py` process via `subprocess.Popen`
   with the same `--config-name`, then exits.

---

## 6. Verifying the Setup

### Check the task appears in the list

After clicking OK, the Task Scheduler library (the main panel) should show your new task.
If you do not see it, click **Task Scheduler Library** in the left-hand tree to refresh
the view.

### Run the task manually to test it

31. Right-click the task in the list and choose **Run**.
32. The **Last Run Result** column should update to `0x0` within a few seconds.
    - `0x0` means `checker.py` started and exited successfully.
    - Any other value indicates an error — see [Section 7](#7-troubleshooting).

### Confirm the checker ran via the History tab

33. Right-click the task and choose **Properties**.
34. Go to the **History** tab.
    - If the tab is empty, first click **Enable All Tasks History** in the right-hand
      Actions panel, then run the task again.
    - Each invocation is listed. Confirm that events show **Task completed** status with
      result `0x0`. You should see entries appearing approximately every 60 seconds once
      the trigger is active.

### Verify heartbeat files are being updated

35. Navigate to `src\scripts_production\heartbeats_<config_name>\` in File Explorer
    (e.g. `heartbeats_watchdog_cmd_02\`).
36. After the watchdog has been running for at least one `CHECK_INTERVAL` (30 s), confirm
    that `watchdog.hb` and `watchdog.pid` are present and that the modification timestamp
    of `watchdog.hb` is recent (within the last 60 seconds).
37. Worker heartbeat files (`<worker_name>.hb`) and PID files (`<worker_name>.pid`) should
    also be present for each worker defined in the configuration.

### Confirm the watchdog process is running

38. Press **Ctrl + Shift + Esc** to open Task Manager.
39. Click the **Details** tab.
40. Look for `python.exe` entries. A healthy system will show one `python.exe` for the
    watchdog daemon plus one per configured worker.

    > **Tip:** Right-click a `python.exe` entry and choose **Open file location** to
    > confirm it points to `.venv\Scripts\python.exe` and not a system Python.

---

## 7. Troubleshooting

### Last Run Result is not `0x0`

Open the task's **Properties → History** tab. If the tab is empty, click **Enable All
Tasks History** in the right-hand Actions panel first, then re-run the task. Each run is
listed with a detailed event log entry showing the exit code.

Common result codes:

| Result code | Likely cause | Fix |
|---|---|---|
| `0x1` | `checker.py` exited with an error | Run the command manually — see below |
| `0x41306` | Task could not start | Verify the Program/script path points to the venv `python.exe` |
| `0x41D` | Task was stopped after a time limit | Disable "Stop the task if it runs longer than" (step 19) |

### Test the command manually before relying on Task Scheduler

Open a **Command Prompt** (search for `cmd` in the Start menu) and run the exact command
that Task Scheduler will use, substituting your actual project path:

```
"D:\TEMP\pt\.venv\Scripts\python.exe" -u "D:\TEMP\pt\src\scripts_production\checker.py" --config-name watchdog_cmd_02
```

`checker.py` should start, log a health-status message, and exit within a few seconds.
If it prints an error or a traceback, fix the underlying issue before relying on Task
Scheduler.

### Configuration file not found

If the command above exits with `Could not load configuration '<name>'`, verify that:

- The configuration file exists at `configurations\<your_config_name>.toml`.
- The `--config-name` value in the **Add arguments** field exactly matches the filename
  (without the `.toml` extension), including capitalisation.

### Watchdog is repeatedly restarted (constant recovery loop)

If `checker.py` triggers a recovery on every invocation, the watchdog is not surviving
long enough to update its heartbeat file. Investigate by:

1. Checking `logs\watchdog_<config_name>.log` for errors written during the watchdog's
   short-lived startup.
2. Running `watchdog.py` manually in a terminal to observe startup errors directly:
   ```
   "D:\TEMP\pt\.venv\Scripts\python.exe" -u "D:\TEMP\pt\src\scripts_production\watchdog.py" --config-name watchdog_cmd_02
   ```

### Task runs but no notifications appear

Confirm **Run only when user is logged on** is selected in the task's **General** tab.
Session 0 isolation silently suppresses toast notifications — see step 7 for the full
explanation.

### Checking which Python interpreter is being used

In Task Manager → Details tab, right-click any `python.exe` → **Open file location**.
The folder that opens should be `.venv\Scripts\`. If it opens a system Python location
(e.g. `C:\Python312\` or somewhere under `AppData\Local\Programs\Python\`), the task is
using the wrong interpreter. Open the task Properties, go to the **Actions** tab, edit
the action, and correct the **Program / script** field as shown in
[Section 3](#3-the-action-tab--exact-values).

---

## 8. Operational Parameters

| Parameter | Value | Location | Purpose |
|---|---|---|---|
| `SCHEDULER_INTERVAL` | 60 s (effective) | `checker.py` | Effective Task Scheduler invocation interval. The in-code constant is 30 s, but 60 s (`PT1M`) is the minimum interval accepted by the Windows XML import validator |
| `HEARTBEAT_THRESHOLD` | 90 s | `checker.py` | Max allowed age of `watchdog.hb` before recovery is triggered; remains adequate at a 60 s check interval (see timing diagram) |
| `CHECK_INTERVAL` | 30 s | `watchdog.py` | How often the watchdog polls workers and updates `watchdog.hb` |
| `STARTUP_GRACE_PERIOD` | 5 s | `watchdog.py` | Delay after spawning workers before the first monitoring poll |
| `WATCHDOG_HEALTHCHECK_INTERVAL` | 60 s | `watchdog.py` | How often the watchdog pings Healthchecks.io |
| Worker `timeout` | 90–360 s | `.toml` files | Per-worker heartbeat freshness threshold |
| Worker `--delay` | 1–5 min | `.toml` files | Sleep duration between worker action cycles |

### Timing diagram

Normal operation:

```
t=0s    checker.py fires → watchdog healthy → exits
t=60s   checker.py fires → watchdog healthy → exits
t=120s  checker.py fires → watchdog healthy → exits
```

Failure scenario — watchdog fails silently at t=31 s (last `.hb` written at ~t=30 s):

```
t=60s   checker.py fires → watchdog.hb is ~30 s old → below 90 s threshold → exits
t=120s  checker.py fires → watchdog.hb is ~90 s old → THRESHOLD HIT → recovery
          └─ kills watchdog process tree (taskkill /T /F)
          └─ cleans up orphaned worker PIDs
          └─ waits 2 s for OS to reclaim handles
          └─ starts new watchdog.py → exits
t=180s  checker.py fires → new watchdog healthy → exits
```

With a 60-second check cycle, the worst-case detection window is approximately 120
seconds: one check may observe a stale heartbeat that has not yet crossed the 90-second
threshold and exit without action, while the following check crosses the threshold and
triggers recovery. This is well within safe operational margins given the system's design
— the watchdog updates `watchdog.hb` every 30 seconds (`CHECK_INTERVAL`), so failure is
never more than two checker cycles away from being detected.
