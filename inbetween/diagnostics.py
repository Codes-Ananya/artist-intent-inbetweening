"""Best-effort local system diagnostics."""
import platform
import shutil
import subprocess
import sys


def collect() -> dict:
    data = {"python": sys.version.split()[0], "platform": platform.platform(), "ffmpeg": shutil.which("ffmpeg")}
    try:
        import torch
        data["torch"] = torch.__version__
        data["cuda_available"] = torch.cuda.is_available()
        data["cuda_devices"] = [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())] if data["cuda_available"] else []
    except Exception as exc:
        data["cuda_available"] = False
        data["cuda_error"] = str(exc)
    try:
        result = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"], capture_output=True, text=True, timeout=5)
        data["nvidia_smi"] = result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        data["nvidia_smi"] = str(exc)
    return data
