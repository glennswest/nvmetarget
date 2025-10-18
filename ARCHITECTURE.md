# Architecture Documentation

## Table of Contents
- [System Overview](#system-overview)
- [NVMe-oF Background](#nvme-of-background)
- [Component Architecture](#component-architecture)
- [Linux Kernel Integration](#linux-kernel-integration)
- [Class Design](#class-design)
- [State Management](#state-management)
- [Configuration Flow](#configuration-flow)
- [Data Structures](#data-structures)
- [Storage Backend](#storage-backend)
- [Network Architecture](#network-architecture)
- [Design Decisions](#design-decisions)
- [Security Considerations](#security-considerations)
- [Limitations](#limitations)
- [Future Enhancements](#future-enhancements)

## System Overview

nvmetarget is a Python abstraction layer over the Linux kernel's NVMe Target subsystem (nvmet). It provides programmatic control over NVMe-oF TCP targets without requiring direct manipulation of the kernel's configfs interface.

### High-Level Architecture

```
┌─────────────────────────────────────────────┐
│         User Application (Python)           │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│         NvmeTarget Class                    │
│  - subsystem()                              │
│  - namespace()                              │
│  - targets()                                │
└─────────────────┬───────────────────────────┘
                  │
         ┌────────┴─────────┐
         │                  │
┌────────▼──────┐  ┌────────▼──────────┐
│  configfs     │  │  pysondb          │
│  Interface    │  │  (JSON DB)        │
└────────┬──────┘  └───────────────────┘
         │
┌────────▼──────────────────────────────────┐
│  Linux Kernel nvmet Subsystem             │
│  /sys/kernel/config/nvmet/                │
└────────┬──────────────────────────────────┘
         │
┌────────▼──────────────────────────────────┐
│  Loop Devices + Backing Files             │
└───────────────────────────────────────────┘
```

## NVMe-oF Background

### What is NVMe-oF?

NVMe over Fabrics (NVMe-oF) extends the NVMe protocol beyond local PCIe connections to network fabrics. This library specifically implements NVMe over TCP, which allows:

- Block-level storage access over standard TCP/IP networks
- High performance, low latency storage access
- Standard Ethernet infrastructure (no special hardware required)

### Protocol Layers

```
Application Layer:    NVMe Commands (Read, Write, etc.)
Transport Layer:      NVMe/TCP
Network Layer:        TCP/IP
```

### Target vs Initiator

- **Target** (Server): Exports storage devices - what this library creates
- **Initiator** (Client): Connects to and uses the exported devices - uses nvme-cli

## Component Architecture

### Core Components

```
NvmeTarget
├── Configuration Manager
│   ├── configfs Writer (echo/read methods)
│   └── Database Manager (pysondb)
├── Storage Backend
│   ├── Loop Device Allocator
│   └── Sparse File Creator
├── Network Setup
│   └── IP Detection
└── Subsystem Hierarchy Manager
    ├── Subsystem Creator
    ├── Namespace Manager
    └── Port Configurator
```

## Linux Kernel Integration

### configfs Interface

The Linux nvmet driver exposes its configuration through configfs, a virtual filesystem for kernel object configuration. The hierarchy is:

```
/sys/kernel/config/nvmet/
├── subsystems/
│   └── <subsystem_name>/
│       ├── attr_allow_any_host       # Security setting
│       ├── attr_serial                # Subsystem serial number
│       └── namespaces/
│           └── <namespace_id>/
│               ├── device_path        # Backend device (loop device)
│               └── enable             # Activation flag
└── ports/
    └── <port_id>/
        ├── addr_adrfam                # Address family (ipv4/ipv6)
        ├── addr_trtype                # Transport type (tcp)
        ├── addr_traddr                # IP address to bind
        ├── addr_trsvcid               # Port number
        └── subsystems/
            └── <subsystem_name>       # Symlink to subsystem
```

### Directory Operations

- **Creating objects**: `mkdir` in configfs creates kernel objects
- **Setting attributes**: Write to special files (via `echo` wrapper)
- **Linking subsystems to ports**: Symbolic links in configfs
- **Activating namespaces**: Write '1' to `enable` file

## Class Design

### NvmeTarget Class

Location: `nvmetarget/nvmelib.py`

#### Initialization (`__init__`)

```python
def __init__(self):
    # 1. Load kernel module
    os.system("modprobe nvmet_tcp")

    # 2. Setup directories
    self.home_dir = os.path.expanduser('~/.nvmetarget')
    os.makedirs(self.home_dir, exist_ok=True)

    # 3. Initialize database
    self.target_db = getDb('/etc/nvmetarget.json')

    # 4. Detect IP
    self.ip = self.get_ip()
```

#### Key Methods

**1. `subsystem(thename)`**

Creates an NVMe subsystem in configfs:
- Creates directory at `/sys/kernel/config/nvmet/subsystems/<name>/`
- Sets `attr_allow_any_host` to '1' (allows any NVMe initiator to connect)
- Stores subsystem name in `~/.nvmetarget/subsystem`

**2. `namespace(thename, thefile, thesize)`**

Most complex operation, creates a namespace and connects it to storage:

```
1. Read current subsystem name
2. Extract serial number from filename
3. Set subsystem serial number
4. Auto-generate namespace ID if empty
5. Create namespace directory in configfs
6. Allocate loop device
7. Create sparse backing file if needed
8. Attach file to loop device (losetup)
9. Set device_path to loop device
10. Enable the namespace
11. Create/update port configuration
12. Link subsystem to port
13. Store metadata in database
```

**3. `targets()`**

Returns all configured targets from the JSON database.

#### Helper Methods

**`get_ip()`**: UDP socket trick to find primary network interface IP
**`run_command()`**: Execute shell commands and capture output
**`get_loop_device()`**: Find next available loop device
**`parse_size()`**: Convert human-readable sizes to bytes
**`echo()`**: Write string to file (configfs attribute setter)
**`read()`**: Read string from file (configfs attribute getter)
**`create_thin_image()`**: Create sparse/thin-provisioned disk image

## State Management

### Persistent State (Survives Reboots)

**Location**: `/etc/nvmetarget.json` (requires root)

**Schema**:
```json
{
  "data": [
    {
      "namespace": "1",
      "subsystem": "storage1",
      "device": "/dev/loop0",
      "file": "/path/to/backing.img",
      "size": "10 GB",
      "active": "True",
      "id": 123456789
    }
  ]
}
```

### Ephemeral State (Session-based)

**Location**: `~/.nvmetarget/`

Files:
- `subsystem`: Last used subsystem name
- `namespace`: Namespace counter for current session

**Location**: `/etc/nvmetarget.namespace`
- Global namespace counter (persists)

### Kernel State (configfs)

Lives in memory, does NOT persist across reboots. The configfs hierarchy must be rebuilt after reboot using the JSON database.

## Configuration Flow

### Creating a Complete NVMe Target

```
User Code
    │
    ├─► subsystem('storage1')
    │       │
    │       ├─► mkdir /sys/kernel/config/nvmet/subsystems/storage1/
    │       └─► echo '1' > .../subsystems/storage1/attr_allow_any_host
    │
    └─► namespace('1', 'disk.img', '10 GB')
            │
            ├─► Extract serial from filename → 'disk'
            ├─► echo 'disk' > .../storage1/attr_serial
            ├─► mkdir .../subsystems/storage1/namespaces/1/
            ├─► losetup -f → /dev/loop0
            ├─► Create sparse file if needed
            ├─► losetup /dev/loop0 disk.img
            ├─► echo '/dev/loop0' > .../namespaces/1/device_path
            ├─► echo '1' > .../namespaces/1/enable
            ├─► Configure port 1 (if not exists)
            │       ├─► mkdir /sys/kernel/config/nvmet/ports/1/
            │       ├─► echo 'ipv4' > .../ports/1/addr_adrfam
            │       ├─► echo 'tcp' > .../ports/1/addr_trtype
            │       ├─► echo '4420' > .../ports/1/addr_trsvcid
            │       └─► echo '<ip>' > .../ports/1/addr_traddr
            ├─► Symlink subsystem to port
            │       └─► ln -s /sys/kernel/config/nvmet/subsystems/storage1/ \
            │                 /sys/kernel/config/nvmet/ports/1/subsystems/storage1
            └─► Save to database
                    └─► pysondb.add({...})
```

## Data Structures

### Database Entry

Each namespace gets an entry in the JSON database:

```python
{
    "namespace": str,      # Namespace ID within subsystem
    "subsystem": str,      # Subsystem name
    "device": str,         # Loop device path (e.g., /dev/loop0)
    "file": str,           # Backing file path
    "size": str,           # Human-readable size
    "active": str,         # "True" or "False"
    "id": int              # Auto-generated by pysondb
}
```

### Subsystem-Namespace Relationship

**Current Architecture** (post git commit f56d562):
- **One namespace per subsystem**
- Each subsystem has a unique serial number
- Serial number derived from backing file's basename

**Example**:
```
Subsystem: storage1
  └─ Serial: disk1 (from disk1.img)
  └─ Namespace: 1
      └─ Device: /dev/loop0 → disk1.img
```

## Storage Backend

### Loop Devices

Loop devices (`/dev/loopN`) allow regular files to be accessed as block devices. The library:

1. Finds free loop device: `losetup -f`
2. Attaches file to loop device: `losetup /dev/loopN /path/to/file`
3. Uses loop device as NVMe namespace backend

### Sparse File Creation

The `create_thin_image()` method creates sparse (thin-provisioned) files:

```python
def create_thin_image(self, thefile, thesize):
    size_in_bytes = self.parse_size(thesize) - 512
    fd = os.open(thefile, os.O_RDWR+os.O_CREAT)
    os.lseek(fd, size_in_bytes, os.SEEK_SET)  # Seek to end
    sector = bytearray(512)                    # Write one sector
    os.write(fd, sector)
    os.close(fd)
```

This creates a file that appears to be `thesize` bytes but only consumes actual disk space for written data.

**Advantages**:
- Instant "allocation" of large volumes
- Saves disk space
- Grows as data is written

**Considerations**:
- Can lead to overprovisioning
- Filesystem must support sparse files (ext4, xfs, btrfs do)

## Network Architecture

### Port Configuration

Currently hardcoded to single port:
- **Port ID**: 1
- **Protocol**: TCP
- **Port Number**: 4420
- **IP Address**: Auto-detected from primary interface

### IP Detection Algorithm

```python
def get_ip(self):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(('10.254.254.254', 1))  # Doesn't need to be reachable
        IP = s.getsockname()[0]            # Gets source IP that would be used
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP
```

This clever technique finds the default route's interface IP without actually sending packets.

### Multi-Subsystem Port Sharing

All subsystems share port 1. The port is created once and subsystems are linked to it via symbolic links in configfs.

## Design Decisions

### One Namespace Per Subsystem

**Rationale** (from git history):
- Simpler client-side management
- Each subsystem acts as a single logical drive
- Serial numbers uniquely identify each subsystem
- Clearer separation of storage resources

**Previous design**: Multiple namespaces per subsystem
**Current design**: One namespace per subsystem (commit f56d562)

### Root-Level Database

**Location**: `/etc/nvmetarget.json`

**Why**:
- Requires root anyway for configfs operations
- Global state accessible to all users/scripts
- Survives user session changes

**Trade-off**: Requires root for all operations

### configfs Over ioctl/netlink

**Why configfs**:
- Easier to understand and debug (filesystem operations)
- Human-readable and scriptable
- Official kernel interface for nvmet
- No need for custom kernel modules or ioctl definitions

**Trade-off**: Slower than binary interfaces, but acceptable for setup operations

### Single TCP Port (4420)

**Why**:
- Simplifies configuration
- Standard NVMe-oF TCP port
- All subsystems accessible through one port
- Discovery service works as expected

### pysondb for Persistence

**Why**:
- Simple JSON-based storage
- No external database server needed
- Built-in querying capabilities
- Lightweight

**Trade-off**: Not suitable for high-concurrency scenarios, but fine for this use case

## Security Considerations

### Root Privileges Required

All operations require root because:
- Loading kernel modules (`modprobe nvmet_tcp`)
- Writing to `/sys/kernel/config/`
- Creating loop devices
- Writing to `/etc/`

### attr_allow_any_host

Currently set to '1', meaning any NVMe initiator can connect without authentication.

**Security implications**:
- No access control at NVMe protocol level
- Rely on network security (firewalls, VLANs)
- Suitable for trusted networks only

**Hardening options** (not currently implemented):
- Host-based ACLs in configfs
- Network-level firewalls
- TLS-secured NVMe-oF (requires different transport)

### File Permissions

Backing files inherit system umask. Consider:
- Setting restrictive permissions on backing files
- Using dedicated filesystems or directories
- Implementing quota systems

## Limitations

### Current Limitations

1. **Single Port**: Only port 1 on TCP 4420
2. **No ACLs**: All hosts can connect (attr_allow_any_host=1)
3. **No IPv6**: Currently only IPv4 support
4. **No Persistence Across Reboots**: configfs state lost on reboot
5. **No Cleanup on Errors**: Partial configurations may remain
6. **Hardcoded IP in Tests**: test.sh uses 192.168.1.51
7. **No RDMA**: Only TCP transport supported
8. **Limited Error Handling**: Minimal validation and error messages

### Architectural Limitations

1. **Loop Device Dependency**: Performance overhead vs direct device access
2. **Sparse File Overprovisioning**: No checks for actual disk space
3. **No Snapshot Support**: Backing files are raw, no built-in snapshots
4. **No Multi-Path**: Single path per namespace

## Future Enhancements

### Potential Improvements

1. **Multi-Port Support**: Allow configuring multiple IP:port combinations
2. **Host ACLs**: Implement per-subsystem host access controls
3. **IPv6 Support**: Add dual-stack networking
4. **Persistence Service**: Systemd service to restore configuration on boot
5. **Error Recovery**: Rollback mechanisms for failed configurations
6. **Direct Device Support**: Allow block devices (not just files) as backends
7. **RDMA Transport**: Support NVMe over RDMA for higher performance
8. **Resource Limits**: Enforce QoS and resource quotas
9. **Monitoring**: Export metrics via Prometheus or similar
10. **Hot-Plug**: Dynamic addition/removal without service disruption
11. **Namespace Snapshots**: Integration with LVM or btrfs snapshots
12. **Configuration Validation**: Pre-flight checks before applying changes

### Code Quality Improvements

1. **Type Hints**: Add Python type annotations
2. **Exception Handling**: Proper exception hierarchy and handling
3. **Logging**: Replace print statements with proper logging
4. **Unit Tests**: Add unit tests (currently only integration tests)
5. **Documentation**: Add docstrings to all methods
6. **Configuration File**: YAML/TOML config instead of hardcoded values

## References

### External Documentation

- [Linux Kernel NVMe Target Documentation](https://www.kernel.org/doc/html/latest/nvme/nvme-target.html)
- [NVMe over Fabrics Specification](https://nvmexpress.org/specifications/)
- [Experimenting with NVMe over TCP](https://jing.rocks/2023/06/13/Experimenting-with-NVMe-over-TCP.html) - Original inspiration

### Related Technologies

- **nvmet**: Linux kernel NVMe target subsystem
- **nvme-cli**: NVMe management command line interface
- **configfs**: Kernel configuration filesystem
- **Loop devices**: Block device abstraction over files

---

This architecture document is maintained alongside the code. For questions or suggestions, contact Glenn West at glennswest@neuralcloudcomputing.com.
