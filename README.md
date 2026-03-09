<div align="center">
<img src="./assets/logo2.png" width="500"/>
</div>

# RoboBrain 2.0: See Better. Think Harder. Do Smarter.

<p align="center">
  <a href="https://github.com/FlagOpen/RoboBrain2.0/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License"></a>
  <a href="https://arxiv.org/abs/2507.02029"><img src="https://img.shields.io/badge/arXiv-2507.02029-b31b1b.svg" alt="arXiv"></a>
  <a href="https://huggingface.co/collections/BAAI/robobrain20-6841eeb1df55c207a4ea0036/"><img src="https://img.shields.io/badge/🤗-Hugging%20Face-yellow.svg" alt="Hugging Face"></a>
</p>

<p align="center">
  ⭐️ <a href="https://superrobobrain.github.io/">Project Page</a>
  &nbsp;|&nbsp;
  🤗 <a href="https://huggingface.co/collections/BAAI/robobrain20-6841eeb1df55c207a4ea0036/">Hugging Face</a>
  &nbsp;|&nbsp;
  🤖 <a href="https://www.modelscope.cn/models/BAAI/RoboBrain2.0-7B/files/">ModelScope</a>
  &nbsp;|&nbsp;
  📖 <a href="https://wisemodel.cn/models/BAAI/RoboBrain2.0-7B">Wisemodel</a>
  &nbsp;|&nbsp;
  📑 <a href="https://arxiv.org/abs/2507.02029">Technical Report</a>
  &nbsp;|&nbsp;
  💬 <a href="./assets/wechat.png">WeChat &amp; RedNote</a>
</p>

<p align="center">
  🎯 <a href="https://flagopen.github.io/RoboOS/">RoboOS</a>: An Efficient Open-Source Multi-Robot Coordination System for RoboBrain.
</p>
<p align="center">
  ⭐️ <a href="https://github.com/tanhuajie/Reason-RFT">Reason-RFT</a>: Core Post-Training Strategy for Embodied Visual Reasoning in RoboBrain 2.0.
</p>
<p align="center">
  🌍 <a href="https://github.com/FlagOpen/RoboBrain">RoboBrain 1.0</a>: A Unified Brain Model for Robotic Manipulation from Abstract to Concrete.
</p>

---

## Table of Contents

- [Overview](#-overview)
- [News](#️-news)
- [Features](#-features)
- [Architecture](#️-architecture)
- [Model Zoo](#-model-zoo)
- [Setup](#️-setup)
- [Quick Start](#-quick-start)
- [Simple Inference](#-simple-inference)
- [Training](#-training)
- [Evaluation](#-evaluation)
- [Results](#-more-results)
- [Citation](#-citation)
- [Contact](#-contact)

---

## 🔥 Overview

We are excited to introduce **RoboBrain 2.0**, the most powerful open-source embodied brain model to date. Compared to its predecessor RoboBrain 1.0, our latest version is designed to unify perception, reasoning, and planning for complex embodied tasks in physical environments. It comes in two variants: a lightweight 7B model and a full-scale 32B model, featuring a heterogeneous architecture with a vision encoder and a language model.

Despite its compact size, RoboBrain 2.0 achieves strong performance across a wide spectrum of embodied reasoning tasks. On both spatial and temporal benchmarks, the 32B variant achieves leading results in most cases, surpassing prior open-source and proprietary models. In particular, it supports key real-world embodied intelligence capabilities, including spatial understanding (e.g., affordance prediction, spatial referring, trajectory forecasting) and temporal decision-making (e.g., closed-loop interaction, multi-agent long-horizon planning, and real-time scene memory).

<div align="center">
<img src="./assets/results.png" />
</div>

---

## 🗞️ News

- **`2025-09-29`**: 🤖 We released a unified cross-embodiment VLA model [RoboBrain-X0-Preview](https://github.com/FlagOpen/RoboBrain-X0) based on RoboBrain 2.0 (3B) at **CoRL 2025**.
- **`2025-09-18`**: 🔥 [**Reason-RFT**](https://arxiv.org/abs/2503.20752) (Core Post-Training Strategy for RoboBrain 2.0) accepted to **NeurIPS 2025**.
- **`2025-07-23`**: 🤗 [RoboBrain 2.0-3B](https://huggingface.co/BAAI/RoboBrain2.0-3B) model checkpoint released on Hugging Face.
- **`2025-07-03`**: 🤗 [RoboBrain 2.0-32B](https://huggingface.co/BAAI/RoboBrain2.0-32B) model checkpoint released on Hugging Face.
- **`2025-06-11`**: 💡 Optimized inference pipeline for **multi-task applications**. See [Simple Inference](#-simple-inference) for quick usage.
- **`2025-06-07`**: 🎉 Training ([FlagScale](https://github.com/FlagOpen/FlagScale)) and evaluation ([FlagEvalMM](https://github.com/flageval-baai/FlagEvalMM)) frameworks highlighted.
- **`2025-06-06`**: 🤗 [RoboBrain 2.0-7B](https://huggingface.co/BAAI/RoboBrain2.0-7B) model checkpoint released on Hugging Face.
- **`2025-06-06`**: 🔥 [RoboBrain 2.0](https://superrobobrain.github.io/) officially released.
- **`2025-04-11`**: 🎉 [RoboBrain 1.0](https://github.com/FlagOpen/RoboBrain/) selected for CVPR 2025's official [Embodied AI Trends Commentary](https://cvpr.thecvf.com/Conferences/2025/News/AI_Enhanced_Robotics).
- **`2025-02-27`**: 🔥 [**RoboBrain 1.0**](http://arxiv.org/abs/2502.21257/) accepted to **CVPR 2025**.

---

## 🚀 Features

**RoboBrain 2.0** supports:

- **Interactive reasoning** — long-horizon planning and closed-loop feedback
- **Spatial perception** — precise point and bounding box prediction from complex instructions
- **Temporal perception** — future trajectory estimation
- **Scene reasoning** — real-time structured memory construction and update

<div align="center">
<img src="./assets/visualization.png" />
</div>

---

## ⭐️ Architecture

**RoboBrain 2.0** supports ***multi-image***, ***long video***, and ***high-resolution visual inputs***, along with complex task instructions and structured ***scene graphs*** on the language side. Visual inputs are processed via a Vision Encoder and MLP Projector, while textual inputs are tokenized into a unified token stream. All inputs are fed into a ***LLM Decoder*** that performs ***long-chain-of-thought reasoning*** and outputs structured plans, spatial relations, and both ***relative*** and ***absolute coordinates***.

<div align="center">
<img src="./assets/arch.png" />
</div>

---

## 🤗 Model Zoo

| Model | Checkpoint | Thinking Mode | Recommended VRAM |
|---|---|---|---|
| RoboBrain 2.0-3B | [🤗 BAAI/RoboBrain2.0-3B](https://huggingface.co/BAAI/RoboBrain2.0-3B) | Not supported | ~8 GB |
| RoboBrain 2.0-7B | [🤗 BAAI/RoboBrain2.0-7B](https://huggingface.co/BAAI/RoboBrain2.0-7B) | Supported ✅ | ~16 GB |
| RoboBrain 2.0-32B | [🤗 BAAI/RoboBrain2.0-32B](https://huggingface.co/BAAI/RoboBrain2.0-32B) | Supported ✅ | ~70 GB |

---

## 🛠️ Setup

**Requirements:** CUDA-capable GPU (CUDA 12.x), Python 3.10, conda.

```bash
# Clone the repository
git clone https://github.com/FlagOpen/RoboBrain2.0.git
cd RoboBrain2.0

# Create and activate conda environment
conda create -n robobrain2 python=3.10
conda activate robobrain2

# Install dependencies
pip install -r requirements.txt
```

> **Note:** Model weights are downloaded automatically from Hugging Face on first use. Ensure you have sufficient disk space (~15 GB for 7B, ~65 GB for 32B).

---

## ⚡ Quick Start

```python
from inference import UnifiedInference

model = UnifiedInference("BAAI/RoboBrain2.0-7B")

result = model.inference(
    "What is shown in this image?",
    "http://images.cocodataset.org/val2017/000000039769.jpg",
    task="general",
    enable_thinking=True,
)
print(result["answer"])
# → 'The image shows two cats lying on a pink blanket on a couch.'
```

---

## 💡 Simple Inference

All inference calls return a dict: `{"answer": "...", "thinking": "..."}`.
The `"thinking"` key is only present when thinking mode is active.

### 1. General VQA — without thinking

```python
from inference import UnifiedInference

model = UnifiedInference("BAAI/RoboBrain2.0-7B")

pred = model.inference(
    "What is shown in this image?",
    "http://images.cocodataset.org/val2017/000000039769.jpg",
    task="general",
    enable_thinking=False,
)
print(pred)
# {'answer': 'Two cats sleeping side by side on a couch.'}
```

### 2. General VQA — with thinking

```python
from inference import UnifiedInference

model = UnifiedInference("BAAI/RoboBrain2.0-7B")

pred = model.inference(
    "What is shown in this image?",
    "http://images.cocodataset.org/val2017/000000039769.jpg",
    task="general",
    enable_thinking=True,
)
print(pred)
# {
#   'thinking': 'Upon examining the visual input, I observe two cats resting comfortably ...',
#   'answer': 'The image shows two cats lying on a pink blanket on a couch.'
# }
```

### 3. Visual Grounding

Predicts a bounding box `[x1, y1, x2, y2]` for a described region. Pass `plot=True` to save an annotated image to `./result/`.

```python
from inference import UnifiedInference

model = UnifiedInference("BAAI/RoboBrain2.0-7B")

pred = model.inference(
    "the person wearing a red hat",
    "./assets/demo/grounding.jpg",
    task="grounding",
    plot=True,
    enable_thinking=True,
)
print(pred)
# {'thinking': '...', 'answer': '[0, 193, 226, 640]'}
```

<div align="center">
<img src="./assets/demo_vg.jpg" />
</div>

### 4. Affordance Prediction (Embodied)

Predicts where a robot end-effector should interact with an object.

```python
from inference import UnifiedInference

model = UnifiedInference("BAAI/RoboBrain2.0-7B")

pred = model.inference(
    "hold the cup",
    "./assets/demo/affordance.jpg",
    task="affordance",
    plot=True,
    enable_thinking=True,
)
print(pred)
# {'thinking': '...', 'answer': '[577, 224, 638, 310]'}
```

<div align="center">
<img src="./assets/demo_aff.jpg" />
</div>

### 5. Trajectory Prediction (Embodied)

Predicts up to 10 key waypoints for end-effector motion.

```python
from inference import UnifiedInference

model = UnifiedInference("BAAI/RoboBrain2.0-7B")

pred = model.inference(
    "reach for the banana on the plate",
    "./assets/demo/trajectory.jpg",
    task="trajectory",
    plot=True,
    enable_thinking=True,
)
print(pred)
# {'thinking': '...', 'answer': '[(137, 116), (169, 94), (208, 84), (228, 80)]'}
```

<div align="center">
<img src="./assets/demo_traj.jpg" />
</div>

### 6. Pointing Prediction (Embodied)

Identifies normalized pixel coordinates for described spatial regions.

```python
from inference import UnifiedInference

model = UnifiedInference("BAAI/RoboBrain2.0-7B")

pred = model.inference(
    "Identify several spots within the vacant space that's between the two mugs",
    "./assets/demo/pointing.jpg",
    task="pointing",
    plot=True,
    enable_thinking=True,
)
print(pred)
# {'thinking': '...', 'answer': '[(376, 309), (332, 357), (384, 335), ...]'}
```

<div align="center">
<img src="./assets/demo_pt.jpg" />
</div>

### 7. Navigation (Embodied)

Use `task="pointing"` to identify navigable spots within scene regions.

```python
from inference import UnifiedInference

model = UnifiedInference("BAAI/RoboBrain2.0-7B")
image = "./assets/demo/navigation.jpg"

# Find spots near the toilet
pred1 = model.inference(
    "Identify several spots within toilet in the house",
    image, task="pointing", plot=True, enable_thinking=True,
)

# Find spots on the sofa
pred2 = model.inference(
    "Identify several spots within the sofa that can be used for sitting",
    image, task="pointing", plot=True, enable_thinking=True,
)
```

<div align="center">
<img src="./assets/demo_nv_1.jpg"/>
</div>

<div align="center">
<img src="./assets/demo_nv_2.jpg"/>
</div>

---

## 🤖 Training

Training code is hosted in external frameworks. Two supported options:

### Option 1: FlagScale (Megatron — Recommended)

<div align="center">
<img src="./assets/logo_flagscale.png" width="250"/>
</div>

We adopted the distributed training framework [FlagScale](https://github.com/FlagOpen/FlagScale) developed by the ***Framework R&D team of BAAI***. Refer to [QuickStart.md](https://github.com/FlagOpen/FlagScale/blob/dc6e8248eafe6f03e66e2735400378e5db1f67dd/flagscale/train/models/qwen2_5_vl/QuickStart.md) to train or fine-tune RoboBrain 2.0.

### Option 2: DeepSpeed (Qwen2.5-VL compatible)

RoboBrain 2.0 is compatible with the official Qwen2.5-VL training code. Refer to [qwen-vl-finetune](https://github.com/QwenLM/Qwen2.5-VL/tree/main/qwen-vl-finetune).

---

## 🔍 Evaluation

<div align="center">
<img src="./assets/logo_flageval.png" width="300"/>
</div>

We adopted the evaluation framework [FlagEvalMM](https://github.com/flageval-baai/FlagEvalMM) developed by the ***FlagEval team of BAAI***.

**Step 1:** Follow the [FlagEvalMM](https://github.com/flageval-baai/FlagEvalMM) instructions for installation, configuration, and data preparation.

**Step 2:** Run evaluation:

```bash
flagevalmm --tasks tasks/where2place/where2place.py \
    --exec model_zoo/vlm/api_model/model_adapter.py \
    --model BAAI/RoboBrain2.0-7B \
    --num-workers 8 \
    --output-dir ./results/RoboBrain2.0-7B \
    --backend vllm \
    --extra-args "--limit-mm-per-prompt image=18 \
                  --tensor-parallel-size 4 \
                  --max-model-len 32768 \
                  --trust-remote-code \
                  --mm-processor-kwargs '{\"max_dynamic_patch\":4}'"
```

---

## 😊 More Results

**RoboBrain 2.0** achieves state-of-the-art or near-SOTA performance on:

- **9 spatial reasoning benchmarks:** BLINK-Spatial, CV-Bench, EmbSpatial, RoboSpatial, RefSpatial, SAT, VSI-Bench, Where2Place, ShareRobot-Bench
- **3 temporal reasoning benchmarks:** Multi-Robot-Planning, Ego-Plan2, RoboBench-Planning

It outperforms leading open-source models (Cosmos-Reason1, Qwen2.5-VL) and closed-source models (Gemini 2.5 Pro, o4-mini, Claude Sonnet 4).

<div align="center">
<img src="./assets/result_table_1.png" />
</div>

<div align="center">
<img src="./assets/result_table_2.png" />
</div>

<div align="center">
<img src="./assets/result_table_3.png" />
</div>

---

## 📑 Citation

If you find this project useful, please cite:

```bibtex
@article{RoboBrain2.0TechnicalReport,
    title={RoboBrain 2.0 Technical Report},
    author={BAAI RoboBrain Team},
    journal={arXiv preprint arXiv:2507.02029},
    year={2025}
}

@article{RoboBrain1.0,
    title={Robobrain: A unified brain model for robotic manipulation from abstract to concrete},
    author={Ji, Yuheng and Tan, Huajie and Shi, Jiayu and Hao, Xiaoshuai and Zhang, Yuan and Zhang, Hengyuan and Wang, Pengwei and Zhao, Mengdi and Mu, Yao and An, Pengju and others},
    journal={arXiv preprint arXiv:2502.21257},
    year={2025}
}

@article{RoboOS,
    title={RoboOS: A Hierarchical Embodied Framework for Cross-Embodiment and Multi-Agent Collaboration},
    author={Tan, Huajie and Hao, Xiaoshuai and Chi, Cheng and Lin, Minglan and Lyu, Yaoxu and Cao, Mingyu and Liang, Dong and Chen, Zhuo and Lyu, Mengsi and Peng, Cheng and He, Chenrui and Ao, Yulong and Lin, Yonghua and Wang, Pengwei and Wang, Zhongyuan and Zhang, Shanghang},
    journal={arXiv preprint arXiv:2505.03673},
    year={2025}
}

@article{zhou2025roborefer,
    title={RoboRefer: Towards Spatial Referring with Reasoning in Vision-Language Models for Robotics},
    author={Zhou, Enshen and An, Jingkun and Chi, Cheng and Han, Yi and Rong, Shanyu and Zhang, Chi and Wang, Pengwei and Wang, Zhongyuan and Huang, Tiejun and Sheng, Lu and others},
    journal={arXiv preprint arXiv:2506.04308},
    year={2025}
}

@article{Reason-RFT,
    title={Reason-rft: Reinforcement fine-tuning for visual reasoning},
    author={Tan, Huajie and Ji, Yuheng and Hao, Xiaoshuai and Lin, Minglan and Wang, Pengwei and Wang, Zhongyuan and Zhang, Shanghang},
    journal={arXiv preprint arXiv:2503.20752},
    year={2025}
}

@article{Code-as-Monitor,
    title={Code-as-Monitor: Constraint-aware Visual Programming for Reactive and Proactive Robotic Failure Detection},
    author={Zhou, Enshen and Su, Qi and Chi, Cheng and Zhang, Zhizheng and Wang, Zhongyuan and Huang, Tiejun and Sheng, Lu and Wang, He},
    journal={arXiv preprint arXiv:2412.04455},
    year={2024}
}
```

---

## 💬 Contact

If you have any questions, feel free to contact us via WeChat or RedNote.

<div align="center">
<img src="./assets/wechat.png" width="600" />
</div>
