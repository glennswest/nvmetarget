# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive README.md with installation, usage examples, and configuration
- Detailed ARCHITECTURE.md documentation covering system design and implementation
- CLAUDE.md for AI-assisted development guidance
- This CHANGELOG.md to track project history

## [0.1.0] - 2025-03-28

### Changed
- **[BREAKING]** Refactored architecture to use one namespace per subsystem (commit f968110)
  - Previously supported multiple namespaces per subsystem
  - Now each subsystem contains exactly one namespace
  - Simplifies client-side management and resource organization
- Cleaned up test script for better readability (commit 877f0b6)

### Fixed
- Removed unnecessary debug output (commit 397cab5)

## [0.0.9] - 2025-03-22

### Added
- Serial number support for NVMe subsystems (commit 2ac6a15, f56d562)
  - Each subsystem now has a unique serial number
  - Serial number derived from backing file's basename
  - Enables better device identification on client side

### Changed
- Improved gitignore configuration (commit f8f1bc7)

### Fixed
- Serial number implementation now working correctly with subsystem per drive model

## [0.0.8] - 2025-03-21

### Added
- Automatic versioning using setuptools_scm (commit 8890837)
- Support for multiple devices/exports (commit fba1bb4)

### Changed
- Port creation moved to namespace level from subsystem level (commit fd50c01)
  - Port created once per subsystem/system
  - Ensures drive attachment before port configuration
- Refactored port and symlink creation logic (commit cc2c749)

### Fixed
- Loop device allocation and management (commit d46ac41)
- Capacity calculation now uses correct power of 2 units (commit 56e3c26)
  - Fixed size parsing for KB, MB, GB, TB units
- Temporary removal of serial number to resolve multi-device issues (commit f3b595f)

## [0.0.5] - 2025-03-20

### Added
- NVMe discovery testing in test script (commit 6fd1451)
- Test script with discovery and connection verification

### Fixed
- First working version with single device/export (commit 35e251f)
- Note: Multiple device support was broken at this point

## [0.0.1] - 2025-03-20

### Added
- Initial project structure and base implementation (commit 183d413)
- Core `NvmeTarget` class with subsystem and namespace management
- Integration with Linux kernel nvmet subsystem via configfs
- Loop device management for backing storage
- Sparse file creation for thin provisioning
- IP address auto-detection for network binding
- Persistent configuration storage using pysondb
- Build script (build.sh) for package creation
- Test script (test.sh) for integration testing
- Cleanup script (cleanup.sh) for nvmet configuration removal
- Status script (status.sh) for verification
- Basic gitignore configuration
- Python package structure with setup.py and pyproject.toml

### Development Progress
- March 20, 07:22: Initial base commit
- March 20, 09:48: Work in progress on core functionality
- March 20, 12:55: Code complete, testing phase begins
- March 20, 14:11: Testing in progress
- March 20, 17:20-17:57: Updates and refinements
- March 20, 18:51: Subsystem functionality passes tests
- March 20, 22:52: First working version achieved (single device)

## Development Timeline

### March 2025 - Project Evolution

**Week of March 20-22**: Rapid initial development
- Day 1 (Mar 20): Initial implementation and first working single-device version
- Day 2 (Mar 21): Multi-device support, versioning, loop device fixes
- Day 3 (Mar 22): Serial number implementation and refinement

**Week of March 23-28**: Architecture refinement
- Mar 23: Major architecture change to one namespace per subsystem
- Mar 28: Code cleanup and documentation

## Key Milestones

1. **Initial Release** (March 20, 2025)
   - Basic NVMe target creation functionality
   - Single device export working

2. **Multi-Device Support** (March 21, 2025)
   - Support for multiple NVMe devices
   - Proper loop device management
   - Automatic versioning

3. **Serial Number Support** (March 22, 2025)
   - Unique identification for each subsystem
   - Better client-side device recognition

4. **Architecture Refinement** (March 23, 2025)
   - One namespace per subsystem model
   - Simplified and more robust design

5. **Documentation Release** (October 18, 2025)
   - Comprehensive README and ARCHITECTURE documentation
   - Developer guidance and change history

## Migration Guide

### Upgrading to 0.1.0 (One Namespace Per Subsystem)

If you were using the library before commit f968110 (March 23, 2025):

**Old approach** (multiple namespaces per subsystem):
```python
target.subsystem('storage')
target.namespace('1', 'disk1.img', '10 GB')
target.namespace('2', 'disk2.img', '10 GB')
# Both namespaces in 'storage' subsystem
```

**New approach** (one namespace per subsystem):
```python
target.subsystem('storage1')
target.namespace('1', 'disk1.img', '10 GB')

target.subsystem('storage2')
target.namespace('2', 'disk2.img', '10 GB')
# Each namespace in its own subsystem
```

**Benefits of new approach**:
- Clearer logical separation
- Easier client-side management
- Unique serial numbers per subsystem
- Better isolation between storage resources

## Notes

- All development commits by Glenn West (gwest)
- Project inspired by [Experimenting with NVMe over TCP](https://jing.rocks/2023/06/13/Experimenting-with-NVMe-over-TCP.html)
- Requires Linux kernel with nvmet_tcp support
- All operations require root privileges

## Future Plans

See [ARCHITECTURE.md](ARCHITECTURE.md#future-enhancements) for planned improvements including:
- Multi-port support
- Host-based ACLs
- IPv6 support
- Persistence service for reboot recovery
- RDMA transport support
- Enhanced error handling and validation

---

For more information, see:
- [README.md](README.md) - User guide and quick start
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical design documentation
- [GitHub Repository](https://github.com/glennswest/nvmetarget)
