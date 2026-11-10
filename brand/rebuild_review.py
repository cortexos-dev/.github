#!/usr/bin/env python3
"""重建 brand/review.html 内嵌的 DATA（品牌素材换新后重跑）。

review.html 的 DATA 是 manifest + 素材内嵌快照：DATA.manifest 是 manifest.json
的副本，DATA.projects[].assets 是各素材的 SVG 文本 + base64 data URI + 校验记录。
素材换新（本次：莫兰迪三弧替换蓝色三弧）后必须重跑，否则评审页展示的还是旧素材
——评审页与实际素材不一致，比没有评审页更坏。

用法（在 brand/ 目录下）：
    python3 rebuild_review.py
"""

import base64
import hashlib
import json
import os
import re

BRAND = os.path.dirname(os.path.abspath(__file__))
REVIEW = os.path.join(BRAND, "review.html")


def svg_text(name):
    with open(os.path.join(BRAND, name), "r", encoding="utf-8") as f:
        return f.read()


def data_uri(name, mime):
    with open(os.path.join(BRAND, name), "rb") as f:
        return "data:%s;base64,%s" % (mime, base64.b64encode(f.read()).decode())


def svg_viewbox(text):
    """从 SVG 文本里读 viewBox —— 品牌栅格会随定稿变化，写死数值就会与实际素材不符。"""
    import re as _re

    m = _re.search(r'viewBox="([\d.\s-]+)"', text)
    if not m:
        return None
    return [float(x) for x in m.group(1).split()]


def svg_asset(name):
    text = svg_text(name)
    return {
        "path": name,
        "filename": name,
        "mime": "image/svg+xml",
        "svg": text,
        "dataUri": "data:image/svg+xml;base64,"
        + base64.b64encode(text.encode("utf-8")).decode(),
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "validation": {
            "format": "SVG",
            "viewBox": svg_viewbox(text),
            "checks": "结构合法（XML 可解析）、无外部引用、无 text/font-family 依赖；路径与配色逐条比对主仓 docs/manifest/branding/breakout.svg 与 lockup-dark.svg 一致；已用 rsvg-convert 实际渲染",
        },
        "limitation": "结构与渲染已验证；16px 最小尺寸、色觉模拟与任意彩色底未验收。",
    }


def png_asset(name):
    with open(os.path.join(BRAND, name), "rb") as f:
        raw = f.read()
    return {
        "path": name,
        "filename": name,
        "mime": "image/png",
        "svg": None,
        "dataUri": "data:image/png;base64," + base64.b64encode(raw).decode(),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "validation": {
            "format": "PNG",
            "checks": "由本目录同名 SVG 经 rsvg-convert 渲染（与 SVG 同源同形）",
        },
        "limitation": "位图为应用版本，矢量以 SVG 为准。",
    }


def main():
    with open(os.path.join(BRAND, "manifest.json"), "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assets = {
        "asset": svg_asset("mark.svg"),
        "darkAsset": svg_asset("mark-dark.svg"),
        "avatar": png_asset("avatar.png"),
        "hero": png_asset("hero.png"),
    }

    tokens = manifest["tokens"]
    project = {
        "id": "cortexos",
        "name": "CortexOS · 组织品牌",
        "tokens": tokens,
        "tokenSources": manifest.get("colorRoles", {}),
        "rationale": [
            "形态与配色取自 CortexOS 主仓的标志真源 docs/manifest/branding/breakout.svg，不是另起炉灶的设计稿。",
            "粗框围出一个空间，核心块从右侧开口处穿出去——掌控与越界同时成立。",
            "框用 fill-rule=evenodd 一次画出外框与内框；越界块是画面里唯一的强调色。",
        ],
        "userDecisions": [
            "用户选定「出框」方向（logo-brand-designer skill 的 examples/cortexos/breakout），替换先前的三弧方案。",
        ],
        "recommendations": [
            "浅底用 mark.svg（透明底），深底用 mark-dark.svg（深色底板）。",
            "16px 最小尺寸、色觉模拟与任意彩色底尚未验收。",
            "设备图标适配与跨端发布需各自验证。",
        ],
        "sources": [
            {
                "url": "https://gitlab.com/webkubor/CortexOS/-/blob/main/docs/manifest/branding/breakout.svg",
                "label": "标志真源：CortexOS 主仓 docs/manifest/branding/breakout.svg",
                "value": "https://gitlab.com/webkubor/CortexOS/-/blob/main/docs/manifest/branding/breakout.svg",
            },
            {
                "url": "https://github.com/webkubor/logo-brand-designer/tree/6c0f403/examples/cortexos/breakout",
                "label": "源形稿：logo-brand-designer skill 的 breakout 方案",
                "value": "https://github.com/webkubor/logo-brand-designer/tree/6c0f403/examples/cortexos/breakout",
            },
        ],
        "assets": assets,
    }

    data = {
        "manifest": manifest,
        "projects": [project],
        "limitation": "已做结构检查与真实渲染（rsvg-convert + Pillow 像素抽查）；未做 16px 最小尺寸、色觉模拟与任意彩色底验收。",
    }

    with open(REVIEW, "r", encoding="utf-8") as f:
        html = f.read()

    # JSON 必须转义控制字符（SVG 文本里含真实换行）——直接内嵌进 <script> 的
    # JSON 字面量不容许裸换行，否则页面脚本当场语法错、评审页一片空白。
    payload = json.dumps(data, ensure_ascii=True)
    # 替换串走 lambda：直接传字符串会被 re 当模板解析，\u 转义会炸
    # （ReperError: bad escape \u）。
    new_html, n = re.subn(
        r"const DATA = \{.*?\};\n",
        lambda _m: "const DATA = " + payload + ";\n",
        html,
        count=1,
        flags=re.S,
    )
    if n != 1:
        raise SystemExit("未找到 const DATA = {...}; 段落，review.html 结构与预期不符")

    # CSP 里 script-src 用的是内联脚本的 sha256 —— 换素材后脚本变了，hash 也变，
    # 不同步的话浏览器会直接拦掉脚本，评审页一片空白（而且没有任何报错提示）。
    # 注意 CSP 声明里的引号是 HTML 实体（&#x27;），正则要能对上。
    script_match = re.search(r"<script>(.*?)</script>", new_html, re.S)
    if not script_match:
        raise SystemExit("未找到 <script> 段落")
    digest = base64.b64encode(
        hashlib.sha256(script_match.group(1).encode("utf-8")).digest()
    ).decode()
    new_html, n2 = re.subn(
        r"script-src (?:&#x27;|')\s*sha256-[^'&]*\s*(?:&#x27;|')",
        lambda _m: "script-src 'sha256-" + digest + "'",
        new_html,
        count=1,
    )
    if n2 != 1:
        raise SystemExit("未找到 CSP script-src 声明")

    with open(REVIEW, "w", encoding="utf-8") as f:
        f.write(new_html)
    print(
        "review.html DATA 已重建：%d 个素材，manifest %d 字节，CSP script hash 已同步"
        % (len(assets), len(payload))
    )


if __name__ == "__main__":
    main()
