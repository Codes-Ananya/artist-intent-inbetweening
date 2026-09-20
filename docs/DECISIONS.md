# Decisions

1. PNG is the accepted input to make channel and alpha validation explicit and keep endpoints pixel-exact.
2. Integer channel crossfade is a deterministic placeholder. It does not estimate motion or preserve line structure.
3. PNG sequence is authoritative for endpoint fidelity. GIF and MP4 are viewing formats with color/alpha limitations.
4. The app listens on loopback only and stores local run folders under ignored `outputs/`.
5. The backend interface permits a future RIFE implementation without changing run orchestration or UI.
