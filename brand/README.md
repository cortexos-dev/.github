# CortexOS brand assets

三段弧线围绕共同中心，表达工具连接与协作上下文。本次制作的新标识；这一解释不代表项目既有的品牌历史。

| 用途 | 素材 |
| --- | --- |
| 浅色背景中的透明标识 | [mark.svg](mark.svg) |
| 深色背景中的透明标识 | [mark-dark.svg](mark-dark.svg) |
| GitHub 组织头像，1024 × 1024 | [avatar.png](avatar.png) · [SVG](avatar.svg) |
| GitHub 首页横幅，1280 × 360 | [hero.png](hero.png) · [SVG](hero.svg) |
| 主题与尺寸离线预览 | 下载后打开 [review.html](review.html) |
| 颜色、来源与设计记录 | [manifest.json](manifest.json) |

可复用标识为 256 × 256 透明 SVG，不依赖字体、图片、脚本或外部资源。头像和横幅是独立应用版本，不能替代透明标识。

本次建议主色为 `#1D4ED8`，辅助色为 `#0284C7`、`#2563EB`；深底分别使用 `#3B82F6`、`#38BDF8`、`#60A5FA` 与近白中心点 `#F8FAFC`。这些值来自本次设计，并非从现有产品状态色推定。

已用 rsvg-convert 实际渲染 32、64、128、512px，检查 RGBA 透明角块、包围盒和留白；浅底 `#FFFFFF`、深底 `#0D1117` 的 32/64/128px 已目视检查。16px、色觉模拟和任意彩色底未验收。横幅中的文字使用独立 PNG 发布，以避免各平台字体差异。
