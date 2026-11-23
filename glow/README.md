# Vidéos « glow » (style fond noir + personnages lumineux)

Format 1920×1080, 30 i/s, voix off française d'homme (Piper « miro », via `voice.py`), musique d'ambiance générée.

Voix : modèles Piper récupérés sur github.com/k2-fsa/sherpa-onnx (releases `tts-models`, ex. `vits-piper-fr_FR-miro-high`),
à placer dans `assets/voices/<nom>/<nom>.onnx` + `.onnx.json`. Changer `VOICE` (miro, tom, jessica, siwis) et `SPEED`
en haut de chaque fichier vidéo pour changer de voix ou de débit.

- `video_attente.py` : « Le bon moment n'existe pas »
- `video_un_pourcent.py` : « 1 % par jour »

## Générer

```bash
pip install skia-python piper-tts kokoro-onnx soundfile numpy pillow
# modèles dans assets/ : kokoro-v1.0.onnx + voices-v1.0.bin
# (github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0)
cd glow
python3 render.py video_attente ../out/video1_le_bon_moment.mp4
python3 render.py video_un_pourcent ../out/video2_un_pourcent.mp4
```

## Faire une nouvelle vidéo

Copier un des fichiers `video_*.py`. Chaque scène = une liste de phrases (`say`) et une fonction `draw(c, T)`.
Dans le texte, `*mot*` s'affiche en italique serif. `T.pc(k, durée)` donne une progression 0→1 qui démarre
quand la phrase `k` de la scène commence à être dite : c'est ce qui synchronise les animations avec la voix.
