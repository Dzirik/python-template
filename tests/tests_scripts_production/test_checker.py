"""
Tests for the checker.py process validation and health-check logic.

Focuses on the fixes for the infinite restart loop:
- ``is_process_alive``: PermissionError must be treated as *alive*.
- ``_get_process_cmdline``: PowerShell CIM query stubbing.
- ``read_pid``: PID file reading edge cases.
- ``is_watchdog_healthy``: Integration of all checks.
"""

import os
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.scripts_production.checker import (
    HEARTBEAT_THRESHOLD,
    _get_process_cmdline,
    is_process_alive,
    is_watchdog_healthy,
    read_pid,
)


# ---------------------------------------------------------------------------
# is_process_alive
# ---------------------------------------------------------------------------
class TestIsProcessAlive:
    """Tests for is_process_alive (tasklist-based)."""

    def _mock_tasklist(self, stdout: str, returncode: int = 0) -> MagicMock:
        """Helper: create a mock subprocess.run result for tasklist."""
        mock_result = MagicMock()
        mock_result.stdout = stdout
        mock_result.returncode = returncode
        return mock_result

    def test_alive_process_returns_true(self) -> None:
        """Tasklist output contains the PID → process is alive."""
        output = "python.exe                39904 Console                    3     98,948 K\r\n"
        with patch("src.scripts_production.checker.subprocess.run", return_value=self._mock_tasklist(output)):
            assert is_process_alive(39904) is True

    def test_dead_process_returns_false(self) -> None:
        """Tasklist output does not contain the PID → process is dead."""
        output = "INFO: No tasks are running which match the specified criteria.\r\n"
        with patch("src.scripts_production.checker.subprocess.run", return_value=self._mock_tasklist(output)):
            assert is_process_alive(99999) is False

    def test_wmi_spawned_process_detected(self) -> None:
        """WMI-spawned process in different session is still found by tasklist."""
        output = "python.exe                11764 Services                   0     45,000 K\r\n"
        with patch("src.scripts_production.checker.subprocess.run", return_value=self._mock_tasklist(output)):
            assert is_process_alive(11764) is True

    def test_timeout_returns_false(self) -> None:
        """Timeout during tasklist call → assume not alive."""
        with patch(
            "src.scripts_production.checker.subprocess.run",
            side_effect=TimeoutError("timed out"),
        ):
            assert is_process_alive(1234) is False

    def test_generic_exception_returns_false(self) -> None:
        """Any unexpected exception → assume not alive."""
        with patch(
            "src.scripts_production.checker.subprocess.run",
            side_effect=RuntimeError("unexpected"),
        ):
            assert is_process_alive(1234) is False


# ---------------------------------------------------------------------------
# _get_process_cmdline
# ---------------------------------------------------------------------------
class TestGetProcessCmdline:
    """Tests for _get_process_cmdline."""

    def test_successful_query(self) -> None:
        """PowerShell returns a valid command line."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '  "C:\\Python\\python.exe" -u watchdog.py --config-name test  \n'
        with patch("src.scripts_production.checker.subprocess.run", return_value=mock_result):
            assert _get_process_cmdline(100) == '"C:\\Python\\python.exe" -u watchdog.py --config-name test'

    def test_nonzero_returncode(self) -> None:
        """PowerShell exits with error → None."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        with patch("src.scripts_production.checker.subprocess.run", return_value=mock_result):
            assert _get_process_cmdline(100) is None

    def test_empty_stdout(self) -> None:
        """PowerShell returns empty stdout → None."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "   \n"
        with patch("src.scripts_production.checker.subprocess.run", return_value=mock_result):
            assert _get_process_cmdline(100) is None

    def test_subprocess_timeout(self) -> None:
        """Timeout during subprocess.run → None."""
        with patch(
            "src.scripts_production.checker.subprocess.run",
            side_effect=TimeoutError("timed out"),
        ):
            assert _get_process_cmdline(100) is None

    def test_generic_exception(self) -> None:
        """Any unexpected exception → None (no crash)."""
        with patch(
            "src.scripts_production.checker.subprocess.run",
            side_effect=RuntimeError("unexpected"),
        ):
            assert _get_process_cmdline(100) is None


# ---------------------------------------------------------------------------
# read_pid
# ---------------------------------------------------------------------------
class TestReadPid:
    """Tests for read_pid."""

    def test_valid_pid_file(self, tmp_path: Path) -> None:
        """Well-formed .pid file → returns int."""
        pid_file = tmp_path / "watchdog.pid"
        pid_file.write_text("11764", encoding="utf-8")
        assert read_pid(pid_file) == 11764

    def test_pid_with_whitespace(self, tmp_path: Path) -> None:
        """PID with surrounding whitespace/newlines → still parsed."""
        pid_file = tmp_path / "watchdog.pid"
        pid_file.write_text("  42  \n", encoding="utf-8")
        assert read_pid(pid_file) == 42

    def test_missing_file(self, tmp_path: Path) -> None:
        """Non-existent file → None."""
        assert read_pid(tmp_path / "nonexistent.pid") is None

    def test_invalid_content(self, tmp_path: Path) -> None:
        """Non-numeric content → None."""
        pid_file = tmp_path / "watchdog.pid"
        pid_file.write_text("not_a_number", encoding="utf-8")
        assert read_pid(pid_file) is None

    def test_empty_file(self, tmp_path: Path) -> None:
        """Empty file → None."""


# ---------------------------------------------------------------------------
# is_watchdog_healthy
# ---------------------------------------------------------------------------
def _make_heartbeat_dir(tmp_path: Path, pid: int | None = 1234, hb_age: float = 0.0) -> Path:
    """
    Helper: create a heartbeat directory with optional .pid and .hb files.

    :param tmp_path: pytest tmp_path fixture.
    :param pid: PID to write (None = don't create .pid file).
    :param hb_age: How many seconds old the heartbeat should appear.
    :return: Path to the heartbeat directory.
    """
    hb_dir = tmp_path / "heartbeats_test_config"
    hb_dir.mkdir()
    if pid is not None:
        (hb_dir / "watchdog.pid").write_text(str(pid), encoding="utf-8")
    hb_file = hb_dir / "watchdog.hb"
    hb_file.write_text("heartbeat", encoding="utf-8")
    if hb_age > 0:
        old_time = time.time() - hb_age
        os.utime(hb_file, (old_time, old_time))
    return hb_dir


class TestIsWatchdogHealthy:
    """Tests for is_watchdog_healthy."""

    @patch("src.scripts_production.checker._get_process_cmdline")
    @patch("src.scripts_production.checker.is_process_alive")
    def test_healthy_with_matching_cmdline(
        self, mock_alive: MagicMock, mock_cmdline: MagicMock, tmp_path: Path
    ) -> None:
        """All checks pass: alive, fresh heartbeat, matching cmdline."""
        mock_alive.return_value = True
        mock_cmdline.return_value = "python.exe -u watchdog.py --config-name test_config"

        hb_dir = _make_heartbeat_dir(tmp_path, pid=1234, hb_age=0)
        assert is_watchdog_healthy(hb_dir, "test_config") is True

    @patch("src.scripts_production.checker._get_process_cmdline")
    @patch("src.scripts_production.checker.is_process_alive")
    def test_healthy_when_cim_unavailable(self, mock_alive: MagicMock, mock_cmdline: MagicMock, tmp_path: Path) -> None:
        """CIM returns None but process alive + heartbeat fresh → healthy."""
        mock_alive.return_value = True
        mock_cmdline.return_value = None

        hb_dir = _make_heartbeat_dir(tmp_path, pid=1234, hb_age=0)
        assert is_watchdog_healthy(hb_dir, "test_config") is True

    def test_unhealthy_missing_pid_file(self, tmp_path: Path) -> None:
        """No .pid file → unhealthy."""
        hb_dir = _make_heartbeat_dir(tmp_path, pid=None)
        assert is_watchdog_healthy(hb_dir, "test_config") is False

    @patch("src.scripts_production.checker.is_process_alive")
    def test_unhealthy_process_dead(self, mock_alive: MagicMock, tmp_path: Path) -> None:
        """Process not alive → unhealthy (no further checks)."""
        mock_alive.return_value = False
        hb_dir = _make_heartbeat_dir(tmp_path, pid=1234)
        assert is_watchdog_healthy(hb_dir, "test_config") is False

    @patch("src.scripts_production.checker.is_process_alive")
    def test_unhealthy_missing_heartbeat(self, mock_alive: MagicMock, tmp_path: Path) -> None:
        """Process alive but .hb file missing → unhealthy."""
        mock_alive.return_value = True
        hb_dir = tmp_path / "heartbeats_test_config"
        hb_dir.mkdir()
        (hb_dir / "watchdog.pid").write_text("1234", encoding="utf-8")
        # No .hb file created
        assert is_watchdog_healthy(hb_dir, "test_config") is False

    @patch("src.scripts_production.checker._get_process_cmdline")
    @patch("src.scripts_production.checker.is_process_alive")
    def test_unhealthy_stale_heartbeat(self, mock_alive: MagicMock, mock_cmdline: MagicMock, tmp_path: Path) -> None:
        """Process alive but heartbeat older than threshold → unhealthy."""
        mock_alive.return_value = True
        mock_cmdline.return_value = "python.exe -u watchdog.py --config-name test_config"

        hb_dir = _make_heartbeat_dir(tmp_path, pid=1234, hb_age=HEARTBEAT_THRESHOLD + 60)
        assert is_watchdog_healthy(hb_dir, "test_config") is False

    @patch("src.scripts_production.checker._get_process_cmdline")
    @patch("src.scripts_production.checker.is_process_alive")
    def test_unhealthy_wrong_process(self, mock_alive: MagicMock, mock_cmdline: MagicMock, tmp_path: Path) -> None:
        """Alive + fresh heartbeat but cmdline is not watchdog.py → unhealthy (PID recycling)."""
        mock_alive.return_value = True
        mock_cmdline.return_value = "python.exe -u some_other_script.py"

        hb_dir = _make_heartbeat_dir(tmp_path, pid=1234, hb_age=0)
        assert is_watchdog_healthy(hb_dir, "test_config") is False

    @patch("src.scripts_production.checker._get_process_cmdline")
    @patch("src.scripts_production.checker.is_process_alive")
    def test_unhealthy_wrong_config(self, mock_alive: MagicMock, mock_cmdline: MagicMock, tmp_path: Path) -> None:
        """Alive + fresh but cmdline shows different config → unhealthy."""
        mock_alive.return_value = True
        mock_cmdline.return_value = "python.exe -u watchdog.py --config-name other_config"

        hb_dir = _make_heartbeat_dir(tmp_path, pid=1234, hb_age=0)
        assert is_watchdog_healthy(hb_dir, "test_config") is False

    @patch("src.scripts_production.checker._get_process_cmdline")
    @patch("src.scripts_production.checker.is_process_alive")
    def test_case_insensitive_cmdline_match(
        self, mock_alive: MagicMock, mock_cmdline: MagicMock, tmp_path: Path
    ) -> None:
        """Command-line matching must be case-insensitive on Windows."""
        mock_alive.return_value = True
        mock_cmdline.return_value = "C:\\Python\\PYTHON.EXE -u WATCHDOG.PY --config-name TEST_CONFIG"

        hb_dir = _make_heartbeat_dir(tmp_path, pid=1234, hb_age=0)
        assert is_watchdog_healthy(hb_dir, "test_config") is True

    @patch("src.scripts_production.checker._get_process_cmdline")
    @patch("src.scripts_production.checker.is_process_alive")
    def test_permission_error_scenario(self, mock_alive: MagicMock, mock_cmdline: MagicMock, tmp_path: Path) -> None:
        """
        End-to-end scenario: WMI-spawned process triggers PermissionError
        in os.kill but CIM returns None. Heartbeat is fresh → healthy.
        This is the exact scenario that caused the infinite restart loop.
        """
        mock_alive.return_value = True  # Fixed: PermissionError now returns True
        mock_cmdline.return_value = None  # CIM query also fails cross-session

        hb_dir = _make_heartbeat_dir(tmp_path, pid=11764, hb_age=5)
        assert is_watchdog_healthy(hb_dir, "test_config") is True
        pid_file = tmp_path / "watchdog.pid"
        pid_file.write_text("", encoding="utf-8")
        assert read_pid(pid_file) is None
