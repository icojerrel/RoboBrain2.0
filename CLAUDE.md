# CLAUDE.md — RoboBrain 2.0

This file provides AI assistants with a concise but complete reference for working in this repository.

---

## Project Overview

**RoboBrain 2.0** is an open-source embodied brain model from BAAI (Beijing Academy of Artificial Intelligence). It is a vision-language model (VLM) built on top of **Qwen2.5-VL** that supports perception, reasoning, and planning for robotic manipulation tasks in physical environments.

The repository is primarily an **inference/deployment release** — training and evaluation are delegated to external frameworks. The core deliverable is a clean Python inference wrapper (`inference.py`) and pre-trained model weights hosted on Hugging Face.

**Paper:** arXiv:2507.02029
**License:** Apache 2.0
**Organization:** BAAI (Beijing Academy of Artificial Intelligence)

---

## Repository Structure

```
RoboBrain2.0/
├── inference.py          # Main inference implementation — the primary source file
├── requirements.txt      # Python dependencies (237 packages pinned)
├── README.md             # Project documentation with usage examples
├── LICENSE               # Apache License 2.0
├── CLAUDE.md             # This file
└── assets/               # Images for README (architecture diagrams, demo outputs, logos)
    ├── demo/             # Input demo images for each task type
    ├── arch.png          # Architecture diagram
    ├── visualization.png
    ├── results.png
    ├── result_table_*.png
    ├── logo*.png
    ├── demo_*.jpg        # Annotated output demo images
    └── wechat.png
```

This is a minimal-structure repository. **There is only one Python source file** (`inference.py`). There are no subdirectories for source modules, no test suite, no CI/CD pipelines, and no build system.

---

## Technology Stack

| Layer | Technology |
|---|---|
| Base model | Qwen2.5-VL (Alibaba) — 3B, 7B, 32B parameter variants |
| ML framework | PyTorch 2.5.1 + CUDA 12.x |
| Transformers | Hugging Face `transformers==4.50.0` |
| Optimized serving | `vllm==0.7.3` |
| Vision processing | `qwen-vl-utils`, `opencv-python`, `Pillow` |
| Embeddings | `sentence-transformers`, `FlagEmbedding` |
| Web APIs | FastAPI, Flask, uvicorn |
| Agentic tools | `smolagents`, `e2b-code-interpreter` |
| Linting | `ruff==0.9.1` (included in requirements, no config file) |
| Testing | `pytest==8.3.5` (no test files exist yet) |
| Language | Python 3.10 (conda env `robobrain2`) |

---

## Model Variants

| Model | HuggingFace ID | Thinking Mode | Notes |
|---|---|---|---|
| 3B | `BAAI/RoboBrain2.0-3B` | Not supported | Lightweight, fastest |
| 7B | `BAAI/RoboBrain2.0-7B` | Supported (default) | Balanced default |
| 32B | `BAAI/RoboBrain2.0-32B` | Supported (default) | Highest accuracy |

Thinking mode is **automatically detected** by checking for `"3b"`, `"7b"`, or `"32b"` in the model ID string (case-insensitive). Unknown model names default to thinking enabled.

---

## Core API — `inference.py`

### `UnifiedInference` class

**Constructor:**
```python
model = UnifiedInference(model_id="BAAI/RoboBrain2.0-7B", device_map="auto")
```
- Downloads and loads the Qwen2.5-VL model and processor from Hugging Face (or local path).
- `device_map="auto"` distributes the model across available GPUs automatically.

**Main method:**
```python
result = model.inference(
    text: str,
    image: Union[list, str],   # file path(s) or HTTP URL(s)
    task="general",            # see supported tasks below
    plot=False,                # if True, saves annotated image to ./result/
    enable_thinking=None,      # None = auto; True/False = override
    do_sample=True,
    temperature=0.7,
)
```

**Return value** is always a dict:
```python
{"answer": "...", "thinking": "..."}   # thinking key omitted when empty
```

**Supported tasks:**

| `task` value | Description | Output format |
|---|---|---|
| `"general"` | General VQA — multi-image OK | Free-form text |
| `"grounding"` | Visual grounding / bounding box | `"[x1, y1, x2, y2]"` |
| `"affordance"` | Robot end-effector affordance area | `"[x1, y1, x2, y2]"` |
| `"trajectory"` | Robot end-effector trajectory | `"[(x1,y1), (x2,y2), ...]"` |
| `"pointing"` | Point to normalized pixel locations | `"[(x1,y1), (x2,y2), ...]"` |

Constraints:
- `"pointing"`, `"affordance"`, `"trajectory"`, `"grounding"` require **exactly one image**.
- `"general"` supports multiple images.
- All non-general tasks automatically prepend a task-specific prompt to the user's text.

**Visualization method:**
```python
model.draw_on_image(
    image_path,
    points=None,        # [(x, y), ...]
    boxes=None,         # [[x1, y1, x2, y2], ...]
    trajectories=None,  # [[(x1, y1), ...], ...]
    output_path=None,   # defaults to "<name>_annotated<ext>"
)
```
- Draws red circles for points, green rectangles for boxes, blue lines for trajectories.
- Saves to `./result/` when called via `inference()` with `plot=True`.

---

## Development Setup

```bash
# Clone and install
git clone https://github.com/FlagOpen/RoboBrain2.0.git
cd RoboBrain2.0

# Create and activate conda environment
conda create -n robobrain2 python=3.10
conda activate robobrain2

pip install -r requirements.txt
```

Requirements:
- **CUDA 12.x GPU** is required — `inputs.to("cuda")` is hardcoded in `inference.py:120`.
- At least **~15 GB VRAM** for 7B; significantly more for 32B.
- All 237 packages are pinned; do not upgrade versions without testing.

---

## Key Conventions

### Code style
- **Linter:** `ruff` is available but has no configuration file (`.ruff.toml` or `pyproject.toml`). Use default ruff rules.
- **No type annotations required** in existing code, but they are welcome on new functions.
- Python 3.10+ syntax is acceptable.
- There is no formatter configured; follow standard PEP 8 style.

### Prompt injection convention (task-specific prompts)
Each non-general task **mutates the `text` argument** in `inference()` before sending to the model. When modifying task prompts, keep the injected format strings consistent with the regex parsers used in the plotting section:
- Trajectory: `r'(\d+),\s*(\d+)'`
- Pointing: `r'\(\s*(\d+)\s*,\s*(\d+)\s*\)'`
- Affordance/Grounding: `r'\[\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\]'`

### Thinking mode implementation
- Thinking is activated by appending `<think>` to the prompt template.
- When thinking is **disabled but supported** (7B/32B), `<think></think><answer>` is injected to force direct output.
- The model's CoT output is parsed by splitting on `</think>`.
- Do not break this token injection pattern when modifying the inference loop.

### File output
- Annotated images are saved to `./result/` (created if absent).
- Output filenames follow the pattern: `<original_basename>_with_<task>_annotated.<ext>`.

---

## Training

Training is **not in this repository**. Two supported paths:

1. **FlagScale** (Megatron-LM based, recommended for large scale):
   - See [FlagScale QuickStart](https://github.com/FlagOpen/FlagScale/blob/dc6e8248eafe6f03e66e2735400378e5db1f67dd/flagscale/train/models/qwen2_5_vl/QuickStart.md)

2. **DeepSpeed** (Qwen2.5-VL official):
   - See [qwen-vl-finetune](https://github.com/QwenLM/Qwen2.5-VL/tree/main/qwen-vl-finetune)

---

## Evaluation

Evaluation uses **FlagEvalMM** (external framework):

```bash
flagevalmm --tasks tasks/where2place/where2place.py \
    --exec model_zoo/vlm/api_model/model_adapter.py \
    --model BAAI/RoboBrain2.0-7B \
    --num-workers 8 \
    --output-dir ./results/RoboBrain2.0-7B \
    --backend vllm \
    --extra-args "--limit-mm-per-prompt image=18 --tensor-parallel-size 4 --max-model-len 32768 --trust-remote-code --mm-processor-kwargs '{\"max_dynamic_patch\":4}'"
```

See [FlagEvalMM](https://github.com/flageval-baai/FlagEvalMM) for installation.

---

## What Does Not Exist (yet)

Be aware of these gaps before assuming infrastructure is in place:

- **No test suite** — no `tests/` directory, no `test_*.py` files, no pytest configuration.
- **No CI/CD** — no `.github/workflows/` directory.
- **No pre-commit hooks** — no `.pre-commit-config.yaml`.
- **No `pyproject.toml` or `setup.py`** — not an installable package.
- **No `Makefile`** — no `make test`, `make lint`, etc.
- **No `.env.example`** — no environment variable configuration needed for basic inference.
- **No Docker configuration** — no `Dockerfile` or `docker-compose.yml`.
- **No linting configuration** — ruff uses all defaults.

---

## Related Projects

| Project | Role |
|---|---|
| [RoboBrain 1.0](https://github.com/FlagOpen/RoboBrain) | Predecessor |
| [RoboOS](https://github.com/flagopen/RoboOS) | Multi-robot coordination system using RoboBrain 2.0 |
| [RoboBrain-X0](https://github.com/FlagOpen/RoboBrain-X0) | Cross-embodiment VLA based on RoboBrain 2.0 (3B) |
| [Reason-RFT](https://github.com/tanhuajie/Reason-RFT) | Post-training strategy used for RoboBrain 2.0 (NeurIPS 2025) |
| [FlagScale](https://github.com/FlagOpen/FlagScale) | Distributed training framework (Megatron-based) |
| [FlagEvalMM](https://github.com/flageval-baai/FlagEvalMM) | Multimodal evaluation framework |
