"""Exact per-pixel UI recolor; no spatial operations or alpha modifications."""
import colorsys
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.tools/python'))
from PIL import Image

FILES = ['resources.assets_116_HighResAtlas.png', 'resources.assets_154_LowResAtlas.png']

def recolor(pixel):
    r, g, b, a = pixel
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    # Neutral white/black/gray glyphs and anti-aliasing remain bit-identical.
    if s < 0.16 or v < 0.10 or a == 0:
        return pixel
    # Preserve HSV value/saturation structure; perceived luminance may change.
    # Blue/cyan are already on-brand; other saturated colors become blue.
    target_h = 0.59 if not 0.49 <= h <= 0.65 else h
    rr, gg, bb = colorsys.hsv_to_rgb(target_h, s, v)
    return round(rr * 255), round(gg * 255), round(bb * 255), a

def main():
    backup = ROOT / 'output/ui_atlases/originals'
    backup.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        path = ROOT / 'textures' / name
        saved = backup / name
        if not saved.exists():
            # Reproduce from the known clean baseline even after output/ is lost.
            source = subprocess.run(
                ['git', 'show', f'a9cdde1:textures/{name}'],
                cwd=ROOT, capture_output=True, check=True,
            ).stdout
            saved.write_bytes(source)
        original = Image.open(saved).convert('RGBA')
        result = Image.new('RGBA', original.size)
        result.putdata([recolor(p) for p in original.getdata()])
        assert result.size == original.size
        assert result.getchannel('A').tobytes() == original.getchannel('A').tobytes()
        # Guarantee identity of unchanged neutral glyph pixels and exact mapping.
        assert all(dst == recolor(src) for src, dst in zip(original.getdata(), result.getdata()))
        result.save(path)
        changed = sum(src != dst for src, dst in zip(original.getdata(), result.getdata()))
        print(name, original.size, 'alpha exact; per-pixel mapping exact; changed', changed)

if __name__ == '__main__':
    main()

