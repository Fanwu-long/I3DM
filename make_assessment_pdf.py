# -*- coding: utf-8 -*-
"""实验室实习考核 · 问题2 · 一页版"""
from __future__ import annotations

from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "实验室实习考核_问题2_一页版.pdf"
OUT_ALIAS = ROOT / "I3DM_Q2_onepage.pdf"
SHOW = ROOT / "results_showcase"

INK = HexColor("#1A2330")
MUTED = HexColor("#5C6773")
ACCENT = HexColor("#0F6E82")
SOFT = HexColor("#F3F7F8")
LINE = HexColor("#D7DEE4")
HEAD_BG = HexColor("#0F6E82")

pdfmetrics.registerFont(TTFont("YaHei", r"C:\Windows\Fonts\msyh.ttc", subfontIndex=0))
pdfmetrics.registerFont(TTFont("YaHeiBold", r"C:\Windows\Fonts\msyhbd.ttc", subfontIndex=0))


def P(name, font="YaHei", size=9, leading=14, color=INK, align=TA_JUSTIFY, before=0, after=4):
    return ParagraphStyle(
        name,
        fontName=font,
        fontSize=size,
        leading=leading,
        textColor=color,
        alignment=align,
        spaceBefore=before,
        spaceAfter=after,
    )


def fit(path: Path, max_w, max_h) -> Image:
    from PIL import Image as PILImage

    with PILImage.open(path) as im:
        w, h = im.size
    r = min(max_w / w, max_h / h)
    return Image(str(path), width=w * r, height=h * r, hAlign="CENTER")


def build():
    st_title = P("title", "YaHeiBold", 14, 20, INK, TA_CENTER, 0, 2)
    st_kicker = P("kicker", "YaHei", 8.5, 12, ACCENT, TA_CENTER, 0, 2)
    st_h = P("h", "YaHeiBold", 10.5, 15, ACCENT, TA_LEFT, 8, 3)
    st_body = P("body", "YaHei", 9, 14.2, INK, TA_LEFT, 0, 4)
    st_cap = P("cap", "YaHei", 8, 11, MUTED, TA_CENTER, 1, 2)
    st_cell = P("cell", "YaHei", 8, 11.5, INK, TA_LEFT, 0, 0)
    st_foot = P("foot", "YaHei", 7.5, 10, MUTED, TA_CENTER, 2, 0)

    page_w, page_h = A4
    margin_x = 16 * mm
    cw = page_w - 2 * margin_x
    story = []

    story.append(Paragraph("实验室实习考核 · 问题 2", st_kicker))
    story.append(Paragraph("编程能力和 Debug 能力", st_title))
    story.append(HRFlowable(width="100%", thickness=0.8, color=ACCENT, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph(
        "项目是 I3DM，做长视频的三维一致生成。平台给本科生的配额是一张 A100、"
        "四个核、单个作业最多四个小时。我做的事情比较具体：把数据和评测收成能反复提交的流程，"
        "训练卡住的时候把显存问题查清楚。",
        st_body,
    ))

    img = SHOW / "005dd9a58df1ba3c" / "compare_grid.jpg"
    if img.exists():
        story.append(Spacer(1, 1 * mm))
        story.append(fit(img, cw, 48 * mm))
        story.append(Paragraph(
            "厨房场景的生成结果和真值对照。推理一共跑完 32 个场景，这个是其中一条。",
            st_cap,
        ))

    story.append(Paragraph("编程上具体做了什么", st_h))
    story.append(Paragraph(
        "数据这边，Re10K 没有下全量，按场景对应的文件下，量大概少了四分之三。"
        "解包之后切成 530 段、每段 77 帧，抽了 200 个样本核对张量形状，避免训到一半才发现格式不对。",
        st_body,
    ))
    story.append(Paragraph(
        "评测这边，一个场景要十几分钟，四个小时的墙钟塞不了多少条。"
        "我给评测脚本加了跳过：目录里已经有 video_combined.mp4 就不再跑。"
        "场景列表切成几块分别提交，32 个场景都出了视频，中间没有失败重跑。",
        st_body,
    ))
    story.append(Paragraph(
        "环境上锁了 torch 2.5.0、xformers 和 transformers 的组合，作业用 sbatch 交。"
        "官方 requirements 不能直接装全，训练脚本里还有没写进去的包。"
        "后来改成提交前把 import 扫一遍，缺的一次补上。",
        st_body,
    ))

    story.append(Paragraph("这个项目里的 Debug", st_h))
    story.append(Paragraph(
        "训练冒烟连着失败了几次。前面几次是缺包：pandas、easydict、wandb，补上就能往下走。"
        "包齐了以后报 CUDA 显存不够，77 帧一次前向大概 78.5 GiB，A100 是 80 GiB。",
        st_body,
    ))
    story.append(Paragraph(
        "我当时以为是 LoRA 太大，把 rank 从 1024 降到 512 再交一次。"
        "显存几乎没变。这个结果把「rank 太大」排除了，剩下能对上的是帧数："
        "激活主要跟序列长度走，不跟 rank 走。帧数减 1 要能被 4 整除，VAE 才压得动时间维，所以改成 41。"
        "rank 仍用 1024，这次 200 步跑完了。",
        st_body,
    ))

    hdr = [
        Paragraph("<font color='white'><b>作业</b></font>", st_cell),
        Paragraph("<font color='white'><b>看到的现象</b></font>", st_cell),
        Paragraph("<font color='white'><b>当时的判断</b></font>", st_cell),
    ]
    rows = [
        ["52883 到 53054", "先缺包，补完后 OOM", "依赖齐了，问题在显存"],
        ["53055", "rank 减半，占用几乎一样", "不是 LoRA 太大"],
        ["53057", "帧数改成 41，训练通过", "瓶颈在帧数"],
    ]
    data = [hdr]
    for r in rows:
        data.append([Paragraph(c, st_cell) for c in r])
    tbl = Table(data, colWidths=[32 * mm, 62 * mm, cw - 94 * mm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HEAD_BG),
        ("BACKGROUND", (0, 1), (-1, -1), SOFT),
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
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph(
        "降 rank 这一步本身没修好问题。它有用，是因为失败得很干净：只改了一个变量，现象不动，原因就缩小了。",
        st_body,
    ))

    story.append(Paragraph("平时也这样查问题", st_h))
    story.append(Paragraph(
        "上面是这一次的过程。别的代码、别的实验，我大致也按这个顺序，不限于显存。",
        st_body,
    ))
    story.append(Paragraph(
        "先把失败固定下来。同一个报错、同一组输入，能再出现一次，才开始改。"
        "然后猜一个原因，并且说清楚：如果猜对了，改完应该看到什么变化。"
        "一次只动一处。变化对不上，就丢掉这个猜测，不在同一次提交里连改好几个地方。",
        st_body,
    ))
    story.append(Paragraph(
        "范围尽量先缩到一层里：是环境缺包，是路径和数据，是模型前向，还是作业时间被杀掉。"
        "修完用一个小例子确认旧问题没了，再把任务放大。"
        "有效的配置和失败的作业号记下来，下次不用从头猜。",
        st_body,
    ))

    story.append(Paragraph("范围", st_h))
    story.append(Paragraph(
        "网络结构用的是官方实现，我改的是下载和切片、评测怎么续跑、以及训练帧数。"
        "四个小时一轮，论文里的 11000 步排不下，所以只做了 200 步，用来确认能反传、能存权重，不是拿来对最终指标。"
        "评测脚本本身也不算 FVD 和 PSNR，这次没有另写指标。",
        st_body,
    ))

    def on_page(c, doc):
        c.saveState()
        c.setFillColor(MUTED)
        c.setFont("YaHei", 7.5)
        c.drawString(margin_x, 8 * mm, "实验室实习考核 · 问题 2")
        c.drawRightString(page_w - margin_x, 8 * mm, str(doc.page))
        c.restoreState()

    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A4,
        leftMargin=margin_x,
        rightMargin=margin_x,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
        title="实验室实习考核 问题2",
    )
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    OUT_ALIAS.write_bytes(OUT.read_bytes())

    chat = ROOT / "实验室实习考核_问题2_聊天稿.txt"
    chat.write_text(
        "我想讲 I3DM，长视频里保持三维一致的那个工作。"
        "本科生配额是一张卡、四个核、单个作业四个小时。"
        "我主要做了两件具体的事：把数据和评测收成能反复交作业的流程，以及训练显存不够时把原因查出来。\n\n"
        "编程方面。数据没有下全量 Re10K，按场景对应的文件下，量少了大概四分之三，"
        "再切成 530 段 77 帧，抽 200 个样本对过张量形状。"
        "评测一个场景要十几分钟，四个小时塞不下，我就让脚本看到已经生成的视频就跳过，列表分块提交，32 个场景都出了结果。"
        "环境锁了 torch 2.5.0、xformers、transformers，用 sbatch 提交。"
        "官方依赖列表不全，训练前把 import 扫一遍再补包。\n\n"
        "这个项目里的 debug 集中在训练显存。"
        "缺包补完以后，77 帧前向大约 78.5 GiB，卡是 80 GiB。"
        "我先以为 LoRA 太大，rank 从 1024 降到 512，显存几乎没动，这个猜测就排除了。"
        "剩下对得上的是帧数。改成 41 帧，因为帧数减 1 要能被 4 整除，VAE 才压得动时间维。rank 仍是 1024，200 步这次过了。"
        "降 rank 没把问题修好，但它失败得很干净，只动了一个变量，所以才能把原因收到帧数上。\n\n"
        "平时查别的问题也差不多，不限于这次显存。"
        "先让同一个失败能再出现，再猜一个原因，并且事先说好改完应该看见什么。"
        "一次只改一处。对不上就换猜测，不在同一次里连改好几处。"
        "先分清是缺包、路径、前向，还是作业被时间杀掉。小例子确认之后再把任务放大，配置和失败的作业号记下来。\n\n"
        "网络用的是官方实现。我改的是数据、评测续跑和训练帧数。"
        "11000 步在四个小时一轮里排不开，200 步只是确认能反传、能存权重。"
        "需要的话我有一页对照，可以发。\n",
        encoding="utf-8",
    )
    print("OK", OUT)
    print("OK", chat)


if __name__ == "__main__":
    build()
