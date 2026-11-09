# CortexOS brand assets

组织品牌素材。**形状与配色不是另起炉灶的设计稿**——唯一真源是 CortexOS 手机端（cs-app）的标识资产：

- 标记本体：`cs-app/client/design/logo/logo-mark.svg`
- 深底版：`cs-app/client/design/logo/adaptive-foreground.svg` + `adaptive-background.svg`
- 生成源：`cs-app/client/design/logo/build_logo.py`（几何与配色的唯一出处）
- 配色出处：`cs-app/client/lib/theme.dart` 的 `AppTokens`

本目录的每个文件都是上述资产的应用版本。改形状或配色要先改 cs-app 真源并重跑 `build_logo.py`，再同步到这里——否则三端会漂移。

| 用途 | 素材 |
| --- | --- |
| 浅色背景中的透明标识 | [mark.svg](mark.svg) |
| 深色背景中的标识（莫兰迪玻璃底） | [mark-dark.svg](mark-dark.svg) |
| GitHub 组织头像，1024 × 1024 | [avatar.png](avatar.png) · [SVG](avatar.svg) |
| GitHub 首页横幅，1280 × 360 | [hero.png](hero.png) · [SVG](hero.svg) |
| 主题与尺寸离线预览 | 下载后打开 [review.html](review.html) |
| 颜色、来源与设计记录 | [manifest.json](manifest.json) |

## 标记

中心核 + 三段互不相接的弧，120° 旋转对称，三段之间各留 42° 缺口（缩到 24px 缺口仍能分开）。108 单位品牌栅格，中心 (54, 54)；核心半径 8.5、弧半径 22、弧宽 10.5。

## 配色

莫兰迪三色，来源是 `AppTokens` 的可读轨朝白提亮 0.52 的实算结果：

| 用途 | 色值 | 来源 |
| --- | --- | --- |
| 核心 | `#EFF4F7` | 标识专用近白核心色 |
| 鼠尾草弧 | `#B5B8AF` | `AppTokens.sage.readable`（#656C58）提亮 0.52 |
| 陶土弧 | `#C4B4A4` | `AppTokens.clay.readable`（#856341）提亮 0.52 |
| 藕粉弧 | `#C1B5B3` | `AppTokens.petal.readable`（#7D6460）提亮 0.52 |

深底版本沿用 `adaptive-background.svg` 的莫兰迪玻璃渐变（`#3C474F` / `#3D4148` / `#343E3F` 基底 + 藕粉与鼠尾草的低 alpha 氛围光）。

`AppTokens` 的双轨制在标识里也成立：弧与核心是「图标」，走可读轨；底面是「氛围渐变」，走气质轨（pigment 低 alpha 叠加）。

## 验收状态

- 已用 rsvg-convert 实际渲染 32 / 64 / 128 / 512 / 1024px，检查透明角块、包围盒与留白
- 标记路径与配色已与 `cs-app/client/design/logo/logo-mark.svg` 逐条比对一致
- 16px 最小尺寸、色觉模拟与任意彩色底未验收
- 横幅中的文字随 SVG 渲染，跨平台字体差异未单独处理
