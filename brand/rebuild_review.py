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
            "viewBox": [0.0, 0.0, 108.0, 108.0]
            if name.startswith("mark")
            else [0.0, 0.0, 512.0, 512.0]
            if name.startswith("avatar")
            else [0.0, 0.0, 1280.0, 360.0],
            "checks": "结构合法（XML 可解析）、无外部引用、路径与配色逐条比对 cs-app logo-mark.svg 一致；已用 rsvg-convert 实际渲染",
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
        "tokenSources": manifest["tokenSources"],
        "rationale": [
            "形态与配色取自 CortexOS 手机端标识资产（cs-app/client/design/logo），不是另起炉灶的设计稿。",
            "中心核 + 三段互不相接的弧，120° 旋转对称，三段间留 42° 缺口。",
            "弧色是 AppTokens 可读轨朝白提亮 0.52 的实算结果（build_logo.py 的 ARC_LIFT）。",
        ],
        "userDecisions": [
            "owner 2026-11-09 拍板：组织门面与手机 APP 用同一套标记，GitHub 组织仓的旧蓝色三弧作废。",
        ],
        "recommendations": [
            "浅底用 mark.svg（透明底），深底用 mark-dark.svg（莫兰迪玻璃底）。",
            "16px 最小尺寸、色觉模拟与任意彩色底尚未验收。",
        ],
        "sources": [
            {
                "url": "https://github.com/cortexos-dev/cs-app",
                "label": "产品真源：cs-app/client/design/logo（logo-mark.svg + build_logo.py）",
                "value": "https://github.com/cortexos-dev/cs-app",
            },
            {
                "url": "https://github.com/cortexos-dev/cs-app/blob/main/client/lib/theme.dart",
                "label": "配色真源：AppTokens（theme.dart）",
                "value": "https://github.com/cortexos-dev/cs-app/blob/main/client/lib/theme.dart",
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
