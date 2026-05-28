"""
手写文字放置工具 - HandInPaper
在自定义背景上放置手写风格文字块，支持畸变调整、随机涂改和字体抖动
"""

import sys
import os
import json
import math
import random
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QColorDialog, QFileDialog,
    QSpinBox, QDoubleSpinBox, QTextEdit, QGroupBox, QFormLayout,
    QComboBox, QScrollArea, QSplitter, QMessageBox, QSizePolicy,
    QSlider, QCheckBox, QToolBar, QStatusBar
)
from PyQt6.QtCore import (
    Qt, QPoint, QPointF, QRectF, QSize, pyqtSignal, QTimer,
    QMimeData, QUrl
)
from PyQt6.QtGui import (
    QPixmap, QFont, QColor, QPainter, QPen, QBrush, QTransform,
    QFontDatabase, QDrag, QCursor, QImage, QWheelEvent, QMouseEvent,
    QPaintEvent, QKeyEvent, QAction, QIcon, QClipboard, QPainterPath,
    QFontMetricsF
)
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import QByteArray

# 获取基础目录（兼容 PyInstaller 打包）
if getattr(sys, 'frozen', False):
    # PyInstaller 打包后，优先从 exe 同级目录找，找不到再从临时目录找
    _exe_dir = Path(sys.executable).parent
    if (_exe_dir / "fonts").exists():
        BASE_DIR = _exe_dir
    else:
        BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).parent

FONT_DIR = BASE_DIR / "fonts"

# 内嵌 SVG 图标（从 icon_data.py 导入，避免打包后丢失）
try:
    from icon_data import ICON_SVG
except ImportError:
    ICON_SVG = None

# 翻译字典 / Translation dictionary
TRANSLATIONS = {
    "zh": {
        "window_title": "HandInPaper - 手写文字放置工具",
        "menu_file": "文件",
        "menu_edit": "编辑",
        "menu_view": "视图",
        "menu_language": "语言",
        "open_background": "打开背景",
        "save_project": "保存项目",
        "load_project": "加载项目",
        "export_image": "导出图片",
        "exit": "退出",
        "add_text_block": "添加文字块",
        "delete_selected": "删除选中",
        "zoom_in": "放大",
        "zoom_out": "缩小",
        "reset_zoom": "重置缩放",
        "ready": "就绪",
        "selected_block": "已选中文字块",
        "added_block": "已添加新文字块",
        "deleted_block": "已删除文字块",
        "project_saved": "项目已保存",
        "project_loaded": "项目已加载",
        "image_exported": "图片已导出",
        "load_error": "加载项目失败",
        "error": "错误",
        "font_settings": "字体设置",
        "font": "字体",
        "font_size": "字号",
        "color": "颜色",
        "line_spacing": "行间距",
        "jitter_settings": "字体抖动",
        "enable_jitter": "启用抖动",
        "bend": "弯曲",
        "thickness": "粗细",
        "size": "大小",
        "offset": "偏移",
        "refresh_jitter": "刷新抖动",
        "scribble_settings": "涂改设置",
        "ratio": "比例",
        "style": "方式",
        "cover": "覆盖",
        "strike": "划掉",
        "mix": "混合",
        "refresh_scribble": "刷新涂改",
        "spacing_settings": "字间距随机",
        "min": "最小",
        "max": "最大",
        "extra_space": "大空格",
        "refresh_spacing": "刷新间距",
        "distortion_settings": "畸变设置",
        "perspective_x": "透视X",
        "perspective_y": "透视Y",
        "shear_x": "倾斜X",
        "shear_y": "倾斜Y",
        "rotation": "旋转",
        "scale_x": "缩放X",
        "scale_y": "缩放Y",
        "position": "位置",
        "add": "添加",
        "delete": "删除",
        "edit_text": "编辑文字",
        "input_text": "输入文字:",
        "drag_drop_hint": "拖放图片到此处设置背景\n或点击菜单 文件 > 打开背景",
        "toolbar_add": "添加文字块",
        "toolbar_zoom": "缩放:",
    },
    "en": {
        "window_title": "HandInPaper - Handwriting Text Tool",
        "menu_file": "File",
        "menu_edit": "Edit",
        "menu_view": "View",
        "menu_language": "Language",
        "open_background": "Open Background",
        "save_project": "Save Project",
        "load_project": "Load Project",
        "export_image": "Export Image",
        "exit": "Exit",
        "add_text_block": "Add Text Block",
        "delete_selected": "Delete Selected",
        "zoom_in": "Zoom In",
        "zoom_out": "Zoom Out",
        "reset_zoom": "Reset Zoom",
        "ready": "Ready",
        "selected_block": "Selected text block",
        "added_block": "New text block added",
        "deleted_block": "Text block deleted",
        "project_saved": "Project saved",
        "project_loaded": "Project loaded",
        "image_exported": "Image exported",
        "load_error": "Failed to load project",
        "error": "Error",
        "font_settings": "Font Settings",
        "font": "Font",
        "font_size": "Size",
        "color": "Color",
        "line_spacing": "Line Spacing",
        "jitter_settings": "Font Jitter",
        "enable_jitter": "Enable Jitter",
        "bend": "Bend",
        "thickness": "Thickness",
        "size": "Size",
        "offset": "Offset",
        "refresh_jitter": "Refresh Jitter",
        "scribble_settings": "Scribble Settings",
        "ratio": "Ratio",
        "style": "Style",
        "cover": "Cover",
        "strike": "Strike",
        "mix": "Mix",
        "refresh_scribble": "Refresh Scribble",
        "spacing_settings": "Random Spacing",
        "min": "Min",
        "max": "Max",
        "extra_space": "Extra Space",
        "refresh_spacing": "Refresh Spacing",
        "distortion_settings": "Distortion Settings",
        "perspective_x": "Perspective X",
        "perspective_y": "Perspective Y",
        "shear_x": "Shear X",
        "shear_y": "Shear Y",
        "rotation": "Rotation",
        "scale_x": "Scale X",
        "scale_y": "Scale Y",
        "position": "Position",
        "add": "Add",
        "delete": "Delete",
        "edit_text": "Edit Text",
        "input_text": "Input text:",
        "drag_drop_hint": "Drag & drop image here for background\nor use File > Open Background",
        "toolbar_add": "Add Text Block",
        "toolbar_zoom": "Zoom:",
    }
}

# 当前语言 / Current language
current_lang = "zh"

def tr(key):
    """获取翻译文本 / Get translated text"""
    return TRANSLATIONS.get(current_lang, TRANSLATIONS["zh"]).get(key, key)


def generate_scribble_path(x, y, width, height, complexity=8):
    """生成一个不规则的涂改路径，模拟真实涂改效果"""
    path = QPainterPath()

    start_x = x + width * 0.3 + random.random() * width * 0.4
    start_y = y + height * 0.3 + random.random() * height * 0.4
    path.moveTo(start_x, start_y)

    for i in range(complexity):
        cp1_x = x + random.random() * width * 1.2 - width * 0.1
        cp1_y = y + random.random() * height * 1.2 - height * 0.1
        cp2_x = x + random.random() * width * 1.2 - width * 0.1
        cp2_y = y + random.random() * height * 1.2 - height * 0.1
        end_x = x + random.random() * width * 1.2 - width * 0.1
        end_y = y + random.random() * height * 1.2 - height * 0.1
        path.cubicTo(cp1_x, cp1_y, cp2_x, cp2_y, end_x, end_y)

    path.closeSubpath()
    return path


def jitter_char_path(char_path, jitter_pixels, seed):
    """
    对字符路径进行轻微随机抖动，模拟手写不规则效果
    jitter_pixels: 实际像素级别的抖动量（通常 0.5-3 像素）
    """
    rng = random.Random(seed)

    bounds = char_path.boundingRect()
    if bounds.isEmpty():
        return char_path

    jittered = QPainterPath()

    i = 0
    while i < char_path.elementCount():
        elem = char_path.elementAt(i)

        if elem.type == QPainterPath.ElementType.MoveToElement:
            dx = (rng.random() - 0.5) * jitter_pixels
            dy = (rng.random() - 0.5) * jitter_pixels
            jittered.moveTo(elem.x + dx, elem.y + dy)

        elif elem.type == QPainterPath.ElementType.LineToElement:
            dx = (rng.random() - 0.5) * jitter_pixels
            dy = (rng.random() - 0.5) * jitter_pixels
            jittered.lineTo(elem.x + dx, elem.y + dy)

        elif elem.type == QPainterPath.ElementType.CurveToElement:
            if i + 2 < char_path.elementCount():
                elem2 = char_path.elementAt(i + 1)
                elem3 = char_path.elementAt(i + 2)
                jittered.cubicTo(
                    elem.x + (rng.random() - 0.5) * jitter_pixels,
                    elem.y + (rng.random() - 0.5) * jitter_pixels,
                    elem2.x + (rng.random() - 0.5) * jitter_pixels,
                    elem2.y + (rng.random() - 0.5) * jitter_pixels,
                    elem3.x + (rng.random() - 0.5) * jitter_pixels,
                    elem3.y + (rng.random() - 0.5) * jitter_pixels
                )
                i += 2

        elif elem.type == QPainterPath.ElementType.CurveToDataElement:
            pass

        i += 1

    return jittered


def create_jittered_char_painter_path(font, char, jitter_params, seed):
    """
    创建一个抖动后的字符 QPainterPath
    jitter_params: dict with keys:
        - bend: 弯曲度 (0-10)
        - size_var: 大小变化 (0-0.3)
        - position_var: 位置变化 (0-10)
    """
    rng = random.Random(seed)

    path = QPainterPath()
    path.addText(0, 0, font, char)

    if path.isEmpty():
        return path, 0, 0

    bounds = path.boundingRect()
    font_height = bounds.height() if bounds.height() > 0 else 20

    # 弯曲度：根据字号按比例计算像素抖动量
    # bend=10 时约为字号的 3%
    bend = jitter_params.get('bend', 3)
    jitter_pixels = (bend / 10.0) * font_height * 0.03
    if jitter_pixels > 0.1:
        path = jitter_char_path(path, jitter_pixels, seed + 1000)

    # 大小变化（高低胖瘦）
    size_var = jitter_params.get('size_var', 0.1)
    scale_x = 1.0 + (rng.random() - 0.5) * size_var
    scale_y = 1.0 + (rng.random() - 0.5) * size_var

    transform = QTransform()
    transform.translate(bounds.center().x(), bounds.center().y())
    transform.scale(scale_x, scale_y)
    transform.translate(-bounds.center().x(), -bounds.center().y())
    path = transform.map(path)

    # 位置偏移
    pos_var = jitter_params.get('position_var', 2)
    dx = (rng.random() - 0.5) * pos_var
    dy = (rng.random() - 0.5) * pos_var
    offset_transform = QTransform()
    offset_transform.translate(dx, dy)
    path = offset_transform.map(path)

    new_bounds = path.boundingRect()
    return path, new_bounds.width(), new_bounds.height()


class TextBlockWidget(QWidget):
    """可拖动、可编辑的文字块控件"""

    selected = pyqtSignal(object)
    position_changed = pyqtSignal()

    # 边框和控制点大小
    BORDER_MARGIN = 15
    CONTROL_SIZE = 10

    def __init__(self, text="双击编辑", x=100, y=100, parent=None):
        super().__init__(parent)
        self._text = text
        self._font_family = "Zhi Mang Xing"
        self._font_size = 24
        self._color = QColor(0, 0, 0)
        self._line_spacing = 1.2
        self._distortion_x = 0.0
        self._distortion_y = 0.0
        self._shear_x = 0.0
        self._shear_y = 0.0
        self._rotation = 0.0
        self._scale_x = 1.0
        self._scale_y = 1.0

        # 涂改参数
        self._scribble_ratio = 5.0
        self._scribble_style = "混合"

        # 字体抖动参数
        self._jitter_enabled = True
        self._jitter_bend = 15.0
        self._jitter_thickness = 0.0
        self._jitter_size_var = 0.65
        self._jitter_position_var = 3.0

        # 字间距随机参数
        self._char_spacing_min = 1.0
        self._char_spacing_max = 10.0
        self._extra_space_count = 2

        # 文本框宽度（用于自动换行）
        self._fixed_width = 0  # 0 表示自动宽度

        self._dragging = False
        self._resize_mode = None
        self._drag_start = QPoint()
        self._drag_start_geometry = None
        self._editing = False
        self._selected = False
        self._canvas_scale = 1.0
        self._logical_x = float(x)
        self._logical_y = float(y)
        self._logical_width = 120
        self._logical_height = 80

        # 为每个字符生成唯一的随机种子
        self._char_seeds = {}
        self._update_char_seeds()

        self._update_size()
        self._apply_logical_pos()
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.SizeAllCursor)

    def _update_char_seeds(self):
        """为文本中的每个字符生成唯一的随机种子"""
        self._char_seeds = {}
        for i, char in enumerate(self._text):
            if char not in '\n':
                self._char_seeds[i] = random.randint(0, 999999)

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        self._update_char_seeds()
        self._update_size()
        self.update()

    @property
    def font_family(self):
        return self._font_family

    @font_family.setter
    def font_family(self, value):
        self._font_family = value
        self._update_size()
        self.update()

    @property
    def font_size(self):
        return self._font_size

    @font_size.setter
    def font_size(self, value):
        self._font_size = max(8, min(200, value))
        self._update_size()
        self.update()

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        self.update()

    @property
    def line_spacing(self):
        return self._line_spacing

    @line_spacing.setter
    def line_spacing(self, value):
        self._line_spacing = max(0.5, min(3.0, value))
        self._update_size()
        self.update()

    @property
    def distortion_x(self):
        return self._distortion_x

    @distortion_x.setter
    def distortion_x(self, value):
        self._distortion_x = max(-1.0, min(1.0, value))
        self.update()

    @property
    def distortion_y(self):
        return self._distortion_y

    @distortion_y.setter
    def distortion_y(self, value):
        self._distortion_y = max(-1.0, min(1.0, value))
        self.update()

    @property
    def shear_x(self):
        return self._shear_x

    @shear_x.setter
    def shear_x(self, value):
        self._shear_x = max(-2.0, min(2.0, value))
        self.update()

    @property
    def shear_y(self):
        return self._shear_y

    @shear_y.setter
    def shear_y(self, value):
        self._shear_y = max(-2.0, min(2.0, value))
        self.update()

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        self._rotation = value % 360
        self.update()

    @property
    def scale_x(self):
        return self._scale_x

    @scale_x.setter
    def scale_x(self, value):
        self._scale_x = max(0.1, min(3.0, value))
        self._update_size()
        self.update()

    @property
    def scale_y(self):
        return self._scale_y

    @scale_y.setter
    def scale_y(self, value):
        self._scale_y = max(0.1, min(3.0, value))
        self._update_size()
        self.update()

    @property
    def scribble_ratio(self):
        return self._scribble_ratio

    @scribble_ratio.setter
    def scribble_ratio(self, value):
        self._scribble_ratio = max(0, min(100, value))
        self.update()

    @property
    def scribble_style(self):
        return self._scribble_style

    @scribble_style.setter
    def scribble_style(self, value):
        self._scribble_style = value
        self.update()

    @property
    def jitter_enabled(self):
        return self._jitter_enabled

    @jitter_enabled.setter
    def jitter_enabled(self, value):
        self._jitter_enabled = value
        self.update()

    @property
    def jitter_bend(self):
        return self._jitter_bend

    @jitter_bend.setter
    def jitter_bend(self, value):
        self._jitter_bend = max(0, min(30, value))
        self.update()

    @property
    def jitter_thickness(self):
        return self._jitter_thickness

    @jitter_thickness.setter
    def jitter_thickness(self, value):
        self._jitter_thickness = max(0, min(5, value))
        self.update()

    @property
    def jitter_size_var(self):
        return self._jitter_size_var

    @jitter_size_var.setter
    def jitter_size_var(self, value):
        self._jitter_size_var = max(0, min(1.0, value))
        self.update()

    @property
    def jitter_position_var(self):
        return self._jitter_position_var

    @jitter_position_var.setter
    def jitter_position_var(self, value):
        self._jitter_position_var = max(0, min(10, value))
        self.update()

    @property
    def char_spacing_min(self):
        return self._char_spacing_min

    @char_spacing_min.setter
    def char_spacing_min(self, value):
        self._char_spacing_min = max(-20, min(20, value))
        self.update()

    @property
    def char_spacing_max(self):
        return self._char_spacing_max

    @char_spacing_max.setter
    def char_spacing_max(self, value):
        self._char_spacing_max = max(-20, min(20, value))
        self.update()

    @property
    def extra_space_count(self):
        return self._extra_space_count

    @extra_space_count.setter
    def extra_space_count(self, value):
        self._extra_space_count = max(0, min(50, value))
        self.update()

    def _get_font(self, size=None):
        font = QFont(self._font_family, size or self._font_size)
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        return font

    def _wrap_text(self, text, font, max_width):
        """根据宽度自动换行 - 紧凑模式，写满才换行"""
        if max_width <= 0:
            return text.split('\n')

        temp_pixmap = QPixmap(1, 1)
        painter = QPainter(temp_pixmap)
        painter.setFont(font)
        fm = painter.fontMetrics()

        result_lines = []
        for line in text.split('\n'):
            if not line:
                result_lines.append('')
                continue

            current_line = ''
            for char in line:
                test_line = current_line + char
                # 测量下一个字符的宽度
                char_width = fm.horizontalAdvance(char)
                current_width = fm.horizontalAdvance(current_line) if current_line else 0
                # 如果当前行宽度加上新字符宽度超过最大宽度，则换行
                if current_width + char_width > max_width and current_line:
                    result_lines.append(current_line)
                    current_line = char
                else:
                    current_line = test_line
            if current_line:
                result_lines.append(current_line)

        painter.end()
        return result_lines

    def _calculate_text_rect(self):
        font = self._get_font()

        padding = 20
        # 如果有固定宽度，使用固定宽度减去padding作为文本宽度
        if self._fixed_width > 0:
            text_width = (self._fixed_width - padding * 2) / self._scale_x
            lines = self._wrap_text(self._text, font, text_width)
        else:
            lines = self._text.split('\n')

        if not lines:
            lines = ['']

        total_height = 0
        max_line_width = 0

        temp_pixmap = QPixmap(1, 1)
        painter = QPainter(temp_pixmap)
        painter.setFont(font)
        fm = painter.fontMetrics()

        for i, line in enumerate(lines):
            line_width = fm.horizontalAdvance(line)
            max_line_width = max(max_line_width, line_width)
            if i > 0:
                total_height += int(fm.height() * (self._line_spacing - 1))
            total_height += fm.height()

        painter.end()

        # 如果没有固定宽度，根据文本内容自动计算宽度
        if self._fixed_width <= 0:
            width = max(max_line_width + padding * 2, 80) * self._scale_x
        else:
            width = self._fixed_width

        height = (total_height + padding * 2) * self._scale_y

        return QRectF(0, 0, width, height)

    def _update_size(self):
        rect = self._calculate_text_rect()
        transform = self._get_transform()
        bound_rect = transform.mapRect(rect)
        size = bound_rect.size().toSize()
        # 增加额外空间确保边框和控制点不被裁剪
        margin = self.BORDER_MARGIN * 2 + self.CONTROL_SIZE
        # 确保最小尺寸
        min_width = 120
        min_height = 80
        self._logical_width = max(min_width, size.width() + margin)
        self._logical_height = max(min_height, size.height() + margin)
        self.setFixedSize(
            max(1, int(round(self._logical_width * self._canvas_scale))),
            max(1, int(round(self._logical_height * self._canvas_scale)))
        )

    def _get_transform(self):
        center = QPointF(self._logical_width / 2, self._logical_height / 2)
        transform = QTransform()
        transform.translate(center.x(), center.y())

        if self._distortion_x != 0 or self._distortion_y != 0:
            dx = self._distortion_x * 0.002
            dy = self._distortion_y * 0.002
            m11 = 1.0 + abs(self._distortion_y) * 0.2
            m12 = self._distortion_x * 0.4
            m21 = self._distortion_y * 0.4
            m22 = 1.0 + abs(self._distortion_x) * 0.2
            m13 = dx
            m23 = dy
            distortion = QTransform(m11, m12, m13, m21, m22, m23, 0, 0, 1)
            transform = transform * distortion

        transform.rotate(self._rotation)
        transform.shear(self._shear_x, self._shear_y)
        transform.scale(self._scale_x, self._scale_y)
        transform.translate(-center.x(), -center.y())
        return transform

    def _to_logical_point(self, pos):
        return QPointF(pos.x() / self._canvas_scale, pos.y() / self._canvas_scale)

    def set_canvas_scale(self, scale):
        self._canvas_scale = max(0.1, min(3.0, scale))
        self._update_size()
        self._apply_logical_pos()
        self.update()

    def set_logical_pos(self, x, y):
        self._logical_x = float(x)
        self._logical_y = float(y)
        self._apply_logical_pos()

    def _apply_logical_pos(self):
        self.move(
            int(round(self._logical_x * self._canvas_scale)),
            int(round(self._logical_y * self._canvas_scale))
        )

    def _draw_scribble_effect(self, painter, char_x, char_y, char_width, char_height, char_index):
        """绘制涂改效果 - 像写错字涂黑一样"""
        seed = self._char_seeds.get(char_index, 0)
        rng = random.Random(seed)

        # 使用字体颜色，不透明，覆盖原字
        scribble_color = QColor(self._color)

        if self._scribble_style == "覆盖" or self._scribble_style == "混合":
            # 绘制涂黑效果 - 变小变细，更像真实涂改
            for layer in range(rng.randint(1, 2)):
                complexity = rng.randint(4, 8)
                scribble_path = QPainterPath()

                # 从字符中心区域开始，更紧凑
                margin = char_width * 0.05
                center_x = char_x + char_width * 0.5
                center_y = char_y + char_height * 0.5
                start_x = center_x + (rng.random() - 0.5) * char_width * 0.6
                start_y = center_y + (rng.random() - 0.5) * char_height * 0.6
                scribble_path.moveTo(start_x, start_y)

                for i in range(complexity):
                    cp1_x = center_x + (rng.random() - 0.5) * char_width * 0.8
                    cp1_y = center_y + (rng.random() - 0.5) * char_height * 0.8
                    cp2_x = center_x + (rng.random() - 0.5) * char_width * 0.8
                    cp2_y = center_y + (rng.random() - 0.5) * char_height * 0.8
                    end_x = center_x + (rng.random() - 0.5) * char_width * 0.8
                    end_y = center_y + (rng.random() - 0.5) * char_height * 0.8
                    scribble_path.cubicTo(cp1_x, cp1_y, cp2_x, cp2_y, end_x, end_y)

                scribble_path.closeSubpath()

                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(scribble_color)
                painter.drawPath(scribble_path)

        if self._scribble_style == "划掉" or self._scribble_style == "混合":
            # 绘制划掉效果 - 变细的线条
            stroke_path = QPainterPath()

            side = rng.choice(['horizontal', 'diagonal', 'curve'])
            if side == 'horizontal':
                start_x = char_x - char_width * 0.15
                start_y = char_y + char_height * (0.3 + rng.random() * 0.4)
                end_x = char_x + char_width * 1.15
                end_y = char_y + char_height * (0.3 + rng.random() * 0.4)
            elif side == 'diagonal':
                start_x = char_x - char_width * 0.15
                start_y = char_y - char_height * 0.1
                end_x = char_x + char_width * 1.15
                end_y = char_y + char_height * 1.1
            else:
                start_x = char_x - char_width * 0.1
                start_y = char_y + char_height * (0.3 + rng.random() * 0.4)
                end_x = char_x + char_width * 1.1
                end_y = char_y + char_height * (0.3 + rng.random() * 0.4)

            stroke_path.moveTo(start_x, start_y)

            segments = rng.randint(3, 5)
            for i in range(1, segments + 1):
                t = i / segments
                base_x = start_x + (end_x - start_x) * t
                base_y = start_y + (end_y - start_y) * t
                offset_x = (rng.random() - 0.5) * char_width * 0.3
                offset_y = (rng.random() - 0.5) * char_height * 0.3

                if i < segments:
                    cp_x = base_x + offset_x
                    cp_y = base_y + offset_y
                    next_t = (i + 1) / segments
                    next_x = start_x + (end_x - start_x) * next_t + (rng.random() - 0.5) * char_width * 0.15
                    next_y = start_y + (end_y - start_y) * next_t + (rng.random() - 0.5) * char_height * 0.15
                    stroke_path.quadTo(cp_x, cp_y, next_x, next_y)

            # 变细的笔划
            pen_width = max(char_width * 0.15, char_height * 0.12) * (0.7 + rng.random() * 0.6)
            pen = QPen(scribble_color, pen_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(stroke_path)

    def _draw_jittered_char(self, painter, char, x, y, char_index, fm):
        """绘制带抖动效果的字符"""
        if not self._jitter_enabled or char in ' \t':
            painter.drawText(int(x), int(y), char)
            return

        seed = self._char_seeds.get(char_index, 0)
        font = painter.font()

        jitter_params = {
            'bend': self._jitter_bend,
            'size_var': self._jitter_size_var,
            'position_var': self._jitter_position_var
        }

        char_path, path_width, path_height = create_jittered_char_painter_path(
            font, char, jitter_params, seed
        )

        if char_path.isEmpty():
            painter.drawText(int(x), int(y), char)
            return

        bounds = char_path.boundingRect()
        draw_x = x
        draw_y = y - fm.descent()

        painter.save()
        painter.translate(draw_x, draw_y)

        # 粗细变化：用描边+填充混合，笔画宽度随机
        thickness_var = self._jitter_thickness
        rng = random.Random(seed + 500)

        if thickness_var > 0:
            # 填充绘制（主体）
            painter.setBrush(self._color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPath(char_path)

            # 描边叠加（模拟粗细变化）
            stroke_width = thickness_var * (0.3 + rng.random() * 0.7) * max(1, self._font_size / 30)
            pen = QPen(self._color, stroke_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(char_path)
        else:
            painter.setBrush(self._color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPath(char_path)

        painter.restore()

    def _get_text_lines(self):
        """获取自动换行后的文本行"""
        font = self._get_font()
        padding = 30
        if self._fixed_width > 0:
            text_width = (self._fixed_width - padding * 2) / self._scale_x
            return self._wrap_text(self._text, font, text_width)
        return self._text.split('\n')

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        painter.scale(self._canvas_scale, self._canvas_scale)
        self._paint_content(painter, include_selection=True)
        painter.end()

    def _paint_content(self, painter, include_selection=False):
        transform = self._get_transform()
        painter.setTransform(transform, True)

        font = self._get_font()
        painter.setFont(font)
        painter.setPen(self._color)

        lines = self._get_text_lines()
        if not lines:
            lines = ['']

        fm = painter.fontMetrics()
        padding = 30
        y = padding
        char_global_index = 0

        # 预生成额外空格的位置
        extra_space_positions = set()
        if self._extra_space_count > 0:
            total_chars = sum(len(line) for line in lines)
            if total_chars > 0:
                rng_space = random.Random(self._char_seeds.get(0, 0) + 77777)
                positions = rng_space.sample(range(total_chars), min(self._extra_space_count, total_chars))
                extra_space_positions = set(positions)

        for line_idx, line in enumerate(lines):
            if line_idx > 0:
                y += int(fm.height() * self._line_spacing)
            else:
                y += fm.ascent()

            x = padding
            for char_idx, char in enumerate(line):
                # 字间距随机偏移
                seed = self._char_seeds.get(char_global_index, 0)
                rng_spacing = random.Random(seed + 99999)
                spacing_offset = rng_spacing.uniform(self._char_spacing_min, self._char_spacing_max)
                x += spacing_offset

                # 额外空格（大幅度偏移）
                if char_global_index in extra_space_positions:
                    x += fm.averageCharWidth() * 1.5

                need_scribble = False
                if self._scribble_ratio > 0 and char not in ' \t':
                    rng = random.Random(seed + 12345)
                    need_scribble = rng.random() * 100 < self._scribble_ratio

                char_rect = fm.boundingRect(char)
                char_width = char_rect.width()
                char_height = fm.height()

                if need_scribble:
                    self._draw_scribble_effect(painter, x, y - fm.ascent(),
                                               char_width, char_height, char_global_index)
                    painter.setPen(self._color)
                    painter.setFont(font)
                    self._draw_jittered_char(painter, char, x, y,
                                             char_global_index, fm)
                else:
                    self._draw_jittered_char(painter, char, x, y,
                                             char_global_index, fm)

                x += char_rect.width()
                char_global_index += 1

        # 绘制选中边框
        if include_selection and self._selected:
            text_rect = self._calculate_text_rect()
            m = self.BORDER_MARGIN
            border_rect = QRectF(m, m, text_rect.width(), text_rect.height())

            # 绘制四条虚线边框
            painter.setPen(QPen(QColor(0, 120, 215), 2, Qt.PenStyle.DashLine))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(border_rect)

            # 绘制四个角的控制点
            painter.setPen(QPen(QColor(0, 120, 215), 1))
            painter.setBrush(QColor(255, 255, 255))
            cs = self.CONTROL_SIZE
            corners = [
                ('tl', border_rect.topLeft()),
                ('tr', border_rect.topRight()),
                ('bl', border_rect.bottomLeft()),
                ('br', border_rect.bottomRight())
            ]
            for _, corner in corners:
                painter.drawRect(QRectF(corner.x() - cs/2, corner.y() - cs/2, cs, cs))

            # 绘制四条边中点的控制点
            mid_points = [
                ('top', QPointF(border_rect.center().x(), border_rect.top())),
                ('bottom', QPointF(border_rect.center().x(), border_rect.bottom())),
                ('left', QPointF(border_rect.left(), border_rect.center().y())),
                ('right', QPointF(border_rect.right(), border_rect.center().y()))
            ]
            for _, mid in mid_points:
                painter.drawRect(QRectF(mid.x() - cs/2, mid.y() - cs/2, cs, cs))

    def _get_resize_mode(self, pos):
        """根据鼠标位置判断调整大小的模式"""
        pos = self._to_logical_point(pos)
        text_rect = self._calculate_text_rect()
        m = self.BORDER_MARGIN
        border_rect = QRectF(m, m, text_rect.width(), text_rect.height())
        cs = self.CONTROL_SIZE

        # 检查四个角
        if abs(pos.x() - border_rect.left()) < cs and abs(pos.y() - border_rect.top()) < cs:
            return 'tl'
        if abs(pos.x() - border_rect.right()) < cs and abs(pos.y() - border_rect.top()) < cs:
            return 'tr'
        if abs(pos.x() - border_rect.left()) < cs and abs(pos.y() - border_rect.bottom()) < cs:
            return 'bl'
        if abs(pos.x() - border_rect.right()) < cs and abs(pos.y() - border_rect.bottom()) < cs:
            return 'br'

        # 检查四条边
        if abs(pos.y() - border_rect.top()) < cs and border_rect.left() <= pos.x() <= border_rect.right():
            return 'top'
        if abs(pos.y() - border_rect.bottom()) < cs and border_rect.left() <= pos.x() <= border_rect.right():
            return 'bottom'
        if abs(pos.x() - border_rect.left()) < cs and border_rect.top() <= pos.y() <= border_rect.bottom():
            return 'left'
        if abs(pos.x() - border_rect.right()) < cs and border_rect.top() <= pos.y() <= border_rect.bottom():
            return 'right'

        return None

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.selected.emit(self)
            resize_mode = self._get_resize_mode(event.pos())

            if resize_mode and self._selected:
                self._resize_mode = resize_mode
                self._drag_start = self._to_logical_point(event.pos())
                self._drag_start_geometry = (
                    self._logical_x,
                    self._logical_y,
                    self._logical_width,
                    self._logical_height
                )
            else:
                self._dragging = True
                self._drag_start = event.pos()
                self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._resize_mode and self._drag_start_geometry:
            # 调整大小
            current_pos = self._to_logical_point(event.pos())
            dx = current_pos.x() - self._drag_start.x()
            dy = current_pos.y() - self._drag_start.y()
            sx, sy, sw, sh = self._drag_start_geometry

            new_x, new_y, new_w, new_h = sx, sy, sw, sh

            if 'right' in self._resize_mode:
                new_w = max(120, sw + dx)
            if 'left' in self._resize_mode:
                new_w = max(120, sw - dx)
                new_x = sx + sw - new_w
            if 'bottom' in self._resize_mode:
                new_h = max(80, sh + dy)
            if 'top' in self._resize_mode:
                new_h = max(80, sh - dy)
                new_y = sy + sh - new_h

            self._fixed_width = new_w
            self.set_logical_pos(new_x, new_y)
            self._update_size()
            self.position_changed.emit()
        elif self._dragging and not self._editing:
            # 拖动移动
            new_pos = self.mapToParent(event.pos() - self._drag_start)
            self.set_logical_pos(
                new_pos.x() / self._canvas_scale,
                new_pos.y() / self._canvas_scale
            )
            self.position_changed.emit()

        # 更新光标样式
        if self._selected and not self._dragging and not self._resize_mode:
            mode = self._get_resize_mode(event.pos())
            if mode in ('tl', 'br'):
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            elif mode in ('tr', 'bl'):
                self.setCursor(Qt.CursorShape.SizeBDiagCursor)
            elif mode in ('left', 'right'):
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            elif mode in ('top', 'bottom'):
                self.setCursor(Qt.CursorShape.SizeVerCursor)
            else:
                self.setCursor(Qt.CursorShape.SizeAllCursor)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._dragging = False
        self._resize_mode = None
        self._drag_start_geometry = None
        self.setCursor(Qt.CursorShape.SizeAllCursor)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        self._editing = True
        self._show_edit_dialog()

    def _show_edit_dialog(self):
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QDialogButtonBox

        dialog = QDialog(self)
        dialog.setWindowTitle(tr("edit_text"))
        dialog.setMinimumSize(500, 300)

        layout = QVBoxLayout(dialog)

        text_edit = QTextEdit()
        text_edit.setPlainText(self._text)
        text_edit.setFont(self._get_font(16))
        layout.addWidget(text_edit)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._text = text_edit.toPlainText()
            self._update_char_seeds()
            self._update_size()
            self.update()
        self._editing = False

    def set_selected(self, selected):
        self._selected = selected
        self.update()

    def get_properties(self):
        return {
            'text': self._text,
            'font_family': self._font_family,
            'font_size': self._font_size,
            'color': self._color.name(),
            'line_spacing': self._line_spacing,
            'distortion_x': self._distortion_x,
            'distortion_y': self._distortion_y,
            'shear_x': self._shear_x,
            'shear_y': self._shear_y,
            'rotation': self._rotation,
            'scale_x': self._scale_x,
            'scale_y': self._scale_y,
            'scribble_ratio': self._scribble_ratio,
            'scribble_style': self._scribble_style,
            'jitter_enabled': self._jitter_enabled,
            'jitter_bend': self._jitter_bend,
            'jitter_thickness': self._jitter_thickness,
            'jitter_size_var': self._jitter_size_var,
            'jitter_position_var': self._jitter_position_var,
            'char_spacing_min': self._char_spacing_min,
            'char_spacing_max': self._char_spacing_max,
            'extra_space_count': self._extra_space_count,
            'fixed_width': self._fixed_width,
            'x': self._logical_x,
            'y': self._logical_y
        }

    def set_properties(self, props):
        if 'text' in props:
            self._text = props['text']
        if 'font_family' in props:
            self._font_family = props['font_family']
        if 'font_size' in props:
            self._font_size = props['font_size']
        if 'color' in props:
            self._color = QColor(props['color'])
        if 'line_spacing' in props:
            self._line_spacing = props['line_spacing']
        if 'distortion_x' in props:
            self._distortion_x = props['distortion_x']
        if 'distortion_y' in props:
            self._distortion_y = props['distortion_y']
        if 'shear_x' in props:
            self._shear_x = props['shear_x']
        if 'shear_y' in props:
            self._shear_y = props['shear_y']
        if 'rotation' in props:
            self._rotation = props['rotation']
        if 'scale_x' in props:
            self._scale_x = props['scale_x']
        if 'scale_y' in props:
            self._scale_y = props['scale_y']
        if 'scribble_ratio' in props:
            self._scribble_ratio = props['scribble_ratio']
        if 'scribble_style' in props:
            self._scribble_style = props['scribble_style']
        if 'jitter_enabled' in props:
            self._jitter_enabled = props['jitter_enabled']
        if 'jitter_bend' in props:
            self._jitter_bend = props['jitter_bend']
        if 'jitter_thickness' in props:
            self._jitter_thickness = props['jitter_thickness']
        if 'jitter_size_var' in props:
            self._jitter_size_var = props['jitter_size_var']
        if 'jitter_position_var' in props:
            self._jitter_position_var = props['jitter_position_var']
        if 'char_spacing_min' in props:
            self._char_spacing_min = props['char_spacing_min']
        if 'char_spacing_max' in props:
            self._char_spacing_max = props['char_spacing_max']
        if 'extra_space_count' in props:
            self._extra_space_count = props['extra_space_count']
        if 'fixed_width' in props:
            self._fixed_width = props['fixed_width']
        if 'x' in props and 'y' in props:
            self.set_logical_pos(float(props['x']), float(props['y']))

        self._update_char_seeds()
        self._update_size()
        self._apply_logical_pos()
        self.update()


class CanvasWidget(QWidget):
    """画布控件 - 以背景原始尺寸为逻辑坐标，按按钮倍数缩放显示"""

    text_block_selected = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._background = None
        self._text_blocks = []
        self._selected_block = None
        self._scale = 1.0

        self.setAcceptDrops(True)
        self._update_size()

    def set_background(self, pixmap):
        self._background = pixmap
        self._update_size()
        self.update()

    def _logical_size(self):
        """返回未缩放的画布尺寸，优先使用背景原始尺寸。"""
        if self._background:
            return self._background.size()
        return QSize(800, 600)

    def _update_size(self):
        size = self._logical_size()
        self.setFixedSize(
            max(1, int(round(size.width() * self._scale))),
            max(1, int(round(size.height() * self._scale)))
        )

    def set_scale(self, new_scale):
        """设置画布缩放，只影响屏幕显示，不改变导出的逻辑坐标。"""
        self._scale = max(0.1, min(3.0, new_scale))
        self._update_size()
        for block in self._text_blocks:
            block.set_canvas_scale(self._scale)
        self.update()

    def add_text_block(self, block):
        self._text_blocks.append(block)
        block.setParent(self)
        block.set_canvas_scale(self._scale)
        block.selected.connect(self._on_block_selected)
        block.position_changed.connect(self.update)
        block.show()
        self._select_block(block)

    def remove_text_block(self, block):
        if block in self._text_blocks:
            self._text_blocks.remove(block)
            if self._selected_block == block:
                self._selected_block = None
            block.deleteLater()
            self.update()

    def _on_block_selected(self, block):
        self._select_block(block)

    def _select_block(self, block):
        if self._selected_block:
            self._selected_block.set_selected(False)
        self._selected_block = block
        if block:
            block.set_selected(True)
        self.text_block_selected.emit(block)

    def get_selected_block(self):
        return self._selected_block

    def get_all_blocks(self):
        return self._text_blocks.copy()

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        if self._background:
            painter.drawPixmap(self.rect(), self._background)
        else:
            painter.fillRect(self.rect(), QColor(240, 240, 240))
            painter.setPen(QColor(180, 180, 180))
            painter.setFont(QFont("Microsoft YaHei", 14))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                             tr("drag_drop_hint"))

        painter.end()

    def wheelEvent(self, event: QWheelEvent):
        event.ignore()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    self.set_background(pixmap)
                    break

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            clicked_on_block = False
            for block in reversed(self._text_blocks):
                if block.geometry().contains(event.pos()):
                    clicked_on_block = True
                    break
            if not clicked_on_block:
                self._select_block(None)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Delete and self._selected_block:
            self.remove_text_block(self._selected_block)
        elif event.key() == Qt.Key.Key_Escape:
            self._select_block(None)
        super().keyPressEvent(event)


class PropertyPanel(QWidget):
    """属性编辑面板"""

    property_changed = pyqtSignal()
    add_block_requested = pyqtSignal()
    delete_block_requested = pyqtSignal()

    def __init__(self, available_fonts=None, parent=None):
        super().__init__(parent)
        self._current_block = None
        self._available_fonts = available_fonts or []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # 字体选择
        font_group = QGroupBox("字体设置")
        font_layout = QGridLayout()
        font_layout.setSpacing(4)

        self.font_combo = QComboBox()
        self._load_fonts()
        self.font_combo.currentTextChanged.connect(self._on_font_changed)
        font_layout.addWidget(QLabel("字体:"), 0, 0)
        font_layout.addWidget(self.font_combo, 0, 1, 1, 3)

        font_layout.addWidget(QLabel("字号:"), 1, 0)
        self.size_spin = QSpinBox()
        self.size_spin.setRange(8, 200)
        self.size_spin.setValue(24)
        self.size_spin.valueChanged.connect(self._on_size_changed)
        font_layout.addWidget(self.size_spin, 1, 1)

        font_layout.addWidget(QLabel("颜色:"), 1, 2)
        self.color_btn = QPushButton()
        self.color_btn.setFixedSize(50, 24)
        self.color_btn.setStyleSheet("background-color: #000000;")
        self.color_btn.clicked.connect(self._on_color_clicked)
        font_layout.addWidget(self.color_btn, 1, 3)

        font_layout.addWidget(QLabel("行间距:"), 2, 0)
        self.spacing_spin = QDoubleSpinBox()
        self.spacing_spin.setRange(0.5, 3.0)
        self.spacing_spin.setValue(1.2)
        self.spacing_spin.setSingleStep(0.1)
        self.spacing_spin.valueChanged.connect(self._on_spacing_changed)
        font_layout.addWidget(self.spacing_spin, 2, 1)

        font_group.setLayout(font_layout)
        layout.addWidget(font_group)

        # 字体抖动设置
        jitter_group = QGroupBox("字体抖动")
        jitter_layout = QGridLayout()
        jitter_layout.setSpacing(4)

        self.jitter_enabled_check = QCheckBox("启用抖动")
        self.jitter_enabled_check.setChecked(True)
        self.jitter_enabled_check.toggled.connect(self._on_jitter_enabled_changed)
        jitter_layout.addWidget(self.jitter_enabled_check, 0, 0, 1, 2)

        jitter_layout.addWidget(QLabel("弯曲:"), 1, 0)
        self.jitter_bend_spin = QDoubleSpinBox()
        self.jitter_bend_spin.setRange(0, 30)
        self.jitter_bend_spin.setValue(15.0)
        self.jitter_bend_spin.setSingleStep(0.5)
        self.jitter_bend_spin.valueChanged.connect(self._on_jitter_bend_changed)
        jitter_layout.addWidget(self.jitter_bend_spin, 1, 1)

        jitter_layout.addWidget(QLabel("粗细:"), 1, 2)
        self.jitter_thickness_spin = QDoubleSpinBox()
        self.jitter_thickness_spin.setRange(0, 5)
        self.jitter_thickness_spin.setValue(0.0)
        self.jitter_thickness_spin.setSingleStep(0.2)
        self.jitter_thickness_spin.valueChanged.connect(self._on_jitter_thickness_changed)
        jitter_layout.addWidget(self.jitter_thickness_spin, 1, 3)

        jitter_layout.addWidget(QLabel("大小:"), 2, 0)
        self.jitter_size_spin = QDoubleSpinBox()
        self.jitter_size_spin.setRange(0, 1.0)
        self.jitter_size_spin.setValue(0.65)
        self.jitter_size_spin.setSingleStep(0.05)
        self.jitter_size_spin.valueChanged.connect(self._on_jitter_size_changed)
        jitter_layout.addWidget(self.jitter_size_spin, 2, 1)

        jitter_layout.addWidget(QLabel("偏移:"), 2, 2)
        self.jitter_position_spin = QDoubleSpinBox()
        self.jitter_position_spin.setRange(0, 10)
        self.jitter_position_spin.setValue(3.0)
        self.jitter_position_spin.setSingleStep(0.5)
        self.jitter_position_spin.valueChanged.connect(self._on_jitter_position_changed)
        jitter_layout.addWidget(self.jitter_position_spin, 2, 3)

        self.refresh_jitter_btn = QPushButton("刷新抖动")
        self.refresh_jitter_btn.clicked.connect(self._on_refresh_jitter)
        jitter_layout.addWidget(self.refresh_jitter_btn, 3, 0, 1, 4)

        jitter_group.setLayout(jitter_layout)
        layout.addWidget(jitter_group)

        # 涂改设置
        scribble_group = QGroupBox("涂改设置")
        scribble_layout = QGridLayout()
        scribble_layout.setSpacing(4)

        scribble_layout.addWidget(QLabel("比例:"), 0, 0)
        self.scribble_ratio_spin = QSpinBox()
        self.scribble_ratio_spin.setRange(0, 100)
        self.scribble_ratio_spin.setValue(5)
        self.scribble_ratio_spin.setSuffix("%")
        self.scribble_ratio_spin.valueChanged.connect(self._on_scribble_ratio_changed)
        scribble_layout.addWidget(self.scribble_ratio_spin, 0, 1)

        scribble_layout.addWidget(QLabel("方式:"), 0, 2)
        self.scribble_style_combo = QComboBox()
        self.scribble_style_combo.addItems(["覆盖", "划掉", "混合"])
        self.scribble_style_combo.setCurrentText("混合")
        self.scribble_style_combo.currentTextChanged.connect(self._on_scribble_style_changed)
        scribble_layout.addWidget(self.scribble_style_combo, 0, 3)

        self.refresh_scribble_btn = QPushButton("刷新涂改")
        self.refresh_scribble_btn.clicked.connect(self._on_refresh_scribble)
        scribble_layout.addWidget(self.refresh_scribble_btn, 1, 0, 1, 4)

        scribble_group.setLayout(scribble_layout)
        layout.addWidget(scribble_group)

        # 字间距随机设置
        spacing_group = QGroupBox("字间距随机")
        spacing_layout = QGridLayout()
        spacing_layout.setSpacing(4)

        spacing_layout.addWidget(QLabel("最小:"), 0, 0)
        self.spacing_min_spin = QDoubleSpinBox()
        self.spacing_min_spin.setRange(-20, 20)
        self.spacing_min_spin.setValue(1.0)
        self.spacing_min_spin.setSingleStep(0.5)
        self.spacing_min_spin.setSuffix("px")
        self.spacing_min_spin.valueChanged.connect(self._on_spacing_min_changed)
        spacing_layout.addWidget(self.spacing_min_spin, 0, 1)

        spacing_layout.addWidget(QLabel("最大:"), 0, 2)
        self.spacing_max_spin = QDoubleSpinBox()
        self.spacing_max_spin.setRange(-20, 20)
        self.spacing_max_spin.setValue(10.0)
        self.spacing_max_spin.setSingleStep(0.5)
        self.spacing_max_spin.setSuffix("px")
        self.spacing_max_spin.valueChanged.connect(self._on_spacing_max_changed)
        spacing_layout.addWidget(self.spacing_max_spin, 0, 3)

        spacing_layout.addWidget(QLabel("大空格:"), 1, 0)
        self.extra_space_spin = QSpinBox()
        self.extra_space_spin.setRange(0, 50)
        self.extra_space_spin.setValue(2)
        self.extra_space_spin.valueChanged.connect(self._on_extra_space_changed)
        spacing_layout.addWidget(self.extra_space_spin, 1, 1)

        self.refresh_spacing_btn = QPushButton("刷新间距")
        self.refresh_spacing_btn.clicked.connect(self._on_refresh_spacing)
        spacing_layout.addWidget(self.refresh_spacing_btn, 1, 2, 1, 2)

        spacing_group.setLayout(spacing_layout)
        layout.addWidget(spacing_group)

        # 畸变设置
        distort_group = QGroupBox("畸变设置")
        distort_layout = QGridLayout()
        distort_layout.setSpacing(4)

        distort_layout.addWidget(QLabel("透视X:"), 0, 0)
        self.distort_x_spin = QDoubleSpinBox()
        self.distort_x_spin.setRange(-1.0, 1.0)
        self.distort_x_spin.setValue(0.0)
        self.distort_x_spin.setSingleStep(0.05)
        self.distort_x_spin.valueChanged.connect(self._on_distort_x_changed)
        distort_layout.addWidget(self.distort_x_spin, 0, 1)

        distort_layout.addWidget(QLabel("透视Y:"), 0, 2)
        self.distort_y_spin = QDoubleSpinBox()
        self.distort_y_spin.setRange(-1.0, 1.0)
        self.distort_y_spin.setValue(0.0)
        self.distort_y_spin.setSingleStep(0.05)
        self.distort_y_spin.valueChanged.connect(self._on_distort_y_changed)
        distort_layout.addWidget(self.distort_y_spin, 0, 3)

        distort_layout.addWidget(QLabel("倾斜X:"), 1, 0)
        self.shear_x_spin = QDoubleSpinBox()
        self.shear_x_spin.setRange(-2.0, 2.0)
        self.shear_x_spin.setValue(0.0)
        self.shear_x_spin.setSingleStep(0.1)
        self.shear_x_spin.valueChanged.connect(self._on_shear_x_changed)
        distort_layout.addWidget(self.shear_x_spin, 1, 1)

        distort_layout.addWidget(QLabel("倾斜Y:"), 1, 2)
        self.shear_y_spin = QDoubleSpinBox()
        self.shear_y_spin.setRange(-2.0, 2.0)
        self.shear_y_spin.setValue(0.0)
        self.shear_y_spin.setSingleStep(0.1)
        self.shear_y_spin.valueChanged.connect(self._on_shear_y_changed)
        distort_layout.addWidget(self.shear_y_spin, 1, 3)

        distort_layout.addWidget(QLabel("旋转:"), 2, 0)
        self.rotation_spin = QDoubleSpinBox()
        self.rotation_spin.setRange(0, 360)
        self.rotation_spin.setValue(0.0)
        self.rotation_spin.setSingleStep(1.0)
        self.rotation_spin.valueChanged.connect(self._on_rotation_changed)
        distort_layout.addWidget(self.rotation_spin, 2, 1)

        distort_layout.addWidget(QLabel("缩放X:"), 2, 2)
        self.scale_x_spin = QDoubleSpinBox()
        self.scale_x_spin.setRange(0.1, 3.0)
        self.scale_x_spin.setValue(1.0)
        self.scale_x_spin.setSingleStep(0.1)
        self.scale_x_spin.valueChanged.connect(self._on_scale_x_changed)
        distort_layout.addWidget(self.scale_x_spin, 2, 3)

        distort_layout.addWidget(QLabel("缩放Y:"), 3, 0)
        self.scale_y_spin = QDoubleSpinBox()
        self.scale_y_spin.setRange(0.1, 3.0)
        self.scale_y_spin.setValue(1.0)
        self.scale_y_spin.setSingleStep(0.1)
        self.scale_y_spin.valueChanged.connect(self._on_scale_y_changed)
        distort_layout.addWidget(self.scale_y_spin, 3, 1)

        distort_group.setLayout(distort_layout)
        layout.addWidget(distort_group)

        # 位置信息
        pos_group = QGroupBox("位置")
        pos_layout = QFormLayout()

        self.pos_x_label = QLabel("0")
        pos_layout.addRow("X:", self.pos_x_label)

        self.pos_y_label = QLabel("0")
        pos_layout.addRow("Y:", self.pos_y_label)

        pos_group.setLayout(pos_layout)
        layout.addWidget(pos_group)

        # 操作按钮
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("添加文字块")
        self.add_btn.clicked.connect(self.add_block_requested.emit)
        btn_layout.addWidget(self.add_btn)

        self.del_btn = QPushButton("删除")
        self.del_btn.clicked.connect(self.delete_block_requested.emit)
        btn_layout.addWidget(self.del_btn)

        layout.addLayout(btn_layout)

        layout.addStretch()

        self._set_enabled(False)

    def _load_fonts(self):
        fonts = self._available_fonts or [
            "Ma Shan Zheng",
            "Zhi Mang Xing",
            "Liu Jian Mao Cao",
            "Long Cang",
            "ZCOOL KuaiLe",
            "ZCOOL QingKe HuangYou",
            "ZCOOL XiaoWei",
            "Caveat Brush",
        ]
        self.font_combo.addItems(fonts)

    def set_block(self, block):
        self._current_block = block
        if block:
            self._set_enabled(True)
            self._update_from_block(block)
        else:
            self._set_enabled(False)

    def _set_enabled(self, enabled):
        self.font_combo.setEnabled(enabled)
        self.size_spin.setEnabled(enabled)
        self.color_btn.setEnabled(enabled)
        self.spacing_spin.setEnabled(enabled)
        self.jitter_enabled_check.setEnabled(enabled)
        self.jitter_bend_spin.setEnabled(enabled)
        self.jitter_thickness_spin.setEnabled(enabled)
        self.jitter_size_spin.setEnabled(enabled)
        self.jitter_position_spin.setEnabled(enabled)
        self.refresh_jitter_btn.setEnabled(enabled)
        self.scribble_ratio_spin.setEnabled(enabled)
        self.scribble_style_combo.setEnabled(enabled)
        self.refresh_scribble_btn.setEnabled(enabled)
        self.spacing_min_spin.setEnabled(enabled)
        self.spacing_max_spin.setEnabled(enabled)
        self.extra_space_spin.setEnabled(enabled)
        self.refresh_spacing_btn.setEnabled(enabled)
        self.distort_x_spin.setEnabled(enabled)
        self.distort_y_spin.setEnabled(enabled)
        self.shear_x_spin.setEnabled(enabled)
        self.shear_y_spin.setEnabled(enabled)
        self.rotation_spin.setEnabled(enabled)
        self.scale_x_spin.setEnabled(enabled)
        self.scale_y_spin.setEnabled(enabled)
        self.del_btn.setEnabled(enabled)

    def _update_from_block(self, block):
        self.font_combo.setCurrentText(block.font_family)
        self.size_spin.setValue(block.font_size)
        self.color_btn.setStyleSheet(f"background-color: {block.color.name()};")
        self.spacing_spin.setValue(block.line_spacing)
        self.jitter_enabled_check.setChecked(block.jitter_enabled)
        self.jitter_bend_spin.setValue(block.jitter_bend)
        self.jitter_thickness_spin.setValue(block.jitter_thickness)
        self.jitter_size_spin.setValue(block.jitter_size_var)
        self.jitter_position_spin.setValue(block.jitter_position_var)
        self.scribble_ratio_spin.setValue(int(block.scribble_ratio))
        self.scribble_style_combo.setCurrentText(block.scribble_style)
        self.spacing_min_spin.setValue(block.char_spacing_min)
        self.spacing_max_spin.setValue(block.char_spacing_max)
        self.extra_space_spin.setValue(block.extra_space_count)
        self.distort_x_spin.setValue(block.distortion_x)
        self.distort_y_spin.setValue(block.distortion_y)
        self.shear_x_spin.setValue(block.shear_x)
        self.shear_y_spin.setValue(block.shear_y)
        self.rotation_spin.setValue(block.rotation)
        self.scale_x_spin.setValue(block.scale_x)
        self.scale_y_spin.setValue(block.scale_y)
        self.pos_x_label.setText(str(int(round(block._logical_x))))
        self.pos_y_label.setText(str(int(round(block._logical_y))))

    def _on_font_changed(self, font_family):
        if self._current_block:
            self._current_block.font_family = font_family
            self.property_changed.emit()

    def _on_size_changed(self, size):
        if self._current_block:
            self._current_block.font_size = size
            self.property_changed.emit()

    def _on_color_clicked(self):
        if self._current_block:
            color = QColorDialog.getColor(self._current_block.color, self, "选择颜色")
            if color.isValid():
                self._current_block.color = color
                self.color_btn.setStyleSheet(f"background-color: {color.name()};")
                self.property_changed.emit()

    def _on_spacing_changed(self, value):
        if self._current_block:
            self._current_block.line_spacing = value
            self.property_changed.emit()

    def _on_jitter_enabled_changed(self, enabled):
        if self._current_block:
            self._current_block.jitter_enabled = enabled
            self.property_changed.emit()

    def _on_jitter_bend_changed(self, value):
        if self._current_block:
            self._current_block.jitter_bend = value
            self.property_changed.emit()

    def _on_jitter_thickness_changed(self, value):
        if self._current_block:
            self._current_block.jitter_thickness = value
            self.property_changed.emit()

    def _on_jitter_size_changed(self, value):
        if self._current_block:
            self._current_block.jitter_size_var = value
            self.property_changed.emit()

    def _on_jitter_position_changed(self, value):
        if self._current_block:
            self._current_block.jitter_position_var = value
            self.property_changed.emit()

    def _on_refresh_jitter(self):
        if self._current_block:
            self._current_block._update_char_seeds()
            self._current_block.update()
            self.property_changed.emit()

    def _on_scribble_ratio_changed(self, value):
        if self._current_block:
            self._current_block.scribble_ratio = value
            self.property_changed.emit()

    def _on_scribble_style_changed(self, style):
        if self._current_block:
            self._current_block.scribble_style = style
            self.property_changed.emit()

    def _on_refresh_scribble(self):
        if self._current_block:
            self._current_block._update_char_seeds()
            self._current_block.update()
            self.property_changed.emit()

    def _on_spacing_min_changed(self, value):
        if self._current_block:
            self._current_block.char_spacing_min = value
            self.property_changed.emit()

    def _on_spacing_max_changed(self, value):
        if self._current_block:
            self._current_block.char_spacing_max = value
            self.property_changed.emit()

    def _on_extra_space_changed(self, value):
        if self._current_block:
            self._current_block.extra_space_count = value
            self.property_changed.emit()

    def _on_refresh_spacing(self):
        if self._current_block:
            self._current_block._update_char_seeds()
            self._current_block.update()
            self.property_changed.emit()

    def _on_distort_x_changed(self, value):
        if self._current_block:
            self._current_block.distortion_x = value
            self.property_changed.emit()

    def _on_distort_y_changed(self, value):
        if self._current_block:
            self._current_block.distortion_y = value
            self.property_changed.emit()

    def _on_shear_x_changed(self, value):
        if self._current_block:
            self._current_block.shear_x = value
            self.property_changed.emit()

    def _on_shear_y_changed(self, value):
        if self._current_block:
            self._current_block.shear_y = value
            self.property_changed.emit()

    def _on_rotation_changed(self, value):
        if self._current_block:
            self._current_block.rotation = value
            self.property_changed.emit()

    def _on_scale_x_changed(self, value):
        if self._current_block:
            self._current_block.scale_x = value
            self.property_changed.emit()

    def _on_scale_y_changed(self, value):
        if self._current_block:
            self._current_block.scale_y = value
            self.property_changed.emit()

    def update_position(self, x, y):
        self.pos_x_label.setText(str(x))
        self.pos_y_label.setText(str(y))


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("HandInPaper - 手写文字放置工具")
        self.setGeometry(100, 100, 1400, 900)

        # 设置窗口图标（直接使用内嵌 SVG，不依赖外部文件）
        if ICON_SVG:
            ba = QByteArray(ICON_SVG.encode('utf-8'))
            renderer = QSvgRenderer(ba)
            pixmap = QPixmap(256, 256)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()
            icon = QIcon()
            icon.addPixmap(pixmap)
            self.setWindowIcon(icon)

        self._load_custom_fonts()
        self._zoom_levels = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 3.0]
        self._zoom_index = self._zoom_levels.index(1.0)
        self._setup_ui()
        self._setup_menu()
        self._setup_toolbar()
        self._setup_statusbar()

    def _load_custom_fonts(self):
        """加载目录下所有字体，返回可用的字体族名列表"""
        self._available_fonts = []
        if FONT_DIR.exists():
            font_files = [
                path for path in sorted(FONT_DIR.iterdir())
                if path.is_file() and path.suffix.lower() in (".ttf", ".otf", ".ttc")
            ]
            for font_file in font_files:
                font_id = QFontDatabase.addApplicationFont(str(font_file))
                if font_id >= 0:
                    families = QFontDatabase.applicationFontFamilies(font_id)
                    for f in families:
                        if f not in self._available_fonts:
                            self._available_fonts.append(f)

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(False)

        self.canvas = CanvasWidget()
        self.canvas.text_block_selected.connect(self._on_block_selected)
        scroll_area.setWidget(self.canvas)
        splitter.addWidget(scroll_area)

        self.property_panel = PropertyPanel(self._available_fonts)
        self.property_panel.property_changed.connect(self._on_property_changed)
        self.property_panel.add_block_requested.connect(self._add_text_block)
        self.property_panel.delete_block_requested.connect(self._delete_selected)
        splitter.addWidget(self.property_panel)

        splitter.setSizes([800, 300])

        layout = QHBoxLayout(central_widget)
        layout.addWidget(splitter)
        layout.setContentsMargins(0, 0, 0, 0)

    def _setup_menu(self):
        menubar = self.menuBar()

        # 文件菜单
        self.file_menu = menubar.addMenu(tr("menu_file"))

        self.open_action = QAction(tr("open_background"), self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.triggered.connect(self._open_background)
        self.file_menu.addAction(self.open_action)

        self.save_action = QAction(tr("save_project"), self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self._save_project)
        self.file_menu.addAction(self.save_action)

        self.load_action = QAction(tr("load_project"), self)
        self.load_action.setShortcut("Ctrl+L")
        self.load_action.triggered.connect(self._load_project)
        self.file_menu.addAction(self.load_action)

        self.export_action = QAction(tr("export_image"), self)
        self.export_action.setShortcut("Ctrl+E")
        self.export_action.triggered.connect(self._export_image)
        self.file_menu.addAction(self.export_action)

        self.file_menu.addSeparator()

        self.exit_action = QAction(tr("exit"), self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.triggered.connect(self.close)
        self.file_menu.addAction(self.exit_action)

        # 编辑菜单
        self.edit_menu = menubar.addMenu(tr("menu_edit"))

        self.add_text_action = QAction(tr("add_text_block"), self)
        self.add_text_action.setShortcut("Ctrl+T")
        self.add_text_action.triggered.connect(self._add_text_block)
        self.edit_menu.addAction(self.add_text_action)

        self.delete_action = QAction(tr("delete_selected"), self)
        self.delete_action.setShortcut("Delete")
        self.delete_action.triggered.connect(self._delete_selected)
        self.edit_menu.addAction(self.delete_action)

        # 视图菜单
        self.view_menu = menubar.addMenu(tr("menu_view"))

        self.zoom_in_action = QAction(tr("zoom_in"), self)
        self.zoom_in_action.setShortcut("Ctrl++")
        self.zoom_in_action.triggered.connect(self._zoom_in)
        self.view_menu.addAction(self.zoom_in_action)

        self.zoom_out_action = QAction(tr("zoom_out"), self)
        self.zoom_out_action.setShortcut("Ctrl+-")
        self.zoom_out_action.triggered.connect(self._zoom_out)
        self.view_menu.addAction(self.zoom_out_action)

        self.reset_zoom_action = QAction(tr("reset_zoom"), self)
        self.reset_zoom_action.setShortcut("Ctrl+0")
        self.reset_zoom_action.triggered.connect(self._reset_zoom)
        self.view_menu.addAction(self.reset_zoom_action)

        # 语言菜单
        self.lang_menu = menubar.addMenu(tr("menu_language"))

        self.zh_action = QAction("中文", self)
        self.zh_action.triggered.connect(lambda: self._switch_language("zh"))
        self.lang_menu.addAction(self.zh_action)

        self.en_action = QAction("English", self)
        self.en_action.triggered.connect(lambda: self._switch_language("en"))
        self.lang_menu.addAction(self.en_action)

    def _setup_toolbar(self):
        self.toolbar = QToolBar(tr("menu_edit"))
        self.addToolBar(self.toolbar)

        self.add_btn = QPushButton(tr("add_text_block"))
        self.add_btn.clicked.connect(self._add_text_block)
        self.toolbar.addWidget(self.add_btn)

        self.toolbar.addSeparator()

        self.zoom_out_btn = QPushButton("-")
        self.zoom_out_btn.setToolTip(tr("zoom_out"))
        self.zoom_out_btn.clicked.connect(self._zoom_out)
        self.toolbar.addWidget(self.zoom_out_btn)

        self.zoom_label = QLabel("100%")
        self.zoom_label.setMinimumWidth(48)
        self.zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.toolbar.addWidget(self.zoom_label)

        self.zoom_in_btn = QPushButton("+")
        self.zoom_in_btn.setToolTip(tr("zoom_in"))
        self.zoom_in_btn.clicked.connect(self._zoom_in)
        self.toolbar.addWidget(self.zoom_in_btn)

        self.reset_zoom_btn = QPushButton(tr("reset_zoom"))
        self.reset_zoom_btn.clicked.connect(self._reset_zoom)
        self.toolbar.addWidget(self.reset_zoom_btn)

    def _setup_statusbar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage(tr("ready"))

    def _on_block_selected(self, block):
        self.property_panel.set_block(block)
        if block:
            self.statusbar.showMessage(f"{tr('selected_block')}: {block.text[:20]}...")
        else:
            self.statusbar.showMessage(tr("ready"))

    def _switch_language(self, lang):
        """切换语言 / Switch language"""
        global current_lang
        current_lang = lang
        self._update_ui_texts()

    def _update_ui_texts(self):
        """更新所有 UI 文本 / Update all UI texts"""
        self.setWindowTitle(tr("window_title"))

        # 更新菜单
        self.file_menu.setTitle(tr("menu_file"))
        self.open_action.setText(tr("open_background"))
        self.save_action.setText(tr("save_project"))
        self.load_action.setText(tr("load_project"))
        self.export_action.setText(tr("export_image"))
        self.exit_action.setText(tr("exit"))

        self.edit_menu.setTitle(tr("menu_edit"))
        self.add_text_action.setText(tr("add_text_block"))
        self.delete_action.setText(tr("delete_selected"))

        self.view_menu.setTitle(tr("menu_view"))
        self.zoom_in_action.setText(tr("zoom_in"))
        self.zoom_out_action.setText(tr("zoom_out"))
        self.reset_zoom_action.setText(tr("reset_zoom"))

        self.lang_menu.setTitle(tr("menu_language"))

        # 更新工具栏
        self.add_btn.setText(tr("add_text_block"))
        self.zoom_out_btn.setToolTip(tr("zoom_out"))
        self.zoom_in_btn.setToolTip(tr("zoom_in"))
        self.reset_zoom_btn.setText(tr("reset_zoom"))

        # 更新状态栏
        self.statusbar.showMessage(tr("ready"))

    def _on_property_changed(self):
        self.canvas.update()

    def _apply_zoom(self):
        scale = self._zoom_levels[self._zoom_index]
        self.canvas.set_scale(scale)
        self.zoom_label.setText(f"{int(scale * 100)}%")

    def _zoom_in(self):
        if self._zoom_index < len(self._zoom_levels) - 1:
            self._zoom_index += 1
            self._apply_zoom()

    def _zoom_out(self):
        if self._zoom_index > 0:
            self._zoom_index -= 1
            self._apply_zoom()

    def _reset_zoom(self):
        self._zoom_index = self._zoom_levels.index(1.0)
        self._apply_zoom()

    def _open_background(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, tr("open_background"), "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)"
        )
        if file_path:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                self.canvas.set_background(pixmap)
                self.statusbar.showMessage(f"{tr('open_background')}: {file_path}")

    def _save_project(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, tr("save_project"), "",
            "Project Files (*.hip);;All Files (*)"
        )
        if file_path:
            data = {'blocks': []}
            for block in self.canvas.get_all_blocks():
                data['blocks'].append(block.get_properties())

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            self.statusbar.showMessage(f"{tr('project_saved')}: {file_path}")

    def _load_project(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, tr("load_project"), "",
            "Project Files (*.hip);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                for block in self.canvas.get_all_blocks():
                    self.canvas.remove_text_block(block)

                for props in data.get('blocks', []):
                    block = TextBlockWidget(
                        text=props.get('text', ''),
                        x=props.get('x', 100),
                        y=props.get('y', 100)
                    )
                    block.set_properties(props)
                    self.canvas.add_text_block(block)

                self.statusbar.showMessage(f"{tr('project_loaded')}: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, tr("error"), f"{tr('load_error')}: {e}")

    def _export_image(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, tr("export_image"), "",
            "PNG (*.png);;JPEG (*.jpg);;All Files (*)"
        )
        if file_path:
            # 取消选中状态
            selected = self.canvas.get_selected_block()
            if selected:
                selected.set_selected(False)

            # 导出始终使用逻辑尺寸：有背景时为原图尺寸，无背景时为默认画布尺寸。
            if self.canvas._background:
                bg = self.canvas._background
                export_w = bg.width()
                export_h = bg.height()
            else:
                logical_size = self.canvas._logical_size()
                export_w = logical_size.width()
                export_h = logical_size.height()

            pixmap = QPixmap(export_w, export_h)
            pixmap.fill(Qt.GlobalColor.white)

            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

            # 绘制背景
            if self.canvas._background:
                painter.drawPixmap(0, 0, self.canvas._background)

            # 绘制文字块
            for block in self.canvas.get_all_blocks():
                painter.save()
                painter.translate(block._logical_x, block._logical_y)
                block._paint_content(painter, include_selection=False)
                painter.restore()

            painter.end()
            pixmap.save(file_path)

            # 恢复选中状态
            if selected:
                selected.set_selected(True)

            self.statusbar.showMessage(f"{tr('image_exported')}: {file_path}")

    def _add_text_block(self):
        x = 100 + len(self.canvas.get_all_blocks()) * 20
        y = 100 + len(self.canvas.get_all_blocks()) * 20
        block = TextBlockWidget(
            text="双击编辑" if current_lang == "zh" else "Double-click to edit",
            x=x, y=y
        )
        # 设置默认宽度为背景图片宽度的50%，如果没有背景则使用屏幕宽度的40%
        if self.canvas._background:
            default_width = int(self.canvas._background.width() * 0.5)
        else:
            default_width = int(self.width() * 0.4)
        block._fixed_width = default_width
        block._update_size()
        self.canvas.add_text_block(block)
        self.statusbar.showMessage(tr("added_block"))

    def _delete_selected(self):
        block = self.canvas.get_selected_block()
        if block:
            self.canvas.remove_text_block(block)
            self.property_panel.set_block(None)
            self.statusbar.showMessage(tr("deleted_block"))


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)

    window = MainWindow()
    window.showMaximized()  # 默认最大化显示

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
