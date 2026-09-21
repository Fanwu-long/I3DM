#!/bin/bash
#SBATCH --job-name=i3dm_smoke
#SBATCH --partition=Students
#SBATCH --qos=qos_stu_default
#SBATCH --gres=gpu:A100:1
#SBATCH -c 4
#SBATCH -t 02:00:00
#SBATCH -o /home/scc/pb********/I3DM/smoke_%j.log

module load miniconda/py312
source $(conda info --base)/etc/profile.d/conda.sh
conda activate i3dm
export HF_ENDPOINT=https://hf-mirror.com
export HF_HUB_OFFLINE=1
cd /home/scc/pb********/I3DM

accelerate launch --num_processes=1 scripts/eval_re10k.py \
  --metadata-path /home/scc/pb********/I3DM/data/smoke/test/re10k_test_list.txt \
  --caption-path configs/re10k_test_captions.json \
  --checkpoint-path ./trained_models/step-11000.safetensors \
  --retrieval-ckpt-path ./trained_models/ckpt_0000000000016000.pt \
  --output-dir ./results/smoke_test