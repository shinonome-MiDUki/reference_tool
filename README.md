# Oxoria 🎨

> A modern, open-source reference management tool for artists and 3D creators.

![OXORIA](src/oxoria/_resources/assets/initial_image.jpg)
---

## What is Oxoria?

Oxoria is a feature-rich reference management tool designed for digital artists and 3D creators. Whether you're painting, illustrating, or modelling in 3D, Oxoria helps you collect, organize, and retrieve your visual references — all in one place.

> **Try it now:** `pip install oxoria` → launch with `oxoria`

---

## ✨ Key Features

### 🔍 Semantic Search
Find references by meaning, not just filename. Type a concept like *"religion"* and Oxoria will surface relevant results such as *"shrine"* — powered by natural language understanding applied to your own image memos.

### 📸 Instant Screenshot Capture
No need to open the app first. With **Oxoria Screen Capture Util** running in the background, press `Cmd+Shift+O` anytime to capture your screen and import it directly into your reference library.

### 🔁 Duplicate Detection
Oxoria stores a perceptual hash for every image. Re-importing the same image won't create duplicates — your library stays clean automatically.

### 📦 Fully Portable
Your entire reference library lives in a single central repository folder. Copy it to a new machine and pick up exactly where you left off.

### 🐍 Python API
Every UI action and internal operation maps to a Python function. Combine them freely to automate workflows, build custom pipelines, or extend Oxoria however you like.

---

## 🛠️ Tech Stack

| Category | Details |
|---|---|
| Language | Python 3.13 |
| GUI | PySide6 |
| ML / Search | `transformers`, `torch`, `faiss-cpu`, `optimum[onnxruntime]` |
| Image Processing | `Pillow`, `ImageHash` |
| Utilities | `numpy`, `psutil`, `setproctitle` |

---

## 🗺️ Roadmap

- [ ] **3D Object Import** — Import `.obj` and other 3D formats as interactive references via OpenGL
- [ ] **Canvas Version Control** — Git-backed versioning of canvas layouts using PyGit
- [ ] **Window Overlay Mode** — Keep references on top with an adjustable transparent window while working in other apps
- [ ] **Partial C++ Migration** — Performance-critical modules (e.g. 3D rendering) migrated to C++ as needed

---

## ⚠️ Known Limitations

- **Startup time** — `transformers` and `torch` currently add ~8 seconds to startup. A planned migration to a Rust-based tokenizer and a lighter ONNX runtime should significantly reduce this.
- **Duplicate sensitivity** — The current 16-bit dHash may flag near-identical images (e.g. expression variants) as duplicates. Upgrading to 32-bit dHash is planned.
- **API coherence** — The Python API is functional but spread across modules. A cleaner, more unified interface is in progress.
- **Test coverage** — Automated unit and regression tests are not yet in place; this is a known priority.

---

## 📄 License

Licensed under the **Apache 2.0 License** — free to use, modify, and redistribute for both personal and commercial purposes.

---

## 🔗 Links

- 📁 [GitHub Repository](https://github.com/shinonome-MiDUki/oxoria)

---

*Oxoria is still under active development. Feedback and contributions are very welcome!*
*A stable build is planned for release on Steam once the core feature set is complete.*