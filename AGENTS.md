# Repository guidance

Use the existing `.venv` and keep execution local. Do not add cloud services, model downloads, or paid APIs. Keep interpolation behind `InterpolationBackend` so a later RIFE backend can be added. Treat uploaded endpoint pixels as immutable. Never commit generated runs, weights, credentials, or the virtual environment. Run pytest and a sample export before committing.
