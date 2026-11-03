#!/usr/bin/env python3
"""Pasul 1 al montajului: fiecare clip brut (.mov) devine un clip „curat”, cu culoarea Kristine Maia, gata pentru program și reel-uri.
Rulezi: python3 studio/montaj/curat.py <clip.mov> <ieșire.mp4> [--luminos]   (--luminos: pentru lumină slabă)

Ce face (GRADE, schimbi într-un singur loc):
  · 1080 x 1920, 30 fps, fără sunet
  · zgomot redus (hqdn3d), negru mai adânc și alb curat (curbă S ușoară), ton ușor cald fără piele portocalie (colorbalance),
    culori vii doar unde sunt șterse (vibrance), claritate ușoară (unsharp), vignetă discretă"""
import subprocess, sys
GRADE = ("hqdn3d=1.5:1.5:6:6,curves=master='0/0 0.12/0.08 0.5/0.52 0.85/0.88 1/0.97',"
         "colorbalance=rs=0.025:bs=-0.025:rm=0.015:bm=-0.015,vibrance=intensity=0.2,unsharp=5:5:0.6:5:5:0.0,vignette=angle=PI/5")
def dur(p): return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p], capture_output=True, text=True).stdout)
# pentru clipurile filmate în lumină slabă: ridică umbrele și expunerea înainte de culoare, zgomot redus mai tare
LUMINOS = "hqdn3d=3:3:8:8,eq=gamma=1.22:brightness=0.035:saturation=1.05,"
def ruleaza(src, out, luminos=False):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-vf', 'fps=30,scale=1080:1920:flags=lanczos,%s%s,format=yuv420p' % (LUMINOS if luminos else '', GRADE), '-an',
                    '-c:v', 'libx264', '-preset', 'medium', '-crf', '15', '-movflags', '+faststart', out], check=True)
    print('curat:', out)
if __name__ == '__main__':
    ruleaza(sys.argv[1], sys.argv[2], '--luminos' in sys.argv)
