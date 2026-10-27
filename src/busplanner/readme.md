# Busplanner

Install the package from the repository root in editable mode:

```powershell
python -m pip install -e .
```

After installation, import modules with their absolute package names:

```python
from busplanner.calculations.power import energy_levels
from busplanner.calculations.checker.errors import overlaps
```

Modules inside `busplanner` use relative imports to refer to sibling modules.
For example, `calculations/imports.py` imports `power` as
`from .power import powerpertrip`.

To run the checker test, use the package module command from the repository
root:

```powershell
python -m busplanner.calculations.checker.test
```

You can also run `src/busplanner/calculations/checker/test.py` directly after
installing the package in the selected Python environment.