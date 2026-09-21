#!/bin/bash
#SBATCH --job-name=i3dm_train_smoke
#SBATCH --partition=Students
#SBATCH --qos=qos_stu_default
#SBATCH --gres=gpu:A100:1
#SBATCH -c 4
#SBATCH -t 04:00:00
#SBATCH -o /home/scc/pb********/I3DM/train_smoke_%j.log

module load miniconda/py312
source $(conda info --base)/etc/profile.d/conda.sh
conda activate i3dm
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export HF_ENDPOINT=https://hf-mirror.com
export HF_HUB_OFFLINE=1
cd /home/scc/pb********/I3DM

accelerate launch --num_processes=1 scripts/train_mem_keyframes_new.py \
  --dataset_metadata_path /home/scc/pb********/I3DM/data/processed/train/full_list_F77_clips_smoke.txt \
  --dataset_caption_path /home/scc/pb********/I3DM/data/processed/train/caption_F77/video_captions_refined.json \
  --model_paths ./configs/model_conf_wan_fun_i2v_1.3b.json \
  --height 352 \
  --width 640 \
  --dataset_repeat 1 \
  --learning_rate 1e-4 \
  --num_epochs 1 \
  --remove_prefix_in_ckpt "pipe.dit." \
  --lora_base_model "dit" \
  --lora_target_modules "q,k,v,o,ffn.0,ffn.2" \
  --trainable_models "ref_conv,nvs_model" \
  --lora_rank 1024 \
  --num_frames 77 \
  --save_steps 50 \
  --dataset_num_workers 4 \
  --gradient_accumulation_steps 1 \
  --wandb_mode offline \
  --use_wandb \
  --output_path "./trained_models/smoke" \
  --wandb_run_name "smoke" \
  --wandb_notes "smoke"