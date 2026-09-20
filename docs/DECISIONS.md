# Decisions

1. PNG is the accepted input to make channel and alpha validation explicit and keep endpoints pixel-exact.
2. Integer channel crossfade is a deterministic placeholder. It does not estimate motion or preserve line structure.
3. PNG sequence is authoritative for endpoint fidelity. GIF and MP4 are viewing formats with color/alpha limitations.
4. The app listens on loopback only and stores local run folders under ignored `outputs/`.
5. The backend interface permits a future RIFE implementation without changing run orchestration or UI.

6. Uploaded file paths are trusted only under the loopback-only Gradio deployment assumption. The API also accepts programmatic sample paths and valid Gradio temporary paths. Do not expose this app as a public service without revisiting path trust.
