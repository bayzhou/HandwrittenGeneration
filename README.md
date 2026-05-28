# HandInPaper - 手写文字放置工具

一个基于 PyQt6 的手写风格文字放置工具，可以在自定义背景图片上放置手写风格的文字块，支持多种手写效果和畸变调整。

A handwriting-style text placement tool based on PyQt6, allowing you to place handwritten text blocks on custom background images with various handwriting effects and distortion adjustments.

## 功能特性 / Features

### 手写字体 / Handwriting Fonts
- 8 种开源手写字体可选 / 8 open-source handwriting fonts available：
  - Ma Shan Zheng（马善政手写体）
  - Zhi Mang Xing（芝麻行草书）
  - Liu Jian Mao Cao（刘建毛草）
  - Long Cang（龙藏体）
  - ZCOOL KuaiLe（站酷快乐体）
  - ZCOOL QingKe HuangYou（站酷庆科黄油体）
  - ZCOOL XiaoWei（站酷小薇体）
  - Caveat Brush（英文手写体）

### 字体抖动效果 / Font Jitter Effects
- **弯曲度**：让横线竖线不再笔直，模拟手写抖动 / Bend: Makes lines uneven, simulating handwriting tremor
- **粗细变化**：笔画粗细不均匀，像真实书写 / Thickness: Uneven stroke thickness, like real writing
- **大小变化**：高低胖瘦微调，每个字略有不同 / Size: Subtle size variations for each character
- **位置偏移**：字符位置微小随机偏移 / Position: Minor random position offsets

### 字间距随机 / Random Character Spacing
- **最小/最大偏移**：设置字间距的随机范围 / Min/Max offset: Set random spacing range
- **随机大空格**：随机插入指定数量的大空格 / Extra spaces: Randomly insert large gaps
- 刷新按钮可重新生成随机效果 / Refresh button to regenerate random effects

### 涂改效果 / Scribble Effects
- **涂改比例**：0-100% 随机选择字符进行涂改 / Ratio: 0-100% random character scribbling
- **涂改方式** / Styles：
  - 覆盖 / Cover：用不规则形状覆盖原字后重写 / Cover original with irregular shapes
  - 划掉 / Strike：用歪曲的线条划掉原字后重写 / Strike through with wavy lines
  - 混合 / Mix：同时使用覆盖和划掉效果 / Combine both effects

### 畸变调整 / Distortion Adjustments
- **透视 X/Y**：模拟纸张倾斜的梯形畸变 / Perspective: Simulate paper tilt distortion
- **倾斜 X/Y**：剪切变换，模拟书写角度 / Shear: Simulate writing angle
- **旋转**：0-360 度旋转 / Rotation: 0-360 degrees
- **缩放 X/Y**：独立调整宽高比 / Scale: Independent width/height scaling

### 其他功能 / Other Features
- 拖放图片设置背景 / Drag & drop images for background
- 文字块可随意拖动摆放 / Drag text blocks freely
- 支持多行文本和自定义行间距 / Multi-line text with custom line spacing
- 保存/加载项目文件（.hip 格式）/ Save/Load project files (.hip format)
- 导出为 PNG/JPEG 图片 / Export as PNG/JPEG images
- 画布缩放（Ctrl+滚轮）/ Canvas zoom (Ctrl+scroll)
- 中英文界面切换 / Chinese/English UI switching

## 安装依赖 / Installation

```bash
pip install PyQt6
```

## 运行 / Run

```bash
python main.py
```

## 快捷键 / Shortcuts

| 快捷键 / Shortcut | 功能 / Function |
|--------|------|
| Ctrl+O | 打开背景图片 / Open background image |
| Ctrl+S | 保存项目 / Save project |
| Ctrl+L | 加载项目 / Load project |
| Ctrl+E | 导出图片 / Export image |
| Ctrl+T | 添加文字块 / Add text block |
| Delete | 删除选中文字块 / Delete selected block |
| Ctrl++ | 放大 / Zoom in |
| Ctrl+- | 缩小 / Zoom out |
| Ctrl+0 | 重置缩放 / Reset zoom |
| Ctrl+Q | 退出 / Exit |
| 双击文字块 / Double-click block | 编辑文字 / Edit text |

## 项目结构 / Project Structure

```
handinpaper/
├── main.py          # 主程序 / Main program
├── icon.svg         # 应用图标 (SVG) / App icon (SVG)
├── icon.png         # 应用图标 (PNG) / App icon (PNG)
├── requirements.txt # 依赖列表 / Dependencies
├── README.md        # 说明文档 / Documentation
└── fonts/           # 手写字体目录 / Fonts directory
    ├── MaShanZheng-Regular.ttf
    ├── ZhiMangXing-Regular.ttf
    ├── LiuJianMaoCao-Regular.ttf
    ├── LongCang-Regular.ttf
    ├── ZCOOLKuaiLe-Regular.ttf
    ├── ZCOOLQingKeHuangYou-Regular.ttf
    ├── ZCOOLXiaoWei-Regular.ttf
    └── CaveatBrush-Regular.ttf
```

## 使用技巧 / Usage Tips

1. **设置背景**：拖放图片到画布，或使用 文件 > 打开背景
   **Set background**: Drag & drop image to canvas, or File > Open Background

2. **添加文字**：点击"添加文字块"按钮，然后双击编辑文字
   **Add text**: Click "Add Text Block" button, then double-click to edit

3. **调整手写效果**：右侧面板可以调整字体抖动、字间距、涂改等参数
   **Adjust effects**: Right panel for font jitter, spacing, scribble settings

4. **匹配背景畸变**：使用透视和倾斜参数让文字与背景纸张的透视效果匹配
   **Match distortion**: Use perspective and shear to match background paper

5. **导出图片**：Ctrl+E 导出最终效果
   **Export**: Ctrl+E to export final result

6. **切换语言**：菜单 > 语言 > 中文/English
   **Switch language**: Menu > Language > 中文/English

## 许可证 / License

本项目使用的字体均为开源字体，遵循各自的开源许可证。
The fonts used in this project are open-source, following their respective licenses.
