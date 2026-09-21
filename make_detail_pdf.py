# -*- coding: utf-8 -*-
"""I3DM 项目复现说明。三个小标题对应考核题的三问。"""
from __future__ import annotations

import subprocess
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "实验室实习考核_问题2.pdf"
SHOW = ROOT / "results_showcase"

INK = HexColor("#1A2330")
MUTED = HexColor("#5C6773")
ACCENT = HexColor("#0F6E82")
SOFT = HexColor("#F4F8F8")
LINE = HexColor("#D7DEE4")

pdfmetrics.registerFont(TTFont("YaHei", r"C:\Windows\Fonts\msyh.ttc", subfontIndex=0))
pdfmetrics.registerFont(TTFont("YaHeiBold", r"C:\Windows\Fonts\msyhbd.ttc", subfontIndex=0))
pdfmetrics.registerFont(TTFont("Consolas", r"C:\Windows\Fonts\consola.ttf"))


def sty(name, font="YaHei", size=9.5, leading=15, color=INK, align=TA_LEFT, before=0, after=3):
    return ParagraphStyle(
        name, fontName=font, fontSize=size, leading=leading, textColor=color,
        alignment=align, spaceBefore=before, spaceAfter=after,
    )


def code_block(filename: str, source: str, width, label_style, code_style):
    pre = Preformatted(source.rstrip() + "\n", code_style)
    box = Table([[pre]], colWidths=[width])
    box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), HexColor("#F3F6F8")),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ("LINEBEFORE", (0, 0), (0, -1), 2.2, ACCENT),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return KeepTogether([
        Paragraph(filename, label_style),
        box,
        Spacer(1, 1.6 * mm),
    ])


def mark(text: str, width, label_style):
    bar = Table(
        [[Paragraph(text, label_style)]],
        colWidths=[width],
    )
    bar.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), ACCENT),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return KeepTogether([
        Spacer(1, 3.2 * mm),
        bar,
        Spacer(1, 2.4 * mm),
    ])


def fit(path: Path, max_w, max_h) -> Image:
    from PIL import Image as PILImage
    with PILImage.open(path) as im:
        w, h = im.size
    r = min(max_w / w, max_h / h)
    return Image(str(path), width=w * r, height=h * r, hAlign="CENTER")


SCENES = [
    ("005dd9a58df1ba3c", "厨房"),
    ("04e4c841b349bf5c", "卧室"),
    ("01aaf4ebb084dc16", "走廊"),
]
STRIP_TIMES = (3, 12, 22)


def _grab_frame(video: Path, second: int, dest: Path):
    if dest.exists() and dest.stat().st_size > 0:
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.check_call(
        [
            "ffmpeg", "-y", "-ss", str(second), "-i", str(video),
            "-frames:v", "1", str(dest),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def ensure_strip(scene_id: str) -> Path:
    """上排生成、下排真值，各三帧，给 PDF 里看视频在动什么。"""
    from PIL import Image as PILImage
    from PIL import ImageDraw, ImageFont

    out = SHOW / "_strips" / f"{scene_id}.jpg"
    if out.exists() and out.stat().st_size > 0:
        return out
    folder = SHOW / scene_id
    frames = []
    for kind in ("gen", "gt"):
        row = []
        for t in STRIP_TIMES:
            dest = SHOW / "_strips" / "_raw" / f"{scene_id}_{kind}_{t}.png"
            _grab_frame(folder / f"{kind}_video_combined.mp4", t, dest)
            row.append(PILImage.open(dest).convert("RGB"))
        frames.append(row)
    fw, fh = frames[0][0].size
    gap = 8
    label_w = 72
    canvas = PILImage.new("RGB", (label_w + 3 * fw + 2 * gap, 2 * fh + gap), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 28, index=0)
    for r, (name, row) in enumerate(zip(("生成", "真值"), frames)):
        y = r * (fh + gap)
        draw.text((8, y + fh // 2 - 16), name, fill=(26, 35, 48), font=font)
        for c, im in enumerate(row):
            canvas.paste(im, (label_w + c * (fw + gap), y))
            im.close()
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, quality=90)
    return out


def attach_videos(pdf_path: Path):
    import pymupdf

    doc = pymupdf.open(pdf_path)
    existing = {item["name"] for item in doc.embfile_info()} if doc.embfile_count() else set()
    for scene_id, label in SCENES:
        folder = SHOW / scene_id
        for kind, kind_name in (("gen", "生成"), ("gt", "真值")):
            key = f"{scene_id}_{kind}"
            if key in existing:
                continue
            data = (folder / f"{kind}_video_combined.mp4").read_bytes()
            filename = f"{label}_{kind_name}.mp4"
            doc.embfile_add(key, data, filename=filename, ufilename=filename, desc=f"{label}{kind_name}视频")
    tmp = pdf_path.with_suffix(".attach.pdf")
    doc.save(tmp, deflate=True)
    doc.close()
    tmp.replace(pdf_path)


def build():
    S = {
        "kicker": sty("k", size=8.5, leading=12, color=ACCENT, align=TA_CENTER, after=2),
        "title": sty("t", "YaHeiBold", 15, 21, INK, TA_CENTER, 0, 2),
        "sub": sty("s", size=9, leading=13, color=MUTED, align=TA_CENTER, after=6),
        "h1": sty("h1", "YaHeiBold", 12, 16, INK, TA_LEFT, 9, 4),
        "h2": sty("h2", "YaHeiBold", 10.5, 15, ACCENT, TA_LEFT, 6, 2),
        "body": sty("body", size=9.5, leading=15.8, after=5),
        "cap": sty("cap", size=8, leading=11.5, color=MUTED, align=TA_CENTER, before=1, after=5),
        "cell": sty("cell", size=8.2, leading=12, after=0),
        "file": sty("file", size=7.6, leading=10, color=MUTED, before=1, after=1),
        "code": sty("code", "Consolas", 7.3, 9.6, INK, TA_LEFT, 0, 0),
        "mark": sty("mark", "YaHeiBold", 11, 15, HexColor("#FFFFFF"), TA_LEFT, 0, 0),
    }
    page_w, _ = A4
    mx = 16 * mm
    cw = page_w - 2 * mx
    story = []

    story.append(Paragraph("I3DM 项目复现", S["title"]))
    story.append(Paragraph("单张 A100 作业", S["sub"]))
    story.append(HRFlowable(width="100%", thickness=0.8, color=ACCENT, spaceBefore=1, spaceAfter=4))
    story.append(Paragraph(
        "下面是评测跑完的三条。对照图左列是生成，右列是真值。"
        "视频各抽了 3 秒、12 秒、22 秒三帧，上排生成，下排真值。"
        "厨房、卧室、走廊三条的完整视频都在这份 PDF 的附件里。",
        S["body"],
    ))
    for scene_id, label in SCENES:
        grid = SHOW / scene_id / "compare_grid.jpg"
        strip = ensure_strip(scene_id)
        block = []
        if grid.exists():
            block.append(fit(grid, cw, 92 * mm))
            block.append(Paragraph(f"{label}。左列生成，右列真值。", S["cap"]))
        block.append(fit(strip, cw, 42 * mm))
        block.append(Paragraph(f"{label}这条视频抽的三帧。", S["cap"]))
        story.append(KeepTogether(block))

    story.append(mark("问 1　哪些部分体现了编程能力", cw, S["mark"]))
    story.append(Paragraph(
        "<b>评测要能断了再续。</b>"
        "一个场景大约 14 分钟，一次交 16 个左右才不会顶满 4 小时，作业又经常排到一半被掐掉。"
        "我在每个场景开头看结果目录里有没有 video_combined.mp4，有就跳过，下一份作业从断的地方接，已经生成的不再算一遍。"
        "这样跑完之后，32 个场景的生成和真值都在。",
        S["body"],
    ))
    story.append(code_block(
        "scripts/eval_re10k.py",
        "if os.path.exists(os.path.join(save_results_dir, 'video_combined.mp4')):\n"
        "    print(f'==SKIP done== {scene_name}', flush=True); continue",
        cw, S["file"], S["code"],
    ))
    story.append(Paragraph(
        "<b>数据只准备后面真会读到的。</b>"
        "Re10K 的 test 是打包文件，index 能对上场景，评测实际用到 121 个，我就下这 121 个，没有按全量拉。"
        "官方站这边连不上，改走镜像，仓库也没有整份克隆。"
        "训练切了 530 段，当时每段还是 77 帧。改帧之前先抽了 200 个样本看形状，免得训到一半才发现长度对不上。",
        S["body"],
    ))
    story.append(Paragraph(
        "<b>环境按能跑来配，不按作者机器上的清单全装。</b>"
        "官方 requirements 是他们自己的环境 freeze 出来的，有些要编译的包装不上，transformers 太新还会把 torch 往上抬。"
        "我用的是 torch 2.5.0，xformers 跟这个版本走，transformers 停在 4.57.3。模型相关的类能 import，就用这套往下做评测和训练。",
        S["body"],
    ))
    story.append(mark("问 2　哪些部分体现了 Debug 能力", cw, S["mark"]))
    story.append(Paragraph(
        "训练是同一个脚本连续报了几次，每次只处理眼前这一层。",
        S["body"],
    ))
    story.append(Paragraph(
        "<b>先是缺包，而且不是一次报完。</b>"
        "52883 缺 pandas，53053 缺 easydict。补完这两次之后我扫过训练入口的 import，以为齐了，53054 还是漏了 wandb。"
        "wandb 装上，同一次作业才第一次跑进前向。",
        S["body"],
    ))
    story.append(Paragraph(
        "<b>前向 OOM 之后，我先怀疑 LoRA，用一次对照把它排掉。</b>"
        "77 帧、640×352，日志里大约 78.5 GiB，卡是 A100 80GB，还是装不下。"
        "rank 当时是 1024，我只把它降到 512，帧数不动，觉得显存至少该少一截。53055 就是这一次，结果还是 78.5 左右，这个方向就放下了。"
        "现在磁盘上的脚本是后来留下的，rank 已经写回 1024，--num_frames 仍是 77，不是 53055 那一版。",
        S["body"],
    ))
    story.append(code_block(
        "train_smoke.sbatch",
        "  --lora_rank 1024 \\\n"
        "  --num_frames 77 \\",
        cw, S["file"], S["code"],
    ))
    story.append(Paragraph(
        "<b>显存几乎不动，说明前向用的帧数不是 --num_frames 给的。</b>"
        "再往下看，训练读的是这批图自己有多少帧。",
        S["body"],
    ))
    story.append(code_block(
        "scripts/train_mem_keyframes_new.py",
        '"num_frames": data["target_src_image"].shape[0],',
        cw, S["file"], S["code"],
    ))
    story.append(Paragraph(
        "<b>帧数改在数据集里，而且不能写成 40。</b>"
        "原来 num_target_views 是 77，我改成 41，rank 加回 1024。",
        S["body"],
    ))
    story.append(code_block(
        "diffsynth/trainers/unified_dataset.py",
        "self.num_target_views = 41\n"
        "target_frames = target_data_json[\"frames\"][-self.num_target_views:]",
        cw, S["file"], S["code"],
    ))
    story.append(Paragraph(
        "pipeline 里时间长度是 (帧数减 1) 整除 4 再加 1。77 减 1 能被 4 整除，所以 77 在公式上是过得去的，不用它只是因为显存不够。"
        "40 帧过不去，因为 39 除不尽。41 减 1 等于 40，能过。"
        "53057 用 41 帧跑完 200 步，一步大约 12.6 秒，四个 checkpoint 都写下来了。",
        S["body"],
    ))
    story.append(code_block(
        "diffsynth/pipelines/wan_video_mem_new.py",
        "length = (num_frames - 1) // 4 + 1",
        cw, S["file"], S["code"],
    ))

    cell = S["cell"]
    header = [
        Paragraph("<font color='white'><b>作业</b></font>", cell),
        Paragraph("<font color='white'><b>只改了什么</b></font>", cell),
        Paragraph("<font color='white'><b>看到什么</b></font>", cell),
    ]
    raw = [
        ["53054", "补上 wandb 后，77 帧，rank 1024", "前向约 78.5 GiB，OOM"],
        ["53055", "只把 rank 降到 512", "显存几乎不动"],
        ["53057", "帧数改成 41，rank 回到 1024", "200 步跑完"],
    ]
    data = [header] + [[Paragraph(c, cell) for c in r] for r in raw]
    tbl = Table(data, colWidths=[22 * mm, 72 * mm, cw - 94 * mm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("BACKGROUND", (0, 1), (-1, -2), SOFT),
        ("BACKGROUND", (0, -1), (-1, -1), HexColor("#E7F4EF")),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(Spacer(1, 1 * mm))
    story.append(tbl)
    story.append(Paragraph(
        "53055 只动了 rank，帧数还是 77，所以显存对得上上一行。",
        S["cap"],
    ))

    loss = SHOW / "training_loss_curve.png"
    if loss.exists():
        story.append(fit(loss, cw * 0.78, 26 * mm))
        story.append(Paragraph(
            "200 步的 loss 是跳的。没有 NaN，梯度大约 2.1，权重能写下来。",
            S["cap"],
        ))

    story.append(Paragraph(
        "<b>还有一类和显存无关，是路径。</b>"
        "评测报过找不到文件。数据当时在登录节点的 /tmp 里，计算节点上看不见，挪到家目录之后这条就过了。"
        "我是先确认跑代码的那台机器能不能看见这个路径，再改位置。",
        S["body"],
    ))

    story.append(mark("问 3　一般的 debug 思路是怎样的", cw, S["mark"]))
    story.append(Paragraph(
        "报错我一般不急着改，先照原样再跑一遍，能复现才谈得上修。"
        "复现不了的话，我先看这次和上次差在哪，是环境变了、数据不在了，还是机器上还挂着别的作业，而不是马上去改刚刚怀疑的那一行。",
        S["body"],
    ))
    story.append(Paragraph(
        "<b>先看它停在哪一层，再决定动什么。</b>"
        "停在 import，就去补包、对版本，这个时候改学习率没有意义。"
        "报找不到文件，我先确认路径在不在、正在算的那台机器能不能看见它，再谈代码写得对不对。"
        "已经跑起来才崩，才轮到显存和张量形状。这三层我尽量不放进同一次修改里，不然过了也说不清是哪一层好的。",
        S["body"],
    ))
    story.append(Paragraph(
        "<b>一次只改一个地方，改之前先写下一句预期。</b>"
        "比如这一次显存应该下来，或者这个文件这次应该能找到。跑完没有出现这句话里的变化，这个方向就放下，不在同一处再叠一个参数。"
        "好几处一起改，就算过了我也分不清是哪一处起的作用。没对上的那次配置我会留着，翻日志比靠印象准。",
        S["body"],
    ))
    story.append(Paragraph(
        "<b>方向对了，先跑一小段，再把任务加大。</b>"
        "我不太拿曲线好不好看当唯一标准，有的量本来就会抖。"
        "一小段能走完、数不是乱的、结果能存下来，我才把规模放大。",
        S["body"],
    ))

    def on_page(c, doc):
        c.saveState()
        c.setFillColor(MUTED)
        c.setFont("YaHei", 7.5)
        c.drawString(mx, 8 * mm, "I3DM 项目复现")
        c.drawRightString(page_w - mx, 8 * mm, str(doc.page))
        c.restoreState()

    doc = SimpleDocTemplate(
        str(OUT), pagesize=A4,
        leftMargin=mx, rightMargin=mx, topMargin=13 * mm, bottomMargin=14 * mm,
        title="I3DM 项目复现",
    )
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    attach_videos(OUT)
    print("pages-check pending")
    print("OK", OUT)


if __name__ == "__main__":
    build()
