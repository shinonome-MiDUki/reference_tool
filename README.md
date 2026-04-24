# OXORIA

OXORIA is a next-generation reference image management software designed for digital creators, concept artists, and 3D modelers. Unlike traditional reference tools that act as simple infinite canvases, OXORIA introduces structured memory, semantic search, and state-versioning to streamline the creative workflow.

## Key Features

### 1 Intelligent Image Memory

- Unique Asset Management: Uses pixel-based hash comparison to prevent duplicate imports.

- Pointer-Based System: Each image is stored as a unique entity (ID). Multiple canvases point to the same asset, ensuring zero redundant data.

- Semantic Search: Powered by a Vector Database. Find images using natural language (e.g., searching "cat" will find images tagged with "cats" or "kitty").

- Global Inbox: Collect images daily with personal memos, even if you aren't working on a specific project yet.

### 2 Versatile Viewing Modes

- Canvas Mode: A traditional free-form space. Use Ctrl+J and type a group name to instantly jump to specific clusters.

- Tile Mode: Automatically organizes groups into a structured grid layout inspired by the River tiling compositor for Linux.

- Dual Perspective: Effortlessly view different parts of your workspace simultaneously.

### 3 Dynamic Classification

- Contextual Switching: Toggle between different classification layouts for the same set of images.

- Example: Switch from "Pose-based" grouping during the sketching phase to "Color-based" grouping during the painting phase.

### 4 3D Reference Support

- OBJ Previewer: Integrated OpenGL-based viewer for 3D models. Reference 3D silhouettes and forms alongside 2D images in the same workspace.

### 5 UI as Data & Version Control

- Embedded Git: OXORIA integrates Git to track the state of your UI.

- Layout Snapshots: Easily revert to yesterday's specific window arrangement or image positioning. The file defines the UI, not just the content.

- Backwards Compatibility: The file format focuses on pointers and layout definitions, ensuring stability as the software evolves.

### 6 Resolution Independence

- Visual-First Sizing: By default, images are sized based on screen pixels and aspect ratios rather than raw file resolution, ensuring a consistent visual scale across your workspace.

### 7 Extensibility & Automation

- Python API: Every UI operation is mapped to a Python function.

- Scripting: Automate your workflow or build custom extensions using the public Python API.

### 8 System Integration

- OS-Level Shortcuts: Capture and import screenshots directly into OXORIA with a single global hotkey.

## Open Source

OXORIA is proud to be open-source, released under the Apache License 2.0. We believe in empowering the creative community through transparency and collaboration.

## License

Distributed under the Apache License 2.0. See LICENSE for more information.