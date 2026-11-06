#!/usr/bin/env python3
"""Pasul 1 al montajului: fiecare clip brut (.mov) devine un clip „curat”, cu culoarea Kristine Maia, gata pentru program și reel-uri.
Rulezi: python3 studio/montaj/curat.py <clip.mov> <ieșire.mp4> [--luminos]   (--luminos: pentru lumină slabă)

Ce face (GRADE, schimbi într-un singur loc):
  · 1080 x 1920, 30 fps, fără sunet
  · zgomot redus (hqdn3d), contrast blând, luminile de pe piele coborâte (fără față „arsă”), culori naturale (vibrance mic),
    claritate ușoară (unsharp), vignetă foarte discretă"""
import subprocess, sys
GRADE = ("hqdn3d=1.5:1.5:6:6,curves=master='0/0 0.15/0.13 0.5/0.48 0.8/0.75 1/0.92',"   # 6 nov: mai puțină lumină pe piele, alb mai blând
         "colorbalance=rs=0.01:bs=-0.01:rh=-0.02:gh=-0.01,vibrance=intensity=0.1,unsharp=5:5:0.5:5:5:0.0,vignette=angle=PI/7")
def dur(p): return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p], capture_output=True, text=True).stdout)
# pentru clipurile filmate în lumină slabă: ridică umbrele și expunerea înainte de culoare, zgomot redus mai tare
LUMINOS = "hqdn3d=3:3:8:8,eq=gamma=1.22:brightness=0.035:saturation=1.05,"
def ruleaza(src, out, luminos=False):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-vf', 'fps=30,scale=1080:1920:flags=lanczos,%s%s,format=yuv420p' % (LUMINOS if luminos else '', GRADE), '-an',
                    '-c:v', 'libx264', '-preset', 'medium', '-crf', '15', '-movflags', '+faststart', out], check=True)
    print('curat:', out)
if __name__ == '__main__':
    ruleaza(sys.argv[1], sys.argv[2], '--luminos' in sys.argv)
