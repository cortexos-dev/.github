# CortexOS brand assets

组织品牌素材。标志本体来自 CortexOS 主仓的标志真源：

- **`docs/manifest/branding/breakout.svg`**（CortexOS 主仓，已合并 `a4c266d`）—— 「出框」标志
- 源形稿：`logo-brand-designer` skill 的 `examples/cortexos/breakout`（用户选定方向）
- 元数据：主仓 `docs/manifest/branding.json`

本目录的每个文件都是该标志的应用版本。改形状或配色要先改主仓真源，再同步到这里——否则各端会漂移。

| 用途 | 素材 |
| --- | --- |
| 浅色背景中的透明标识 | [mark.svg](mark.svg) |
| 深色背景中的标识（深色底板） | [mark-dark.svg](mark-dark.svg) |
| GitHub 组织头像，1024 × 1024 | [avatar.png](avatar.png) · [SVG](avatar.svg) |
| GitHub 首页横幅，1280 × 360 | [hero.png](hero.png) · [SVG](hero.svg) |
| 主题与尺寸离线预览 | 下载后打开 [review.html](review.html) |
| 颜色、来源与设计记录 | [manifest.json](manifest.json) |

## 标志：出框

粗框围出一个空间，核心块从右侧开口处穿出去——**掌控与越界同时成立**。

- 框：`fill-rule=evenodd` 一次画出外框与内框，右侧留出开口
- 越界块：`rect` 从开口伸出边界，是画面里唯一的强调色
- 栅格：200 × 200，`viewBox 0 0 200 200`

## 字标

「CortexOS」字标由 **Inter Latin SemiBold 转成 SVG 路径**，不依赖查看者的系统字体——换一台没装 Inter 的机器，字形不会走样。

- 真源：CortexOS 主仓 `docs/manifest/branding/lockup-dark.svg`（700 × 220，合入提交 `0d52b0f`）
- 本仓副本：[branding-source/](branding-source/)（含 Inter-Latin-600.woff2 与 OFL 许可）
- 深底版的 `OS` 用提亮紫 `#A99AFF` → `#B4A8FF`，改善深底上的小字对比
- 字标按字体 advance 固定收紧 2 单位排字（不用字偶距），因此与浏览器直接排版的 Inter 并非完全相同

## 配色

| 用途 | 色值 | 角色 |
| --- | --- | --- |
| 框渐变 | `#4F46E5` → `#7C3AED` | 品牌主色，靛蓝到紫，承载「空间 / 结构」 |
| 越界块渐变 | `#5EEAD4` → `#22D3EE` | 唯一的强调色，小面积高饱和，只标出越界那一块 |
| 浅底文字 | `#14151B` | 横版字标文字色 |
| 深底文字 | `#F4F5F8` | 深底横版字标文字色 |
| 深底字标 OS | `#A99AFF` → `#B4A8FF` | 深底版的提亮紫，改善小字对比 |
| 深底板 | `#0B0C10` | 深底应用（mark-dark / avatar / hero）底板 |

## 横幅

`hero.svg`（1280 × 360）= 深底板 + 出框标志 + Inter 路径字标 + 副标题。

- 字标整段搬自 `lockup-dark.svg`，**不重画、不改色、不改几何**
- 副标题「An operating layer for agents and tools.」用同一份 Inter 转路径，
  23px、正常字距（0），左边与字标起点对齐（真源里字标首字起点 x=240），置于字标下方、不压标志
- 整个横幅不含 `text` / `tspan` 元素，也不含 `font-family` 引用 → 跨系统渲染一致
- 重新生成：`/tmp/fontenv/bin/python brand/build_hero.py`（需要 fontTools[woff] 与 rsvg-convert）

## 验收状态

- 已用 rsvg-convert 实际渲染 32 / 64 / 128 / 512 / 1024px，检查透明角块、包围盒与留白
- 浅底 `#FFFFFF` 与深底 `#0B0C10` 下的 32px 均已实际查看，结构可辨
- 已过视觉模型盲审：未被识别为常见通用图标件，24px 可辨主结构，换名测试不成立
- 横幅：XML 合法；真源 10 个图元在 hero 中零缺失；全部渐变 id 与色值原样保留；
  标志与字标按 hero 的变换对齐后逐像素比对，差异 1.9%（仅缩放重采样舍入）；
  Chrome headless 实际渲染已看图确认
- 16px 最小尺寸、纹理底、任意彩色底与色觉模拟未验收
- 设备图标适配（圆角方底板 / Android adaptive / iOS）与跨端发布未完成，需各自验证
