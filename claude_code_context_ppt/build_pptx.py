from __future__ import annotations

import html
import os
import shutil
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


BASE = Path(__file__).resolve().parent
FRAMES_DIR = BASE / "frames"
OUT = BASE / "Claude_Code上下文架构解析_视频素材PPT.pptx"

SLIDE_W = 13.333333
SLIDE_H = 7.5
EMU = 914400


def emu(inches: float) -> int:
    return round(inches * EMU)


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def content_types(image_names: list[str]) -> str:
    overrides = "\n".join(
        f'<Override PartName="/ppt/slides/slide{i}.xml" '
        f'ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        for i in range(1, 14)
    )
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="jpg" ContentType="image/jpeg"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
  <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
  {overrides}
</Types>'''


def rels_root() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>'''


def app_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
 xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Codex</Application>
  <PresentationFormat>Widescreen</PresentationFormat>
  <Slides>13</Slides>
</Properties>'''


def core_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
 xmlns:dc="http://purl.org/dc/elements/1.1/"
 xmlns:dcterms="http://purl.org/dc/terms/"
 xmlns:dcmitype="http://purl.org/dc/dcmitype/"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>Claude Code上下文架构解析</dc:title>
  <dc:creator>Codex</dc:creator>
  <cp:keywords>Claude Code, 上下文架构, 视频抽帧, 音频</cp:keywords>
  <dcterms:created xsi:type="dcterms:W3CDTF">2026-05-19T00:00:00Z</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">2026-05-19T00:00:00Z</dcterms:modified>
</cp:coreProperties>'''


def presentation_xml(count: int) -> str:
    slide_ids = "\n".join(
        f'<p:sldId id="{255+i}" r:id="rId{i}"/>' for i in range(1, count + 1)
    )
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
 xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId{count+1}"/></p:sldMasterIdLst>
  <p:sldIdLst>{slide_ids}</p:sldIdLst>
  <p:sldSz cx="{emu(SLIDE_W)}" cy="{emu(SLIDE_H)}" type="wide"/>
  <p:notesSz cx="{emu(10)}" cy="{emu(7.5)}"/>
</p:presentation>'''


def presentation_rels(count: int) -> str:
    rels = [
        f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>'
        for i in range(1, count + 1)
    ]
    rels.append(
        f'<Relationship Id="rId{count+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>'
    )
    rels.append(
        f'<Relationship Id="rId{count+2}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>'
    )
    return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + "".join(rels) + "</Relationships>"


def theme_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Codex Clean">
  <a:themeElements>
    <a:clrScheme name="Codex">
      <a:dk1><a:srgbClr val="111827"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1>
      <a:dk2><a:srgbClr val="1F2937"/></a:dk2><a:lt2><a:srgbClr val="F7F8FA"/></a:lt2>
      <a:accent1><a:srgbClr val="2563EB"/></a:accent1><a:accent2><a:srgbClr val="059669"/></a:accent2>
      <a:accent3><a:srgbClr val="DC2626"/></a:accent3><a:accent4><a:srgbClr val="7C3AED"/></a:accent4>
      <a:accent5><a:srgbClr val="EA580C"/></a:accent5><a:accent6><a:srgbClr val="0891B2"/></a:accent6>
      <a:hlink><a:srgbClr val="2563EB"/></a:hlink><a:folHlink><a:srgbClr val="7C3AED"/></a:folHlink>
    </a:clrScheme>
    <a:fontScheme name="CodexFont">
      <a:majorFont><a:latin typeface="Aptos Display"/><a:ea typeface="PingFang SC"/></a:majorFont>
      <a:minorFont><a:latin typeface="Aptos"/><a:ea typeface="PingFang SC"/></a:minorFont>
    </a:fontScheme>
    <a:fmtScheme name="CodexFmt">
      <a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst>
      <a:lnStyleLst><a:ln w="9525"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst>
      <a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst>
      <a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst>
    </a:fmtScheme>
  </a:themeElements>
</a:theme>'''


def master_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
 xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld><p:bg><p:bgPr><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill></p:bgPr></p:bg><p:spTree>
    <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
    <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
  </p:spTree></p:cSld>
  <p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst>
  <p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles>
</p:sldMaster>'''


def layout_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
 xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank" preserve="1">
  <p:cSld name="Blank"><p:spTree>
    <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
    <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
  </p:spTree></p:cSld>
</p:sldLayout>'''


def simple_rels(target: str, rel_type: str) -> str:
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="{rel_type}" Target="{target}"/>
</Relationships>'''


def fill(color: str) -> str:
    return f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill>'


def rect(shape_id: int, x: float, y: float, w: float, h: float, color: str, line: str | None = None) -> str:
    ln = '<a:ln><a:noFill/></a:ln>' if line is None else f'<a:ln w="9525">{fill(line)}</a:ln>'
    return f'''<p:sp>
  <p:nvSpPr><p:cNvPr id="{shape_id}" name="Box {shape_id}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>
    <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>{fill(color)}{ln}</p:spPr>
  <p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody>
</p:sp>'''


def text_box(shape_id: int, text: str, x: float, y: float, w: float, h: float, size: int = 24,
             color: str = "111827", bold: bool = False, valign: str = "top") -> str:
    b = '<a:b/>' if bold else ''
    lines = text.split("\n")
    paras = []
    for line in lines:
        paras.append(
            f'<a:p><a:r><a:rPr lang="zh-CN" sz="{size*100}" dirty="0">{b}<a:solidFill><a:srgbClr val="{color}"/></a:solidFill></a:rPr><a:t>{esc(line)}</a:t></a:r><a:endParaRPr lang="zh-CN" sz="{size*100}"/></a:p>'
        )
    return f'''<p:sp>
  <p:nvSpPr><p:cNvPr id="{shape_id}" name="Text {shape_id}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>
    <a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></p:spPr>
  <p:txBody><a:bodyPr wrap="square" anchor="{valign}"/><a:lstStyle/>{''.join(paras)}</p:txBody>
</p:sp>'''


def bullet_box(shape_id: int, bullets: list[str], x: float, y: float, w: float, h: float, size: int = 18) -> str:
    paras = []
    for item in bullets:
        paras.append(
            f'<a:p><a:pPr marL="342900" indent="-171450"><a:buChar char="•"/></a:pPr><a:r><a:rPr lang="zh-CN" sz="{size*100}" dirty="0"><a:solidFill><a:srgbClr val="374151"/></a:solidFill></a:rPr><a:t>{esc(item)}</a:t></a:r></a:p>'
        )
    return f'''<p:sp>
  <p:nvSpPr><p:cNvPr id="{shape_id}" name="Bullets {shape_id}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>
    <a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></p:spPr>
  <p:txBody><a:bodyPr wrap="square"/><a:lstStyle/>{''.join(paras)}</p:txBody>
</p:sp>'''


def picture(shape_id: int, rid: str, x: float, y: float, w: float, h: float) -> str:
    return f'''<p:pic>
  <p:nvPicPr><p:cNvPr id="{shape_id}" name="Image {shape_id}"/><p:cNvPicPr/><p:nvPr/></p:nvPicPr>
  <p:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>
  <p:spPr><a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>
</p:pic>'''


def slide_xml(shapes: list[str]) -> str:
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
 xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld><p:bg><p:bgPr>{fill("FFFFFF")}</p:bgPr></p:bg><p:spTree>
    <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
    <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
    {''.join(shapes)}
  </p:spTree></p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>'''


def image_slide(title: str, caption: str, img_name: str, idx: int) -> tuple[str, str]:
    shapes = [
        rect(2, 0, 0, SLIDE_W, SLIDE_H, "F8FAFC"),
        text_box(3, title, 0.55, 0.28, 6.7, 0.46, 20, "111827", True),
        text_box(4, caption, 7.45, 0.32, 5.2, 0.42, 11, "6B7280"),
        rect(5, 0.55, 0.9, 12.25, 5.95, "FFFFFF", "E5E7EB"),
        picture(6, "rId1", 0.72, 1.05, 11.91, 5.48),
        text_box(7, f"{idx:02d}", 12.25, 6.95, 0.45, 0.25, 10, "9CA3AF"),
    ]
    rel = simple_rels(f"../media/{img_name}", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image")
    return slide_xml(shapes), rel


def package() -> None:
    frames = sorted(FRAMES_DIR.glob("frame_*.jpg"))
    contact = BASE / "contact_sheet.jpg"
    images = [contact] + frames
    if len(frames) != 12 or not contact.exists():
        raise SystemExit("Expected 12 frames and contact_sheet.jpg")

    tmp = BASE / "_pptx_build"
    if tmp.exists():
        shutil.rmtree(tmp)
    for path in [
        tmp / "_rels",
        tmp / "docProps",
        tmp / "ppt" / "_rels",
        tmp / "ppt" / "slides" / "_rels",
        tmp / "ppt" / "media",
        tmp / "ppt" / "theme",
        tmp / "ppt" / "slideMasters" / "_rels",
        tmp / "ppt" / "slideLayouts" / "_rels",
    ]:
        path.mkdir(parents=True, exist_ok=True)

    image_names = []
    for i, src in enumerate(images, 1):
        name = f"image{i}.jpg"
        image_names.append(name)
        shutil.copyfile(src, tmp / "ppt" / "media" / name)

    slides: list[tuple[str, str | None]] = []
    slides.append((
        slide_xml([
            rect(2, 0, 0, SLIDE_W, SLIDE_H, "F7F8FA"),
            rect(3, 0, 0, 0.16, SLIDE_H, "2563EB"),
            text_box(4, "Claude Code\n上下文架构解析", 0.72, 0.72, 5.2, 1.45, 34, "111827", True),
            text_box(5, "17分钟视频素材整理版", 0.76, 2.32, 3.2, 0.35, 15, "4B5563"),
            bullet_box(6, ["音频已提取：audio.m4a", "关键帧已提取：12张 JPG", "本文件用于复盘视频结构与画面线索"], 0.74, 3.1, 4.75, 1.35, 16),
            picture(7, "rId1", 6.1, 0.7, 6.65, 5.6),
            text_box(8, "来源视频：AI大模型学习-Claude Code上下文架构解析，17分钟给你讲清楚.mp4", 0.74, 6.85, 11.2, 0.26, 10, "6B7280"),
        ]),
        simple_rels("../media/image1.jpg", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"),
    ))

    times = ["00:01:27", "00:02:54", "00:04:21", "00:05:48", "00:07:15", "00:08:42",
             "00:10:09", "00:11:36", "00:13:03", "00:14:30", "00:15:57", "00:17:24"]
    for i, (img, ts) in enumerate(zip(image_names[1:], times), 1):
        slides.append(image_slide(f"关键画面 {i}", f"视频时间点约 {ts}", img, i + 1))

    for i, (xml, rel) in enumerate(slides, 1):
        (tmp / "ppt" / "slides" / f"slide{i}.xml").write_text(xml, encoding="utf-8")
        if rel:
            (tmp / "ppt" / "slides" / "_rels" / f"slide{i}.xml.rels").write_text(rel, encoding="utf-8")

    (tmp / "[Content_Types].xml").write_text(content_types(image_names), encoding="utf-8")
    (tmp / "_rels" / ".rels").write_text(rels_root(), encoding="utf-8")
    (tmp / "docProps" / "app.xml").write_text(app_xml(), encoding="utf-8")
    (tmp / "docProps" / "core.xml").write_text(core_xml(), encoding="utf-8")
    (tmp / "ppt" / "presentation.xml").write_text(presentation_xml(len(slides)), encoding="utf-8")
    (tmp / "ppt" / "_rels" / "presentation.xml.rels").write_text(presentation_rels(len(slides)), encoding="utf-8")
    (tmp / "ppt" / "theme" / "theme1.xml").write_text(theme_xml(), encoding="utf-8")
    (tmp / "ppt" / "slideMasters" / "slideMaster1.xml").write_text(master_xml(), encoding="utf-8")
    (tmp / "ppt" / "slideMasters" / "_rels" / "slideMaster1.xml.rels").write_text(
        simple_rels("../slideLayouts/slideLayout1.xml", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout"),
        encoding="utf-8",
    )
    (tmp / "ppt" / "slideLayouts" / "slideLayout1.xml").write_text(layout_xml(), encoding="utf-8")
    (tmp / "ppt" / "slideLayouts" / "_rels" / "slideLayout1.xml.rels").write_text(
        simple_rels("../slideMasters/slideMaster1.xml", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster"),
        encoding="utf-8",
    )

    if OUT.exists():
        OUT.unlink()
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in sorted(tmp.rglob("*")):
            if file.is_file():
                zf.write(file, file.relative_to(tmp).as_posix())
    shutil.rmtree(tmp)

    ET.parse(zipfile.ZipFile(OUT).open("ppt/presentation.xml"))
    print(OUT)
    print(f"slides={len(slides)}")
    print(f"size={os.path.getsize(OUT)}")


if __name__ == "__main__":
    package()
