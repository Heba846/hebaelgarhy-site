import json,re,subprocess,numpy as np,wave
segs=json.load(open('segments.json',encoding='utf8'))
DIA=re.compile('[ً-ٰٟۖ-ۭـ]')
GAP=0.5; t=0.5
anchors=[
 {"maa":"وَمَعَ","qub":"قُبِلَتْ"},
 {},
 {"qatala":"فقتلَهُ","nope":"ليست","mia":"المئة"},
 {"quote":"وَمَنْ","ref":"التَّوبة"},
 {"qawm":"قومٌ","kharaja":"فخرج","mawt":"أدركَ"},
 {"qisu":"قِيسُوا"},
 {"shibr":"بِشِبْر","ghufira":"فَغُفِرَ"},
 {"iktub":"اكتبْ","ursil":"وأرسلها"},
]
gold=[["قبلت"],["نظرتك"],["راهب","المئة"],["عالم","التوبة"],["صالحون","أرض","سوء","الموت"],["ملائكة","بينهما"],["بشبر"],["رجعت"]]
TL=[];CAP=[]
for i,s in enumerate(segs):
    al=json.load(open(f'audio/s{i+1}.align.json',encoding='utf8'))
    ch=al["characters"];st=al["character_start_times_seconds"];en=al["character_end_times_seconds"]
    txt=s["tts"]; assert ''.join(ch)==txt, (i,)
    dur=en[-1]+0.15
    cue={}
    for k,a in anchors[i].items():
        j=txt.find(a); assert j>=0,(i,a); cue[k]=round(t+st[j],3)
    TL.append({"start":round(t,3),"end":round(t+dur,3),"cue":cue})
    # words
    words=[];cur=[];
    for j,c in enumerate(txt):
        if c==' ':
            if cur: words.append(cur);cur=[]
        else: cur.append(j)
    if cur: words.append(cur)
    W=[]
    for idx in words:
        raw=''.join(txt[j] for j in idx); disp=DIA.sub('',raw)
        disp=disp.replace('…','…')
        base=re.sub('[…؟:،.]','',disp)
        W.append({"w":disp,"g":base in gold[i],"t0":t+st[idx[0]],"t1":t+en[idx[-1]]})
    # chunk
    chunks=[];cur=[]
    for w in W:
        cur.append(w)
        if len(cur)>=3 or re.search('[…؟.]$',w["w"]): chunks.append(cur);cur=[]
    if cur: chunks.append(cur)
    for k,c in enumerate(chunks):
        t0=c[0]["t0"]; t1=chunks[k+1][0]["t0"] if k+1<len(chunks) else c[-1]["t1"]+0.1
        CAP.append({"t0":round(t0,3),"t1":round(t1,3),"words":[{"w":w["w"],"g":w["g"]} for w in c]})
    t+=dur+GAP
TOTAL=round(TL[-1]["end"]+2.6,2)
open('timeline.js','w',encoding='utf8').write(f"window.TL={json.dumps(TL)};window.TOTAL={TOTAL};window.CAP={json.dumps(CAP,ensure_ascii=False)};")
json.dump({"TL":TL,"TOTAL":TOTAL},open('tl.json','w'))
print(TOTAL,TL[2]["cue"],TL[4]["cue"])
# ---- audio
SR=44100;N=int(TOTAL*SR)
sfx=np.zeros(N,dtype=np.float32)
def add(t0,sig,g=1.0):
    i=int(t0*SR);j=min(N,i+len(sig));sfx[i:j]+=sig[:j-i]*g
def thump(f=55,d=1.2):
    x=np.arange(int(d*SR))/SR;return np.sin(2*np.pi*(f+30*np.exp(-x*8))*x)*np.exp(-x*3.2)
def chime(f,d=2.2):
    x=np.arange(int(d*SR))/SR;return (np.sin(2*np.pi*f*x)+.4*np.sin(2*np.pi*f*2.01*x)+.2*np.sin(2*np.pi*f*3*x))*np.exp(-x*2.0)*(1-np.exp(-x*60))
def tick(d=.06):
    x=np.arange(int(d*SR))/SR;return np.sin(2*np.pi*1800*x)*np.exp(-x*70)
def whoosh(d=1.0):
    n=np.random.RandomState(1).randn(int(d*SR));k=np.ones(200)/200;n=np.convolve(n,k,'same');x=np.linspace(0,1,len(n));return n*np.sin(np.pi*x)**2*8
add(0.3,thump(),0.8)
c=TL[0]["cue"];add(c["qub"],chime(660),0.35)
add(TL[1]["start"],thump(45,1.6),0.6);add(TL[1]["start"],whoosh(),0.25)
c=TL[2]["cue"];add(c["nope"],thump(70,.9),0.6);add(c["mia"]+0.4,chime(523),0.4)
c=TL[3]["cue"];add(c["quote"],chime(440),0.3);add(c["quote"]+0.1,whoosh(),0.2)
c=TL[4]["cue"];add(c["kharaja"],whoosh(3.0),0.2);add(c["mawt"],thump(50,1.5),0.7)
c=TL[5]["cue"]
for k in range(12):add(c["qisu"]+0.6+k*0.17,tick(),0.25)
c=TL[6]["cue"];add(c["shibr"],chime(784,1.6),0.35);add(c["ghufira"],chime(523,3.0),0.5);add(c["ghufira"],chime(784,3.0),0.35);add(c["ghufira"],chime(1046,3.0),0.25)
add(TL[7]["start"]+0.1,whoosh(.8),0.2);add(TL[7]["cue"]["iktub"],chime(880,1.8),0.3)
# soft drone bed (noise-based, no instruments)
bed=np.convolve(np.random.RandomState(3).randn(N),np.ones(800)/800,'same').astype(np.float32)*0.9
sfx+=bed*0.035
sfx=np.clip(sfx*0.6,-1,1)
w=wave.open('sfx.wav','wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((sfx*32767).astype('<i2').tobytes());w.close()
inputs=[];filt=[]
for i,s in enumerate(TL):
    inputs+=['-i',f'audio/s{i+1}.mp3'];filt.append(f"[{i}:a]adelay={int(s['start']*1000)}|{int(s['start']*1000)},volume=1.6[v{i}]")
inputs+=['-i','sfx.wav']
mix=''.join(f'[v{i}]' for i in range(len(TL)))+f'[{len(TL)}:a]'
filt.append(f"{mix}amix=inputs={len(TL)+1}:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
subprocess.run(['ffmpeg','-y','-loglevel','error',*inputs,'-filter_complex',';'.join(filt),'-map','[a]','-t',str(TOTAL),'-ar','44100','audio_mix.wav'],check=True)
print('audio ok')
