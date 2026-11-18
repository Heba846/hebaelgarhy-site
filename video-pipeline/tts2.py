import json,base64,urllib.request
VOICE="Rcau5bjEnkLqbLj7rnLI"
segs=json.load(open('segments.json',encoding='utf8'))
for i,s in enumerate(segs):
    body=json.dumps({"text":s["tts"],"model_id":"eleven_multilingual_v2","voice_settings":{"stability":0.55,"similarity_boost":0.75,"style":0.15,"use_speaker_boost":True}}).encode()
    req=urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps?output_format=mp3_44100_128",data=body,headers={"Content-Type":"application/json"})
    r=json.loads(urllib.request.urlopen(req,timeout=180).read())
    open(f"audio/s{i+1}.mp3","wb").write(base64.b64decode(r["audio_base64"]))
    json.dump(r["alignment"],open(f"audio/s{i+1}.align.json","w"),ensure_ascii=False)
    print(i+1,len(r["alignment"]["characters"]),r["alignment"]["character_end_times_seconds"][-1])
