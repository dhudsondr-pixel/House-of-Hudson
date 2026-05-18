"""Assemble the final video: stock clips + voiceover + Pillow-rendered captions."""
from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import (
    AudioFileClip,
    CompositeVideoClip,
    ImageClip,
    VideoFileClip,
    concatenate_videoclips,
)


def _resize_and_crop(clip: VideoFileClip, target_w: int, target_h: int) -> VideoFileClip:
    """Resize+center-crop a clip to the target dimensions without distortion."""
    cw, ch = clip.w, clip.h
    target_ratio = target_w / target_h
    source_ratio = cw / ch

    if source_ratio > target_ratio:
        new_h = target_h
        new_w = int(cw * (target_h / ch))
        clip = clip.resize(newsize=(new_w, new_h))
        x_center = new_w / 2
        return clip.crop(x1=x_center - target_w / 2, y1=0, x2=x_center + target_w / 2, y2=target_h)
    else:
        new_w = target_w
        new_h = int(ch * (target_w / cw))
        clip = clip.resize(newsize=(new_w, new_h))
        y_center = new_h / 2
        return clip.crop(x1=0, y1=y_center - target_h / 2, x2=target_w, y2=y_center + target_h / 2)


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    """Try a series of common fonts; fall back to PIL default if none found."""
    candidates = [
        "/System/Library/Fonts/Supplemental/Impact.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "C:\\Windows\\Fonts\\impact.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
    """Word-wrap by measuring rendered width."""
    words = text.split()
    lines: List[str] = []
    current = ""
    for w in words:
        trial = (current + " " + w).strip()
        bbox = font.getbbox(trial)
        width = bbox[2] - bbox[0]
        if width <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines


def _render_caption_image(text: str, video_w: int, video_h: int) -> np.ndarray:
    """Render a caption with thick black stroke + white fill onto a transparent image."""
    fontsize = max(48, video_w // 16)
    font = _load_font(fontsize)
    stroke_w = max(3, fontsize // 14)

    text = text.upper()
    max_text_width = int(video_w * 0.85)
    lines = _wrap_text(text, font, max_text_width)

    # Measure block size.
    line_heights = []
    line_widths = []
    for ln in lines:
        bbox = font.getbbox(ln)
        line_widths.append(bbox[2] - bbox[0])
        line_heights.append(bbox[3] - bbox[1])
    line_gap = int(fontsize * 0.25)
    block_h = sum(line_heights) + line_gap * (len(lines) - 1) if lines else 0
    block_w = max(line_widths) if line_widths else 0

    # Generous padding so stroke isn't clipped.
    pad = stroke_w * 3
    img = Image.new("RGBA", (block_w + pad * 2, block_h + pad * 2), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    y = pad
    for ln, lh in zip(lines, line_heights):
        bbox = font.getbbox(ln)
        line_w = bbox[2] - bbox[0]
        x = pad + (block_w - line_w) // 2
        draw.text(
            (x, y),
            ln,
            font=font,
            fill=(255, 255, 255, 255),
            stroke_width=stroke_w,
            stroke_fill=(0, 0, 0, 255),
        )
        y += lh + line_gap

    return np.array(img)


def _render_watermark_image(text: str, video_w: int) -> np.ndarray:
    fontsize = max(28, video_w // 36)
    font = _load_font(fontsize)
    bbox = font.getbbox(text)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    pad = fontsize // 2
    img = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.text(
        (pad, pad),
        text,
        font=font,
        fill=(255, 255, 255, 230),
        stroke_width=2,
        stroke_fill=(0, 0, 0, 230),
    )
    return np.array(img)


def assemble(
    clip_paths: List[Path],
    audio_path: Path,
    captions: List[str],
    out_path: Path,
    resolution: str = "1080x1920",
    channel_name: str = "",
) -> Path:
    target_w, target_h = (int(x) for x in resolution.lower().split("x"))

    audio = AudioFileClip(str(audio_path))
    total_dur = audio.duration

    raw_clips = [VideoFileClip(str(p)).without_audio() for p in clip_paths]
    raw_clips = [c.subclip(0, min(c.duration, 5.0)) for c in raw_clips if c.duration > 0.3]
    if not raw_clips:
        raise RuntimeError("No usable stock clips.")

    sequence = []
    accumulated = 0.0
    idx = 0
    while accumulated < total_dur + 0.5:
        c = raw_clips[idx % len(raw_clips)]
        sequence.append(c)
        accumulated += c.duration
        idx += 1

    video = concatenate_videoclips(sequence, method="compose").subclip(0, total_dur)
    video = _resize_and_crop(video, target_w, target_h)
    video = video.set_audio(audio)

    overlays = []
    if captions:
        per = total_dur / len(captions)
        for i, cap in enumerate(captions):
            try:
                img_arr = _render_caption_image(cap, target_w, target_h)
                clip = (
                    ImageClip(img_arr, transparent=True)
                    .set_position(("center", int(target_h * 0.68)))
                    .set_start(i * per)
                    .set_duration(per)
                )
                overlays.append(clip)
            except Exception as e:
                print(f"  [warn] caption render failed for '{cap}': {e}")

    if channel_name:
        try:
            wm_arr = _render_watermark_image(channel_name, target_w)
            wm = (
                ImageClip(wm_arr, transparent=True)
                .set_position(("center", int(target_h * 0.05)))
                .set_duration(total_dur)
            )
            overlays.append(wm)
        except Exception:
            pass

    final = CompositeVideoClip([video, *overlays], size=(target_w, target_h))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    final.write_videofile(
        str(out_path),
        fps=30,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        threads=4,
        logger=None,
    )

    audio.close()
    for c in raw_clips:
        c.close()
    final.close()

    return out_path
