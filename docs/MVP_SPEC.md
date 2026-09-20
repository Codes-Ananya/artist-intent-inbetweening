# Milestone 1 MVP specification

The local Gradio app accepts two PNG keyframes with matching dimensions and RGB or RGBA mode, 0–120 intermediate frames, and 1–60 FPS. It rejects unreadable files, other formats, mismatched dimensions, mismatched color mode, and mismatched alpha presence. The deterministic placeholder linearly blends channel values with integer rounding. Original endpoints occupy the first and last frame.

A run saves ordered PNG files, an animated GIF, an H.264 MP4, a JSON manifest, and JSONL events in a unique `outputs/<run-id>/` folder. The UI shows a timeline gallery, selected frame, animated preview, downloads, and diagnostics. No model weights or network inference are used.
