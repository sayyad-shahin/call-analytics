import json, subprocess, tempfile, wave, os
VOICES = {"agent": ["-v", "en-us+f3", "-s", "150"], "customer": ["-v", "en-us+m3", "-s", "145"]}
base = os.path.dirname(os.path.abspath(__file__))
calls = json.load(open(os.path.join(base, "data", "calls.json")))
for c in calls:
    frames, params = [], None
    for who, text in c["turns"]:
        with tempfile.NamedTemporaryFile(suffix=".wav") as t:
            subprocess.run(["espeak-ng", *VOICES[who], "-w", t.name, text], check=True)
            with wave.open(t.name) as w:
                params = params or w.getparams()
                frames.append(w.readframes(w.getnframes()))
        frames.append(b"\x00\x00" * int(params.framerate * 0.5))
    out = os.path.join(base, "audio", c["file"])
    with wave.open(out, "wb") as w:
        w.setparams(params); w.writeframes(b"".join(frames))
    print("wrote", out)
