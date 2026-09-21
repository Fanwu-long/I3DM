#!/bin/bash
#SBATCH --job-name=i3dm_eval
#SBATCH --partition=Students
#SBATCH --qos=qos_stu_default
#SBATCH --gres=gpu:A100:1
#SBATCH -c 4
#SBATCH -t 04:00:00
#SBATCH -o /home/scc/pb********/I3DM/eval_r%j.log

module load miniconda/py312
source $(conda info --base)/etc/profile.d/conda.sh
conda activate i3dm
export HF_ENDPOINT=https://hf-mirror.com
export HF_HUB_OFFLINE=1
cd /home/scc/pb********/I3DM

LIST=${1:-/home/scc/pb********/I3DM/data/processed/test/re10k_test_list.txt}
echo "Using list: $LIST"

accelerate launch --num_processes=1 scripts/eval_re10k.py \
  --metadata-path $LIST \
  --caption-path configs/re10k_test_captions.json \
  --checkpoint-path ./trained_models/step-11000.safetensors \
  --retrieval-ckpt-path ./trained_models/ckpt_0000000000016000.pt \
  --output-dir ./results/i3dm_re10K_eval_200