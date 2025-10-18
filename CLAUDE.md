# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

nvmetarget is a Python library for managing NVMe over TCP targets on Linux. It provides a programmatic interface to create and manage NVMe-oF (NVMe over Fabrics) TCP targets using the Linux kernel's configfs-based nvmet subsystem.

## Documentation

Comprehensive documentation is available:
- **README.md** - User guide with installation instructions, usage examples, and quick start
- **ARCHITECTURE.md** - Detailed technical documentation covering system design, implementation details, and design decisions
- **CHANGELOG.md** - Complete project history with version changes and migration guides

## Build and Development Commands

### Build and Install
```bash
./build.sh
```
Builds a wheel package and force-reinstalls it locally. The build process:
- Removes existing dist files
- Builds wheel using `python -m build --wheel`
- Force-reinstalls the package with pip

### Testing
```bash
./test.sh
```
Full integration test that:
1. Rebuilds and reinstalls the package
2. Cleans up existing nvmet configuration
3. Runs the test suite (`tests/test_nvmelib.py`)
4. Tests NVMe discovery and connection using `nvme-cli`
5. Connects to created subsystems and lists devices

**Note**: test.sh is hardcoded to IP address `192.168.1.51` and expects the nvme-cli tools to be installed.

### Cleanup
```bash
./cleanup.sh
```
Removes nvmet configuration from `/sys/kernel/config/nvmet/` and deletes `/etc/nvmetarget.json`.

### Status Check
```bash
./status.sh
```
Tests NVMe discovery and connects to a storage subsystem for verification.

## Architecture

### Core Components

**NvmeTarget class** (`nvmetarget/nvmelib.py`):
The main interface for managing NVMe targets. Key responsibilities:
- Loads the `nvmet_tcp` kernel module on initialization
- Manages subsystems via `/sys/kernel/config/nvmet/`
- Creates loop devices for backing storage
- Tracks configuration in `/etc/nvmetarget.json` using pysondb

### NVMe Target Hierarchy

The library manages a three-level hierarchy:
1. **Subsystems**: NVMe subsystems (created via `subsystem()` method)
2. **Namespaces**: Namespaces within subsystems (created via `namespace()` method)
3. **Ports**: TCP ports for NVMe-oF access (automatically created on port 4420)

Recent architecture change (per git history): The system now uses **one namespace per subsystem** instead of multiple namespaces per subsystem. Each subsystem gets a unique serial number derived from the backing file's basename.

### Key Design Patterns

**configfs interaction**: All NVMe target management happens through the Linux kernel's configfs filesystem mounted at `/sys/kernel/config/nvmet/`. The library writes to specific files in this hierarchy to configure targets.

**Loop device management**: Backing storage files are attached to loop devices using `losetup`. The library auto-discovers free loop devices and creates sparse files for efficient storage.

**Persistent state**: Configuration is stored in `/etc/nvmetarget.json` (requires root) and user state in `~/.nvmetarget/` (subsystem, namespace counters).

### Important File Paths

- `/sys/kernel/config/nvmet/` - Kernel configfs interface for nvmet
- `/etc/nvmetarget.json` - Persistent database of created targets
- `~/.nvmetarget/subsystem` - Current subsystem name
- `~/.nvmetarget/namespace` - Namespace counter file
- `/etc/nvmetarget.namespace` - Global namespace counter

## Version Management

The project uses `setuptools_scm` for automatic versioning from git tags. Version is written to `nvmetarget/_version.py` during build.

## Testing Notes

The test file `tests/test_nvmelib.py` creates 19 subsystems (storage1-storage19) each with one namespace and a 10 MB backing file. This tests the multi-subsystem architecture.

Testing requires root privileges due to:
- Loading kernel modules
- Writing to `/sys/kernel/config/`
- Creating loop devices
- Writing to `/etc/nvmetarget.json`

## Dependencies

Runtime dependencies:
- `pysondb` - JSON-based database for target configuration
- `nvme-cli` - NVMe command line tools (for testing/verification)
- Linux kernel with nvmet_tcp module

The kernel module `nvmet_tcp` must be available and the kernel must be compiled with NVMe target support.
