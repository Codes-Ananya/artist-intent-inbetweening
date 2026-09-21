"""Keep normal pytest independent of installed GPU model assets."""
import importlib
import pytest


@pytest.fixture(autouse=True)
def prohibit_real_rife_model_import(monkeypatch):
    original = importlib.import_module

    def guarded(name, *args, **kwargs):
        if name == 'model.RIFE':
            raise AssertionError('Real RIFE inference is forbidden in pytest; inject a fake backend/model')
        return original(name, *args, **kwargs)

    # Existing mocked OOM coverage supplies its own fake module explicitly.
    monkeypatch.setattr(importlib, 'import_module', guarded)
