from types import SimpleNamespace
from inbetween import diagnostics


def setup_probes(monkeypatch, torch_present, smi_present=False):
    monkeypatch.setattr(diagnostics.importlib.util, "find_spec", lambda name: object() if torch_present else None)
    monkeypatch.setattr(diagnostics.shutil, "which", lambda name: "/usr/bin/" + name if name == "ffmpeg" or (name == "nvidia-smi" and smi_present) else None)


def test_missing_torch_does_not_claim_cuda_absent(monkeypatch):
    setup_probes(monkeypatch, False)
    result = diagnostics.collect()
    assert result["torch_installed"] is False
    assert result["torch_version"] is None
    assert result["cuda_available"] is None
    assert result["cuda_probe_error"] is None
    assert result["nvidia_smi_available"] is False


def test_cuda_available_and_nvidia_smi(monkeypatch):
    setup_probes(monkeypatch, True, True)
    fake = SimpleNamespace(__version__="2.14.0+cu126", cuda=SimpleNamespace(is_available=lambda: True, device_count=lambda: 1, get_device_name=lambda _: "RTX 4050 Laptop GPU"))
    monkeypatch.setattr(diagnostics.importlib, "import_module", lambda name: fake)
    monkeypatch.setattr(diagnostics.subprocess, "run", lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout="RTX 4050 Laptop GPU, 6144 MiB, driver\n", stderr=""))
    result = diagnostics.collect()
    assert result["torch_installed"] is True
    assert result["torch_version"] == "2.14.0+cu126"
    assert result["cuda_available"] is True
    assert result["cuda_devices"] == ["RTX 4050 Laptop GPU"]
    assert result["nvidia_smi_available"] is True
    assert "6144 MiB" in result["nvidia_smi_output"]


def test_cuda_probe_error_is_distinct_from_cuda_unavailable(monkeypatch):
    setup_probes(monkeypatch, True)
    def fail(name):
        raise RuntimeError("probe blocked")
    monkeypatch.setattr(diagnostics.importlib, "import_module", fail)
    result = diagnostics.collect()
    assert result["torch_installed"] is True
    assert result["cuda_available"] is None
    assert result["cuda_probe_error"] == "probe blocked"


def test_cuda_unavailable_and_failed_nvidia_smi(monkeypatch):
    setup_probes(monkeypatch, True, True)
    fake = SimpleNamespace(__version__="2.14.0+cu126", cuda=SimpleNamespace(is_available=lambda: False))
    monkeypatch.setattr(diagnostics.importlib, "import_module", lambda name: fake)
    monkeypatch.setattr(diagnostics.subprocess, "run", lambda *args, **kwargs: SimpleNamespace(returncode=1, stdout="", stderr="driver blocked"))
    result = diagnostics.collect()
    assert result["cuda_available"] is False
    assert result["nvidia_smi_available"] is True
    assert result["nvidia_smi_error"] == "driver blocked"
