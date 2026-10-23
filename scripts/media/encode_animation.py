#!/usr/bin/env python3
"""Encode the OSS Blender frame sequence for browser/download/README playback."""
import argparse
import hashlib
import re
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
LABEL = (
    "drawbox=x=0:y=ih-32:w=iw:h=32:color=black@0.52:t=fill,"
    "drawtext=text='Blender reconstruction - intended motion':fontcolor=white:fontsize=18:x=12:y=h-24,"
    "drawtext=text='A side  /  B opposite  /  C end':fontcolor=white:fontsize=18:x=w-tw-12:y=h-24"
)


def run(args):
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', *args], check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frames', type=Path)
    args = parser.parse_args()
    expected = [args.frames / f'frame_{frame:04d}.png' for frame in range(1, 433)]
    if any(not path.is_file() for path in expected):
        parser.error('Expected all 432 Blender frames, frame_0001.png through frame_0432.png')
    media = ROOT / 'docs/media'
    mp4 = media / 'intended-sorting-simulation.mp4'
    webm = media / 'intended-sorting-simulation.webm'
    gif = media / 'intended-sorting-preview.gif'
    inputs = ['-framerate', '24', '-start_number', '1', '-i',
              str(args.frames / 'frame_%04d.png'), '-frames:v', '432']
    run([*inputs, '-vf', LABEL, '-c:v', 'libx264', '-profile:v', 'baseline',
         '-level:v', '3.1', '-crf', '20', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
         '-an', str(mp4)])
    run(['-i', str(mp4), '-c:v', 'libvpx-vp9', '-crf', '32', '-b:v', '0',
         '-row-mt', '1', '-pix_fmt', 'yuv420p', '-an', str(webm)])
    palette = ('fps=8,scale=800:-1:flags=lanczos,split[a][b];'
               '[a]palettegen=max_colors=128:stats_mode=diff[p];'
               '[b][p]paletteuse=dither=bayer:bayer_scale=5')
    run(['-i', str(mp4), '-vf', palette, '-loop', '0', str(gif)])
    # Content-specific URLs prevent an old cached clip surviving a rebuild.
    player = media / 'player.html'
    if player.exists():
        html = player.read_text()
        for name in [mp4.name, webm.name, gif.name, 'simulation-preview.png']:
            token = hashlib.sha256((media / name).read_bytes()).hexdigest()[:12]
            html = re.sub(r'((?:src|poster|href)=")' + re.escape(name) + r'(?:\?[^"]*)?(")',
                          lambda match: match.group(1) + name + '?v=' + token + match.group(2), html)
        player.write_text(html)
    print('Encoded MP4 (H.264 baseline), WebM (VP9), and looping README GIF.')


if __name__ == '__main__':
    main()
