# evidence_src — 源码与改动证据

本目录保存 I3DM 复现中涉及的关键源码文件，分为两类：**基线文件（`base_` 前缀）** 与 **自定义脚本（`scripts_` 前缀）**。

---

## 一、文件分类

### 1. 基线文件（`base_*.py`）— diffsynth 库的原始版本

这些是 **I3DM 所依赖的 diffsynth 库中对应文件的「改动前原始版本」**，作为基线备份保留，便于对照本次复现做了哪些修改。

| 文件 | 对应 diffsynth 原始路径 | 作用 |
|------|------------------------|------|
| `base_diffsynth_models_wan_scene_decoder_retrieval_occ.py` | `diffsynth/models/wan_scene_decoder_retrieval_occ.py` | 场景解码器 + 记忆检索模块（I3DM 核心创新点）|
| `base_diffsynth_pipelines_wan_video_mem_new.py` | `diffsynth/pipelines/wan_video_mem_new.py` | WanVideo 视频生成 pipeline（记忆注入版）|
| `base_diffsynth_trainers_unified_dataset.py` | `diffsynth/trainers/unified_dataset.py` | Re10K 统一数据集加载器 |

> **说明**：实际运行时，diffsynth 库内这三个文件已被修改以适配 I3DM 的记忆检索注入机制；`base_` 文件是修改前的原始副本，用于证明改动范围与可追溯性。修改主要集中在：场景解码器的检索逻辑、pipeline 的记忆注入流程、数据集的关键帧切片。

### 2. 自定义脚本（`scripts_*`）— 本次复现编写的入口与工具

| 文件 | 作用 |
|------|------|
| `scripts_eval_re10k.py` | **推理评测入口**。加载官方权重，逐场景生成 3D 一致性漫游视频，含断点续跑补丁（已有 `video_combined.mp4` 自动跳过）|
| `scripts_train_mem_keyframes_new.py` | **训练入口**。LoRA 微调 DiT + 训练记忆检索模块，支持 wandb 离线记录 |
| `scripts_frame_memory_retrieval.py` | 记忆检索模块实现（`KeyFrameMemoryBankLearnedOccRetrieval`）|
| `scripts_re10K_clips_process.py` | 训练数据切片：将 Re10K 场景切成 77 帧 clips |
| `scripts_train.sh` | 官方训练命令模板（含完整超参数）|

---

## 二、改动与原创性说明

- **`base_` 前缀文件**：来自第三方 diffsynth 库，非本人编写，仅作基线备份。
- **`scripts_` 前缀文件**：本次复现中编写/适配的脚本，其中 `eval_re10k.py` 和 `train_mem_keyframes_new.py` 基于 I3DM 官方脚本，加入了**断点续跑补丁**（评测）与**显存适配**（`num_target_views` 77→41，训练）。
- 完整改动背景与排错过程见 `../I3DM复现报告.md` §4.4（训练排错表）与 §7（9 项工程问题）。
