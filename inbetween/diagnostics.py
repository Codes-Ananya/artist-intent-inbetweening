"""Best-effort local system diagnostics."""
import importlib
import importlib.util
import platform
import shutil
import subprocess
import sys


def collect() -> dict:
    data = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "ffmpeg": shutil.which("ffmpeg"),
        "torch_installed": importlib.util.find_spec("torch") is not None,
        "torch_version": None,
        "cuda_available": None,
        "cuda_devices": [],
        "cuda_probe_error": None,
        "nvidia_smi_available": False,
        "nvidia_smi_output": None,
        "nvidia_smi_error": None,
    }
    if data["torch_installed"]:
        try:
            torch = importlib.import_module("torch")
            data["torch_version"] = torch.__version__
            data["cuda_available"] = bool(torch.cuda.is_available())
            if data["cuda_available"]:
                data["cuda_devices"] = [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())]
        except Exception as exc:
            data["cuda_probe_error"] = str(exc)
    data["nvidia_smi_available"] = bool(shutil.which("nvidia-smi"))
    if data["nvidia_smi_available"]:
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0:
                data["nvidia_smi_output"] = result.stdout.strip()
            else:
                data["nvidia_smi_error"] = result.stderr.strip() or f"exit code {result.returncode}"
        except (OSError, subprocess.TimeoutExpired) as exc:
            data["nvidia_smi_error"] = str(exc)
    return data
