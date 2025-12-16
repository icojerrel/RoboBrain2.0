# CLAUDE.md - AI Assistant Guide for RoboBrain 2.0

This document provides comprehensive guidance for AI assistants working with the RoboBrain 2.0 codebase.

## Project Overview

**RoboBrain 2.0** is an advanced open-source embodied AI brain model designed for robotic manipulation and spatial reasoning tasks. It unifies perception, reasoning, and planning capabilities for complex embodied tasks in physical environments.

### Key Features
- **Multi-modal Understanding**: Supports multi-image, long video, and high-resolution visual inputs
- **Chain-of-Thought Reasoning**: Advanced reasoning capabilities with thinking mode (7B/32B models)
- **Spatial Intelligence**: Affordance prediction, visual grounding, trajectory forecasting, pointing
- **Temporal Planning**: Closed-loop interaction, multi-agent planning, scene memory
- **Multiple Model Sizes**: 3B (lightweight), 7B (balanced), 32B (full-scale) parameter variants

### Architecture
- **Vision Encoder** + **MLP Projector** for visual processing
- **LLM Decoder** (based on Qwen2.5-VL) for reasoning and generation
- Heterogeneous architecture combining vision and language models
- Outputs structured plans, spatial relations, and coordinate predictions

## Repository Structure

```
RoboBrain2.0/
├── inference.py          # Main inference implementation (UnifiedInference class)
├── requirements.txt      # Python dependencies
├── README.md            # Detailed project documentation
├── LICENSE              # Project license
├── .gitignore           # Git ignore patterns
└── assets/              # Images, logos, and demo resources
    └── demo/            # Demo images for testing
```

### Key Files

**inference.py** (260 lines)
- `UnifiedInference` class: Main inference wrapper for RoboBrain models
- Supports tasks: general, pointing, affordance, trajectory, grounding
- Handles thinking mode for 7B/32B models
- Includes visualization utilities (`draw_on_image` method)
- Automatically detects model capabilities based on model ID

## Technology Stack

### Core Dependencies
- **Python**: 3.10 (required)
- **PyTorch**: 2.5.1 (deep learning framework)
- **Transformers**: 4.50.0 (Hugging Face library)
- **Qwen-VL-Utils**: 0.0.8 (Qwen vision-language utilities)
- **vLLM**: 0.7.3 (efficient inference)
- **OpenCV**: 4.7.0.72 (image processing)

### Additional Key Packages
- **Accelerate**: 1.3.0 (distributed training)
- **PEFT**: 0.14.0 (parameter-efficient fine-tuning)
- **Datasets**: 3.6.0 (data loading)
- **Gradio**: 5.12.0 (web UI)
- **Ray**: 2.40.0 (distributed computing)
- **LangChain**: 0.3.15 (LLM application framework)

### CUDA/GPU Requirements
- CUDA 12.x support (nvidia-cuda-runtime-cu12==12.4.127)
- cuDNN, cuBLAS, NCCL for distributed training
- GPU recommended for inference and training

## Development Setup

### Environment Setup
```bash
# Clone repository
git clone https://github.com/FlagOpen/RoboBrain2.0.git
cd RoboBrain2.0

# Create conda environment
conda create -n robobrain2 python=3.10
conda activate robobrain2

# Install dependencies
pip install -r requirements.txt
```

### Model Downloads
Models are available on Hugging Face:
- `BAAI/RoboBrain2.0-3B` (3B parameters, no thinking mode)
- `BAAI/RoboBrain2.0-7B` (7B parameters, with thinking mode)
- `BAAI/RoboBrain2.0-32B` (32B parameters, with thinking mode)

Models will be automatically downloaded from Hugging Face on first use.

## Code Conventions

### Python Style
- Uses standard Python conventions
- Type hints for function parameters (see `Union[list, str]` in inference.py)
- Docstrings for classes and methods
- Clear variable naming (e.g., `enable_thinking`, `do_sample`)

### Model Naming Convention
- Model IDs follow pattern: `BAAI/RoboBrain2.0-{size}B`
- Size determines capabilities: 3B (basic), 7B (thinking), 32B (advanced thinking)

### Task Types
The codebase supports 5 task types:
1. **general**: General visual question answering
2. **pointing**: Identify specific points in images (returns coordinates)
3. **affordance**: Predict actionable areas for robot end-effector
4. **trajectory**: Predict motion path as sequence of waypoints
5. **grounding**: Visual grounding with bounding boxes

### Coordinate Systems
- **Normalized coordinates**: Used for some tasks (pointing)
- **Pixel coordinates**: Absolute x,y positions in image space
- **Bounding boxes**: `[x1, y1, x2, y2]` format (top-left, bottom-right)
- **Trajectories**: List of (x, y) tuples representing waypoints

## Usage Patterns

### Basic Inference
```python
from inference import UnifiedInference

# Initialize model
model = UnifiedInference("BAAI/RoboBrain2.0-7B")

# Run inference
result = model.inference(
    text="What is shown in this image?",
    image="path/to/image.jpg",
    task="general",
    enable_thinking=True,
    do_sample=True
)

# Access results
print(result['thinking'])  # Reasoning process (if enabled)
print(result['answer'])    # Final answer
```

### Thinking Mode
- **3B models**: No thinking support (direct answers only)
- **7B/32B models**: Support thinking mode
- When enabled: Model generates `<think>reasoning</think><answer>result</answer>`
- Can be disabled for faster inference: `enable_thinking=False`

### Plotting Results
For spatial tasks (pointing, affordance, trajectory, grounding):
```python
result = model.inference(
    text="the person wearing a red hat",
    image="image.jpg",
    task="grounding",
    plot=True  # Saves annotated image to result/ directory
)
```

## Training and Evaluation

### Training Options

**Option 1: FlagScale (Recommended for Megatron users)**
- Framework developed by BAAI Framework R&D team
- Optimized for distributed training
- Repository: https://github.com/FlagOpen/FlagScale
- See: `flagscale/train/models/qwen2_5_vl/QuickStart.md`

**Option 2: DeepSpeed**
- Compatible with official Qwen2.5-VL training code
- Repository: https://github.com/QwenLM/Qwen2.5-VL/tree/main/qwen-vl-finetune

### Evaluation Framework
- **FlagEvalMM**: Flexible evaluation framework by BAAI FlagEval team
- Repository: https://github.com/flageval-baai/FlagEvalMM
- Supports comprehensive multimodal benchmarks
- Example command:
```bash
flagevalmm --tasks tasks/where2place/where2place.py \
    --exec model_zoo/vlm/api_model/model_adapter.py \
    --model BAAI/RoboBrain2.0-7B \
    --num-workers 8 \
    --output-dir ./results/RoboBrain2.0-7B \
    --backend vllm
```

### Supported Benchmarks
**Spatial Reasoning:**
- BLINK-Spatial, CV-Bench, EmbSpatial, RoboSpatial
- RefSpatial, SAT, VSI-Bench, Where2Place, ShareRobot-Bench

**Temporal Reasoning:**
- Multi-Robot-Planning, Ego-Plan2, RoboBench-Planning

## Development Workflows

### Making Code Changes

1. **Before Editing**: Always read the file first to understand context
2. **Minimal Changes**: Only modify what's necessary for the task
3. **Preserve Structure**: Maintain existing code style and patterns
4. **Test Changes**: Verify with appropriate task type and model

### Adding New Task Types

If extending with new task types:
1. Add task name to assertion in `inference()` method (line 61-62)
2. Add task-specific prompt formatting (lines 72-83)
3. Add parsing logic for output format (lines 157-186)
4. Update plotting logic if visual output needed (lines 206-259)

### Git Workflow

- **Main branch**: Default branch for the project
- **Feature branches**: Should start with `claude/` prefix
- **Commit messages**: Clear, descriptive, focusing on "why" not "what"
- **Never commit**: Model weights, result images, test.py, .env files

### Files to Ignore (from .gitignore)
- `__pycache__/`, `*.pyc` (Python cache)
- `result/` (inference output directory)
- `test.py` (local testing scripts)
- `.env`, `venv/` (environment files)
- Model checkpoints and large files

## Best Practices for AI Assistants

### Understanding the Codebase
1. **Start with README.md**: Comprehensive project overview
2. **Review inference.py**: Understand the main API and task types
3. **Check requirements.txt**: Understand dependencies before suggesting changes
4. **Examine .gitignore**: Know what files should not be committed

### Making Modifications
1. **Read First**: Always read files before suggesting changes
2. **Respect Architecture**: This is a wrapper around Qwen2.5-VL, don't fundamentally change that
3. **Maintain Compatibility**: Changes should work across 3B/7B/32B models
4. **Test with Examples**: Use the examples in README.md as test cases

### Common Tasks

**Adding a new task type**:
- Extend the task assertion list
- Add prompt template for the new task
- Add output parsing regex pattern
- Add visualization if needed

**Improving inference performance**:
- Consider vLLM backend optimizations
- Adjust `max_new_tokens`, `temperature`, `do_sample` parameters
- Check GPU memory usage and batch size

**Debugging inference issues**:
- Check model ID for thinking support
- Verify image paths (local files need `file://` prefix)
- Examine raw output before parsing
- Review task-specific prompt formatting

### When to Avoid Changes
- Don't modify core model architecture without explicit request
- Don't change coordinate systems or output formats (breaks compatibility)
- Don't add unnecessary dependencies
- Don't remove backward compatibility for existing code

## Important Notes

### Model Behavior
- **3B models**: Fast, no reasoning, direct answers
- **7B models**: Balanced performance, chain-of-thought reasoning
- **32B models**: Best performance, advanced reasoning, higher resource needs

### Coordinate Formats
Different tasks use different coordinate representations:
- **Pointing**: List of (x, y) tuples, normalized or pixel coordinates
- **Grounding/Affordance**: Bounding boxes as [x1, y1, x2, y2]
- **Trajectory**: Ordered list of waypoints [(x1, y1), (x2, y2), ...]

### Image Inputs
- Supports local file paths (will add `file://` prefix automatically)
- Supports HTTP/HTTPS URLs (used directly)
- Single image or list of images (multi-image reasoning)
- Must be single image for pointing/affordance/trajectory/grounding tasks

### Output Directory
- Annotated images saved to `result/` directory
- Created automatically if doesn't exist
- Included in .gitignore (don't commit result images)

## Related Projects

- **RoboBrain 1.0**: Previous version (CVPR 2025)
- **RoboBrain-X0-Preview**: Cross-embodiment VLA model (CoRL 2025)
- **RoboOS**: Multi-robot coordination system
- **Reason-RFT**: Core post-training strategy (NeurIPS 2025)
- **FlagScale**: Training framework
- **FlagEvalMM**: Evaluation framework

## Resources

- **Project Website**: https://superrobobrain.github.io/
- **Paper**: https://arxiv.org/abs/2507.02029
- **Hugging Face**: https://huggingface.co/collections/BAAI/robobrain20-6841eeb1df55c207a4ea0036/
- **GitHub**: https://github.com/FlagOpen/RoboBrain2.0
- **Training Framework**: https://github.com/FlagOpen/FlagScale
- **Evaluation Framework**: https://github.com/flageval-baai/FlagEvalMM

## Quick Reference

### Key Classes and Functions

**UnifiedInference** (inference.py:6-260)
- `__init__(model_id, device_map)`: Initialize model
- `inference(text, image, task, plot, enable_thinking, do_sample, temperature)`: Main inference method
- `draw_on_image(image_path, points, boxes, trajectories, output_path)`: Visualization helper

### Key Parameters
- `model_id`: Hugging Face model identifier or local path
- `task`: One of ["general", "pointing", "affordance", "trajectory", "grounding"]
- `enable_thinking`: Enable chain-of-thought reasoning (7B/32B only)
- `do_sample`: Use sampling vs greedy decoding
- `temperature`: Sampling temperature (0.7 default)
- `max_new_tokens`: Maximum tokens to generate (768 default)

### Common Patterns
```python
# General VQA
model.inference(prompt, image, task="general")

# Spatial understanding
model.inference(prompt, image, task="grounding", plot=True)

# Robot planning
model.inference(prompt, image, task="trajectory", enable_thinking=True)

# Point identification
model.inference(prompt, image, task="pointing", plot=True)
```

---

**Last Updated**: 2025-12-16
**For Questions**: See project website or GitHub issues
