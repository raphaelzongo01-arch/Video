import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine, music
# usage : python3 render.py <module_video> <sortie.mp4> [--musique]
name, out = sys.argv[1], sys.argv[2]
engine.render_video(name, out, music.ambient if "--musique" in sys.argv else None)
