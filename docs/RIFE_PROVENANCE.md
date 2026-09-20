# RIFE baseline provenance

This is an optional local baseline, not this project's proposed research contribution.

| Item | Pinned identity |
| --- | --- |
| Official source | https://github.com/hzwer/ECCV2022-RIFE |
| Source commit | `5d8adbdd40e12c2c8f91930eff838aebe561c086` |
| Source license | MIT, see `LICENSE` in the pinned repository |
| Author checkpoint host | https://huggingface.co/hzwer/RIFE |
| Checkpoint revision | `19b0c859634efaf9dc63d56e7118c8c7bdfa5960` |
| Checkpoint archive | `RIFE_m_train_log.zip` (39,819,850 bytes; 38.0 MiB) |
| Download URL | https://huggingface.co/hzwer/RIFE/resolve/19b0c859634efaf9dc63d56e7118c8c7bdfa5960/RIFE_m_train_log.zip?download=true |
| Archive SHA-256 | `8cb49709fde0d53de8167273986458db1b15ff45b947a042026f1d383c99c8d7` |
| Extracted checkpoint | `RIFE_m_train_log/flownet.pkl` (42,884,324 bytes) |
| Checkpoint SHA-256 | `9f9e2e8b5c3fef311c9a782aa17a30f87c388ce6dc9c00e4993eba3d3941d3cb` |

The pinned repository's `model/RIFE.py` constructs `IFNet_m` with `Model(arbitrary=True)` and accepts `timestep` in `Model.inference`. Its `benchmark/HD_multi_4X.py` calls this model with arbitrary timestamps. The model accepts two three-channel RGB tensors, normalized to `[0, 1]`; the adapter passes each requested time `i/(N+1)` directly, for `i=1..N`. There is no power-of-two subdivision, duplication, or frame dropping. Endpoint frames come from the original uploaded images, not RIFE output.

For RGBA input, the adapter composites RGB against white for model inference and linearly interpolates alpha separately. It pads the working tensors on the right and bottom to multiples of 32 by replication. If input area exceeds 512×512 pixels, it scales down proportionally to that area budget, then restores each generated frame to the original dimensions with bicubic resizing. The manifest discloses the actual dimensions and processing. The model runs in float32; FP16 is deferred until normal-shell GPU accuracy and stability checks establish safety.

Setup uses a pinned Git checkout and checksum-verified author archive. It does not install Python packages. The checkpoint is loaded with `torch.load(..., weights_only=True)` and strict state-dict matching. Downloaded source, archive, and weights live under ignored `.local/rife/`. To reclaim the space, remove that directory: `rm -r .local/rife`.
