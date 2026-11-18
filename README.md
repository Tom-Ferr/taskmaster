# Taskmaster

Taskmaster is a Python-based process manager inspired by Supervisor. It provides a daemon responsible for managing process lifecycles and an interactive command-line interface (CLI) to control and monitor managed programs.

## Features

- **Process management:** Start, stop and restart programs.
- **Process monitoring:** Inspect process status through the CLI.
- **Automatic startup:** Start configured programs when the daemon launches.
- **Automatic restart:** Configure restart policies and startup retry limits.
- **Configuration validation:** Load and validate YAML configuration files.
- **Logging:** Separate standard output and error logs for managed processes.
- **Interactive CLI:** Manage processes through a terminal interface.

## Requirements

- Python 3
- pip

## Installation

Clone the repository:

```bash
git clone https://github.com/Tom-Ferr/taskmaster.git
cd taskmaster
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Taskmaster uses YAML configuration files to define the programs managed by the daemon and their execution parameters.

The default configuration is located at `configs/default.yaml`.

Example:

```yaml
taskmaster:
  logfile: ./logs/taskmaster.log

programs:
  worker:
    cmd: /usr/bin/python3 worker.py
    numprocs: 1
    workingdir: ./worker
    autostart: true
    autorestart: unexpected
    exitcodes:
      - 0
    startretries: 3
    starttime: 5
    stopsignal: TERM
    stoptime: 10
    stdout: ./logs/worker.out.log
    stderr: ./logs/worker.err.log
    env:
      APP_ENV: production
```

### Global options

| Option | Description |
|---|---|
| `logfile` | Daemon log file |
| `email` | Email configuration |
| `uid` | User ID |
| `gid` | Group ID |

### Program options

Each entry under `programs` represents a managed program.

| Option | Description |
|---|---|
| `cmd` | Command used to launch the program (required) |
| `numprocs` | Number of process instances |
| `workingdir` | Program working directory |
| `autostart` | Automatically start the program with the daemon |
| `autorestart` | Restart policy: `true`, `false` or `unexpected` |
| `exitcodes` | Expected exit codes |
| `startretries` | Maximum startup retries |
| `starttime` | Startup time threshold |
| `stopsignal` | Signal used to stop the process |
| `stoptime` | Stop timeout |
| `stdout` | Standard output log file |
| `stderr` | Standard error log file |
| `env` | Environment variables |
| `umask` | File creation permission mask |

Make sure configured commands and paths are valid, and that the required working and logging directories exist.

## Usage

Taskmaster consists of two components:

- **Taskmasterd:** The daemon responsible for loading configuration and managing processes.
- **TaskmasterCLT:** The interactive command-line interface used to communicate with the daemon.

The daemon must be running before launching the CLI.

### 1. Start the daemon

Launch the daemon with a configuration file:

```bash
python3 Taskmasterd/taskmasterd.py configs/default.yaml
```

The daemon loads and validates the configuration, initializes process management and starts programs configured with `autostart: true`.

By default, the daemon runs in the background.

To run it in the foreground:

```bash
python3 Taskmasterd/taskmasterd.py configs/default.yaml --no-daemon
```

The daemon exposes its HTTP interface on `127.0.0.1:4242`.

### 2. Launch the CLI

Open another terminal and start the interactive CLI:

```bash
python3 TaskmasterCLT/taskmasterclt.py
```

The CLI communicates with the running daemon through its HTTP interface.

### 3. CLI commands

| Command | Description |
|---|---|
| `start <program>` | Start a program |
| `stop <program>` | Stop a program |
| `restart <program>` | Restart a program |
| `status` | Display process status |
| `reread <path>` | Read and validate a configuration file |
| `reload` | Reload the daemon |
| `update` | Apply configuration updates |
| `shutdown` | Shut down the daemon |
| `clear` | Clear the terminal |
| `exit` | Exit the CLI |

The CLI supports command history navigation using the arrow keys.

## Dependencies

Taskmaster relies on the following Python packages:

- [PyYAML](https://pyyaml.org/) — YAML configuration parsing.
- [Flask](https://flask.palletsprojects.com/) — HTTP interface.
- [psutil](https://psutil.readthedocs.io/) — Process and system information.
- [Requests](https://requests.readthedocs.io/) — HTTP communication between the CLI and daemon.