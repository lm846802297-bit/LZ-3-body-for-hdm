#!/usr/bin/env python3
"""Append Chinese, source-checked captions to the original Xe-131 figures."""

from __future__ import annotations

import hashlib
import io
import json
import re
from html import escape
from pathlib import Path

import matplotlib
import pymupdf
from fontTools import subset
from fontTools.ttLib import TTFont as SourceFont
from fontTools.varLib.instancer import instantiateVariableFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

from captions_zh import AUDIT, COMPARISON, PAGES


ROOT = Path(__file__).resolve().parent
ORIGINALS = ROOT / "originals"
OUTPUT = ROOT / "chinese_captions"
PAGE_WIDTH = 720.0
PLOT_LEFT = 22.0
PLOT_TOP = 12.0
PLOT_WIDTH = PAGE_WIDTH - 2.0 * PLOT_LEFT
TEXT_LEFT = 36.0
TEXT_WIDTH = PAGE_WIDTH - 2.0 * TEXT_LEFT

SOURCE_HASHES = {
    "originals/xe131_six_channel_interpolation_audit.pdf": "8f7063b22afc1a4439ab90b24dc8a540756b3c7e37b9850ef6c9a078c605420e",
    "originals/xe131_afh_six_channel_comparison.pdf": "28f12b4183f64ba6c2fc4629f9d5e54ac46a16637059b975acc70b46191fa498",
    "data/xe131_six_response_grid.csv": "74ee7ca4897a22c5b5b55fdabb3c009d2947819a098df2d006ca44730c209806",
    "data/xe131_six_channel_fixed_speed_recoil_scan.csv": "50cbb459f91ae0b72361e7b626ad7da8d27ebc824f4974e2ac9e1c61e003c28c",
    "data/xe131_six_channel_fixed_speed_recoil_scan.json": "0e594d518d74df82fa44b29f5112843f7a48ebd38c7c4240664ff3b453e22af3",
}

INK = colors.HexColor("#20272f")
SUBTLE = colors.HexColor("#52606c")
RULE = colors.HexColor("#d5dce1")
SERIES = {
    "blue": colors.HexColor("#1f77b4"),
    "lightblue": colors.HexColor("#73b2db"),
    "orange": colors.HexColor("#ff7f0e"),
    "green": colors.HexColor("#2ca02c"),
    "red": colors.HexColor("#d62728"),
}


def check_sources() -> None:
    for relative_path, expected_hash in SOURCE_HASHES.items():
        actual_hash = hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            raise ValueError(f"Unexpected source SHA-256: {relative_path}: {actual_hash}")


def register_fonts() -> None:
    windows_fonts = Path("C:/Windows/Fonts")
    math_fonts = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
    characters = str(PAGES) + (
        "图 坐标 线型与点型 读数 对照 范围 适用范围 基准参数 |｜"
        "本组研究中的散射核采用固定速度和领先阶静态单体矢量流；"
        "三个空间响应为源码转写，尚待独立原生验证。"
        "插值对照使用同一粗网格，不能取代密网原生计算。"
        "质量入射速度耦合 Xe-131 GeV keV km/s 0123456789"
    )
    for name, filename, weight in (
        ("NotoSerifSC", "NotoSerifSC-VF.ttf", 400),
        ("NotoSansSC", "NotoSansSC-VF.ttf", 600),
    ):
        path = windows_fonts / filename
        if not path.is_file():
            raise FileNotFoundError(f"Required font not found: {path}")
        source_font = SourceFont(path)
        subsetter = subset.Subsetter()
        subsetter.populate(text=characters)
        subsetter.subset(source_font)
        instantiateVariableFont(source_font, {"wght": weight}, inplace=True)
        font_data = io.BytesIO()
        source_font.save(font_data)
        font_data.seek(0)
        pdfmetrics.registerFont(TTFont(name, font_data))

    for name, path in (
        ("STIX", math_fonts / "STIXGeneral.ttf"),
        ("STIXItalic", math_fonts / "STIXGeneralItalic.ttf"),
    ):
        if not path.is_file():
            raise FileNotFoundError(f"Required font not found: {path}")
        pdfmetrics.registerFont(TTFont(name, str(path)))


def math_text(symbol: str) -> str:
    italic = lambda value: f'<font name="STIXItalic">{value}</font>'
    roman = lambda value: f'<font name="STIX">{value}</font>'
    subscript = lambda value: f"<sub>{value}</sub>"
    superscript = lambda value: f"<super>{value}</super>"
    symbols = {
        "M": italic("M"),
        "q": italic("q") + subscript(italic("A")),
        "ER": italic("E") + subscript(italic("R")),
        "dm": roman("Δ") + italic("m"),
        "mchi": italic("m") + subscript(roman("χ") + "1"),
        "ms": italic("m") + subscript(italic("s")),
        "g2": italic("g") + subscript("2"),
        "Phi": roman("Φ″"),
        "MPhi": italic("M") + roman("Φ″"),
        "Delta": roman("Δ"),
        "Sigma": roman("Σ′"),
        "SigmaDelta": roman("Σ′Δ"),
        "WM": italic("W") + subscript(italic("M")),
        "WPhi": italic("W") + subscript(roman("Φ″")),
        "WMPhi": italic("W") + subscript(italic("M") + roman("Φ″")),
        "WDelta": italic("W") + subscript(roman("Δ")),
        "WSigma": italic("W") + subscript(roman("Σ′")),
        "WSigmaDelta": italic("W") + subscript(roman("Σ′Δ")),
        "Ks": italic("K") + subscript(roman("spatial")),
        "Kc": italic("K") + subscript(roman("charge")),
        "P": italic("P"),
        "C": italic("C"),
        "e9": "10" + superscript("9"),
        "e-3": "10" + superscript("−3"),
        "e-8": "10" + superscript("−8"),
        "e-9": "10" + superscript("−9"),
    }
    if symbol not in symbols:
        raise ValueError(f"Unknown mathematical symbol: {symbol}")
    return symbols[symbol]


def markup(text: str) -> str:
    return re.sub(r"\$([^$]+)\$", lambda match: math_text(match.group(1)), escape(text))


def paragraph(text: str, width: float, size: float = 11.2, leading: float = 16.2) -> tuple[Paragraph, float]:
    style = ParagraphStyle(
        "caption",
        fontName="NotoSerifSC",
        fontSize=size,
        leading=leading,
        textColor=INK,
        wordWrap="CJK",
        allowWidows=0,
        allowOrphans=0,
    )
    para = Paragraph(markup(text), style)
    _, height = para.wrap(width, 5000)
    return para, height


def build_layout(page_info: dict, figure_bottom: float) -> tuple[list[tuple], float]:
    items = []
    cursor = figure_bottom + 15.0
    items.append(("header", cursor, f"图 {page_info['id']}  |  {page_info['title']}"))
    cursor += 21.0
    items.append(("rule", cursor))
    cursor += 9.0

    para, height = paragraph("坐标｜" + page_info["axes"], TEXT_WIDTH)
    items.append(("paragraph", cursor, para, height, TEXT_LEFT))
    cursor += height + 7.0

    items.append(("legend_header", cursor, "线型与点型"))
    cursor += 16.0
    for colour, line_style, marker, description in page_info["legend"]:
        para, height = paragraph(description, TEXT_WIDTH - 45.0, size=10.9, leading=15.4)
        items.append(("legend", cursor, para, height, colour, line_style, marker))
        cursor += max(height, 15.4) + 2.0
    cursor += 5.0

    for label, content in page_info["notes"]:
        para, height = paragraph(label + "｜" + content, TEXT_WIDTH)
        items.append(("paragraph", cursor, para, height, TEXT_LEFT))
        cursor += height + 6.0

    if page_info["id"] in {"A3", "B1", "B2", "B3"}:
        channels = "六通道｜电荷项：$M$、$Phi$、$MPhi$；空间项：$Delta$、$Sigma$、$SigmaDelta$。"
        para, height = paragraph(channels, TEXT_WIDTH, size=10.4, leading=15.0)
        items.append(("paragraph", cursor, para, height, TEXT_LEFT))
        cursor += height + 4.0
        baseline = "基准参数｜$mchi$ = 1000 GeV，$ms$ = 300 keV，入射速度 776 km/s，$g2$ = 1。"
        para, height = paragraph(baseline, TEXT_WIDTH, size=10.4, leading=15.0)
        items.append(("paragraph", cursor, para, height, TEXT_LEFT))
        cursor += height + 6.0

    cursor += 1.0
    items.append(("rule", cursor))
    cursor += 8.0
    caution = (
        "适用范围｜本组研究中的散射核采用 Xe-131 固定速度和领先阶静态单体矢量流；"
        "三个空间响应为源码转写，尚待独立原生验证。插值对照使用同一粗网格，不能取代密网原生计算。"
    )
    para, height = paragraph(caution, TEXT_WIDTH, size=9.5, leading=14.1)
    items.append(("paragraph", cursor, para, height, TEXT_LEFT))
    cursor += height + 18.0
    return items, cursor


def draw_swatch(draw: canvas.Canvas, left: float, center: float, colour: str, line_style: str, marker: str) -> None:
    draw.saveState()
    draw.setStrokeColor(SERIES[colour])
    draw.setFillColor(SERIES[colour])
    draw.setLineWidth(1.7)
    if line_style == "dash":
        draw.setDash(6.2, 3.1)
    elif line_style == "dots":
        draw.setDash(1.5, 2.6)
    elif line_style == "dashdot":
        draw.setDash([7, 2.4, 1.5, 2.4])
    if line_style != "none":
        draw.line(left, center, left + 27, center)
    draw.setDash()
    if marker == "circle":
        draw.circle(left + 13.5, center, 2.7, stroke=0, fill=1)
    elif marker == "square":
        draw.rect(left + 10.8, center - 2.7, 5.4, 5.4, stroke=0, fill=1)
    draw.restoreState()


def caption_layer(items: list[tuple], page_height: float) -> bytes:
    buffer = io.BytesIO()
    draw = canvas.Canvas(buffer, pagesize=(PAGE_WIDTH, page_height), pageCompression=1)
    for item in items:
        kind, top = item[0], item[1]
        if kind == "header":
            draw.setFillColor(INK)
            draw.setFont("NotoSansSC", 14.5)
            draw.drawString(TEXT_LEFT, page_height - top - 14, item[2])
        elif kind == "legend_header":
            draw.setFillColor(SUBTLE)
            draw.setFont("NotoSansSC", 10.5)
            draw.drawString(TEXT_LEFT, page_height - top - 10, item[2])
        elif kind == "rule":
            draw.setStrokeColor(RULE)
            draw.setLineWidth(0.6)
            draw.line(TEXT_LEFT, page_height - top, PAGE_WIDTH - TEXT_LEFT, page_height - top)
        elif kind == "paragraph":
            _, _, para, height, left = item
            para.drawOn(draw, left, page_height - top - height)
        elif kind == "legend":
            _, _, para, height, colour, line_style, marker = item
            draw_swatch(draw, TEXT_LEFT + 2, page_height - top - 7.2, colour, line_style, marker)
            para.drawOn(draw, TEXT_LEFT + 45.0, page_height - top - height)
        else:
            raise ValueError(f"Unknown layout item: {kind}")
    draw.showPage()
    draw.save()
    return buffer.getvalue()


def png_name(page_info: dict) -> str:
    if "png" in page_info:
        return page_info["png"] + "_zh.png"
    return f"xe131_six_channel_comparison_{page_info['id']}_zh.png"


def generate(source_name: str, page_data: list[dict]) -> list[Path]:
    source = pymupdf.open(ORIGINALS / f"{source_name}.pdf")
    if len(source) != len(page_data):
        raise ValueError(f"Page count does not match caption count: {source_name}")
    result = pymupdf.open()
    generated = []
    try:
        for index, page_info in enumerate(page_data):
            source_page = source[index]
            figure_height = PLOT_WIDTH * source_page.rect.height / source_page.rect.width
            figure_box = pymupdf.Rect(PLOT_LEFT, PLOT_TOP, PLOT_LEFT + PLOT_WIDTH, PLOT_TOP + figure_height)
            layout, page_height = build_layout(page_info, figure_box.y1)
            page = result.new_page(width=PAGE_WIDTH, height=page_height)
            page.show_pdf_page(figure_box, source, index)
            with pymupdf.open(stream=caption_layer(layout, page_height), filetype="pdf") as overlay:
                page.show_pdf_page(page.rect, overlay, 0)

        pdf_path = OUTPUT / f"{source_name}_zh.pdf"
        result.set_metadata({"title": "Xe-131 AFH 中文图注：" + source_name, "subject": "原始数值图与中文图注"})
        result.save(pdf_path, garbage=4, deflate=True)
        generated.append(pdf_path)
    finally:
        result.close()
        source.close()

    with pymupdf.open(pdf_path) as rendered:
        for index, page_info in enumerate(page_data):
            png_path = OUTPUT / png_name(page_info)
            rendered[index].get_pixmap(dpi=200, alpha=False).save(png_path)
            generated.append(png_path)
    return generated


def main() -> None:
    check_sources()
    register_fonts()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    results = []
    for name in (AUDIT, COMPARISON):
        results.extend(generate(name, PAGES[name]))
    manifest = {
        "source_sha256": SOURCE_HASHES,
        "plot_origin": "Original PDF pages retained; first PDF contains raster charts, second PDF contains vector charts.",
        "scan_workflow": 44307471788,
        "scan_artifact": 14430267797,
        "outputs": {path.name: {"bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for path in results},
    }
    (OUTPUT / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
