#!/usr/bin/env python3
"""生成 brand/hero.svg / hero.png —— 组织主页横幅。

组成（全部来自品牌真源，无系统字体依赖）：
  · 标志 + 「CortexOS」字标 → CortexOS 主仓 docs/manifest/branding/lockup-dark.svg
    （字标已由 Inter Latin SemiBold 转成 SVG 路径）
  · 副标题「An operating layer for agents and tools.」→ 本脚本用同一份
    Inter 字体转成路径（真源 README 明确要求不依赖运行时字体）

用法（在仓根跑）：
    /tmp/fontenv/bin/python brand/build_hero.py

需要 fontTools（'fonttools[woff]'）与 rsvg-convert。
"""
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)

# 真源位置：CortexOS 主仓 docs/manifest/branding/。
# 该目录同时被拷到本仓 brand/branding-source/ 作为可追溯副本。
SOURCE_DIR = HERE / "branding-source"
LOCKUP = SOURCE_DIR / "lockup-dark.svg"
FONT = SOURCE_DIR / "fonts" / "Inter-Latin-600.woff2"

TAGLINE = "An operating layer for agents and tools."
W, H = 1280, 360
SURFACE = "#0B0C10"
TAGLINE_FILL = "#9AA0AA"


def load_font():
    return TTFont(FONT)


def glyph_paths(font, text, scale, cursor_x, baseline_y, fill, letter_gap=-2.0):
    """把一段文字转成 SVG path 列表（字体轮廓，不依赖运行时字体）。"""
    glyphs = font.getGlyphSet()
    mapping = font.getBestCmap()
    out = []
    cursor = cursor_x
    for character in text:
        name = mapping[ord(character)]
        pen = SVGPathPen(glyphs)
        glyphs[name].draw(pen)
        d = pen.getCommands()
        if d:
            out.append(
                {
                    "d": d,
                    "fill": fill,
                    "transform": f"translate({cursor:.4f} {baseline_y}) scale({scale:.8f} {-scale:.8f})",
                }
            )
        cursor += font["hmtx"].metrics[name][0] * scale + letter_gap
    return out, cursor


def build():
    font = load_font()
    scale = 96 / font["head"].unitsPerEm

    root = ET.Element(f"{{{NS}}}svg", {
        "viewBox": f"0 0 {W} {H}", "width": str(W), "height": str(H),
        "role": "img", "aria-labelledby": "hero-title hero-desc",
    })
    ET.SubElement(root, f"{{{NS}}}title", {"id": "hero-title"}).text = "CortexOS — An operating layer for agents and tools"
    ET.SubElement(root, f"{{{NS}}}desc", {"id": "hero-desc"}).text = (
        "深色底板上的出框标志与 CortexOS 字标，字标为 Inter SemiBold 转路径，不依赖系统字体。"
    )

    defs = ET.SubElement(root, f"{{{NS}}}defs")
    clip = ET.SubElement(defs, f"{{{NS}}}clipPath", {"id": "hero-clip"})
    ET.SubElement(clip, f"{{{NS}}}rect", {"width": str(W), "height": str(H), "rx": "24"})

    surface_group = ET.SubElement(root, f"{{{NS}}}g", {"clip-path": "url(#hero-clip)"})
    ET.SubElement(surface_group, f"{{{NS}}}rect", {
        "width": str(W), "height": str(H), "fill": SURFACE,
    })

    # ── lockup：标志 + 字标（整段搬自真源，不重画） ──────────────────────
    lockup = ET.parse(LOCKUP).getroot()
    lockup_title = lockup.find(f"{{{NS}}}title")
    if lockup_title is not None:
        lockup.remove(lockup_title)

    # 真源的渐变 id 是 lockup-dark-*，本文件内唯一，直接沿用不冲突。
    # 尺寸：lockup 是 700×220（标志 200 + 字标约 460）。
    lockup_scale = 1.05
    lockup_x, lockup_y = 56, 46
    lockup_group = ET.SubElement(surface_group, f"{{{NS}}}g", {
        "transform": f"translate({lockup_x} {lockup_y}) scale({lockup_scale})",
    })
    for child in list(lockup):
        lockup_group.append(child)

    # ── 副标题：同一份 Inter 转路径（不依赖系统字体） ────────────────────
    # 副标题排在字标**正下方**，左边与字标起点对齐（真源里字标第一个字形起点
    # 是 x=240，见 lockup-dark.svg 的 translate(240.0000 142)）。字号 23、
    # 正常字距（0，不用字标的 -2 收紧——那是给大字标题排的，副标题用会挤）。
    #
    # 基线按**字形实际边界**算，不按 lockup 画布高度（220）：画布底部有大片
    # 空白——字标实际只占真源内 y=71..143（基线 142，descender 到 143），
    # 按画布排会把副标题甩到画面底部（实测基线曾落在 y=308，与字标相距
    # 113px，视觉脱节）。字标实际底缘在 hero 内 = 46 + 143.1*1.05 ≈ 196。
    tagline_scale = 23 / font["head"].unitsPerEm
    wordmark_x = lockup_x + 240 * lockup_scale
    wordmark_bottom = lockup_y + 143.1 * lockup_scale  # ≈ 196
    tagline_paths, _ = glyph_paths(
        font,
        TAGLINE,
        tagline_scale,
        wordmark_x,
        wordmark_bottom + 44,
        TAGLINE_FILL,
        letter_gap=0.0,
    )
    for p in tagline_paths:
        ET.SubElement(surface_group, f"{{{NS}}}path", {
            "d": p["d"], "fill": p["fill"], "transform": p["transform"],
        })

    ET.indent(root, space="  ")
    out = HERE / "hero.svg"
    out.write_text(ET.tostring(root, encoding="unicode") + "\n", encoding="utf-8")
    print(f"hero.svg 已生成：{out}")

    png = HERE / "hero.png"
    subprocess.run(["rsvg-convert", "-w", str(W), "-h", str(H), str(out), "-o", str(png)], check=True)
    print(f"hero.png 已生成：{png}")


if __name__ == "__main__":
    build()
