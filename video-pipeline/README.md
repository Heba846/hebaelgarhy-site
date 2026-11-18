# Short 01 (AR) render pipeline
1. `python3 tts2.py` — ElevenLabs TTS with timestamps (segments.json → audio/).
2. `python3 build.py` — builds timeline.js (cues/captions) + SFX + audio_mix.wav.
3. Put fonts (Cairo 700/800, Amiri 400, Aref Ruqaa 700 woff2 from @fontsource) in `fonts/`.
4. `OUT=frames node render.js <worker> <nworkers> 30` (run 4 in parallel), then
   `ffmpeg -framerate 30 -i frames/f%05d.jpg -i audio_mix.wav -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac out.mp4`
