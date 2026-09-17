# Glacier Fall Simulation

Physics-based glacier ice-rock fall simulation using PyChrono, with analytical validation.

## Overview

Simulates a block sliding down a sloped surface, hitting an obstacle, and validates the results against analytical physics solutions. Designed for supercomputer deployment (SCNet) but can be adapted for local execution.

## Requirements

- Python 3.8+
- NumPy
- **Project Chrono** (PyChrono bindings) — compiled from source
- SCNet supercomputer environment (for default paths)

## Quick Start

### On SCNet (Supercomputer)

```bash
# Enter GPU container first
ssh -p 9999 -i ~/.ssh/id_ed25519_overseas -o StrictHostKeyChecking=no root@localhost

# Run simulation
cd /work/home/scnxak5p9h/glacier_fall
python scripts/simulation.py
```

### Local / Other Environments

**Note**: This script uses hardcoded paths for SCNet. To run elsewhere:

1. Edit `scripts/simulation.py`:
   - Change `sys.path.insert(0, '/root/private_data/chrono/build-py311/bin')` to your PyChrono path
   - Change `CONFIG_PATH` to `./config/parameters.json`
   - Change `OUTPUT_DIR` and `LOG_DIR` to relative paths

2. Install PyChrono:
```bash
# Requires Project Chrono compiled with Python bindings
# See: https://api.projectchrono.org/deployment_workflow.html
```

3. Run:
```bash
python scripts/simulation.py
```

## Project Structure

```
glacier_fall/
├── config/
│   └── parameters.json         # Simulation parameters (mass, angle, friction, etc.)
├── scripts/
│   └── simulation.py           # Main simulation script
├── output/
│   ├── result.json             # Final simulation state
│   ├── analytical_baseline.json # Analytical solution for comparison
│   ├── time_series.csv         # Full trajectory data
│   └── collision_minimal_results.json
├── tests/
│   ├── test_exact_unit.py      # Unit tests
│   ├── test_collision_minimal.py
│   └── ...
├── validation/
│   └── validate.py             # Compare simulation vs analytical
└── logs/
    └── simulation.log          # Execution log
```

## Output Files

| File | Description |
|------|-------------|
| `result.json` | Final time, position, velocity, contact detection |
| `analytical_baseline.json` | Expected values from physics formulas |
| `time_series.csv` | Per-step trajectory (position, velocity, contacts, forces) |

## Key Parameters (`config/parameters.json`)

| Parameter | Description |
|-----------|-------------|
| `gravity` | Gravitational acceleration (m/s²) |
| `slope_angle` | Slope angle in degrees |
| `friction` | Friction coefficient |
| `mass` | Block mass (kg) |
| `height` | Initial height (m) |
| `slope_length` | Slope length (m) |
| `obstacle_x/y` | Obstacle position |

## Validation

```bash
python validation/validate.py
```

Compares simulation output against analytical baseline and reports error margins.

## Known Limitations

- **Hardcoded paths**: Default configuration assumes SCNet supercomputer environment
- **PyChrono dependency**: Requires compiled C++ library, not pip-installable
- **No GPU acceleration**: Runs on CPU; PyChrono GPU support requires additional setup

## License

MIT License
