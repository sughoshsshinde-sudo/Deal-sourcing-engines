import os, urllib.parse, time
from datetime import datetime
import pandas as pd
import requests
from dotenv import load_dotenv

BASE_DIR = r"C:\Users\Sughosh\Downloads\RegTech"
OUT_DIR = os.path.join(BASE_DIR, "Master Sourcing Results")
HF_LIMIT = 30
GH_LIMIT = 20
TEST_MODE = True
TEST_ROWS_PER_SOURCE = 25
GH_PUSHED_AFTER = "2025-01-01"

THESIS = {
    "RegTech / Compliance": ["regtech","regulatory technology","regulatory compliance","compliance","compliance ai","compliance agent","compliance automation","regulatory reporting","regulatory intelligence","financial crime","aml","anti-money laundering","kyc","kyb","sanctions","sanction screening","watchlist screening","pep screening","transaction monitoring","fraud detection","fraud prevention","governance","ai governance","model governance","model risk","risk management","enterprise risk","grc","internal audit","audit ai","internal controls","third party risk","legal ai","legaltech","contract ai","contract intelligence","privacy ai","data governance","privacy compliance","legal compliance","identity verification","kyc infrastructure","audit trail","policy engine"],
    "Cybersecurity": ["cybersecurity","cyber security","application security","appsec","cloud security","network security","endpoint security","identity security","access management","iam","zero trust","threat detection","threat intelligence","security automation","security platform","security agent","security ai","ai security","security operations","soc","vulnerability management","penetration testing","devsecops","secrets management","data security","privacy engineering","software supply chain security","api security","container security","cloud posture"],
    "Enterprise SaaS / AI": ["enterprise ai","enterprise agent","ai agent","agentic ai","workflow automation","enterprise automation","back office ai","business process automation","enterprise software","enterprise saas","b2b saas","b2b","saas","workflow","business automation","operations automation","developer tools","devtools","productivity platform","knowledge management","data infrastructure","ai infrastructure","llm infrastructure","rag","retrieval augmented generation","ai evaluation","ai observability","model monitoring","document intelligence","document ai"],
    "Blockchain / Crypto Infrastructure": ["blockchain","web3 infrastructure","crypto infrastructure","crypto compliance","crypto aml","virtual asset","virtual asset compliance","vasp","vasp compliance","travel rule","on-chain compliance","blockchain analytics","on-chain analytics","wallet security","crypto security","blockchain security","institutional custody","digital assets","digital asset infrastructure","zk-kyc","zero knowledge identity","verifiable credentials","decentralized identity"]
}
TERM_CATEGORY = {t:c for c,ts in THESIS.items() for t in ts}
KEYWORDS = list(TERM_CATEGORY)

load_dotenv()
TOKEN = os.getenv("GITHUB_TOKEN")
if not TOKEN:
    raise SystemExit("GitHub token not found. Check .env")

GH_HEADERS = {"Authorization":f"Bearer {TOKEN}","Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"}

def get_json(url, headers=None, params=None):
    try:
        r=requests.get(url,headers=headers or {},params=params,timeout=20)
        r.raise_for_status(); return r.json()
    except Exception as e:
        print(f"   Request failed: {e}"); return None

def age_days(s):
    try: return (datetime.now()-datetime.strptime(str(s)[:10],"%Y-%m-%d")).days
    except: return None

def score(category, keyword, project, desc="", bio="", topics="", stars=0, likes=0, downloads=0, updated="", ptype="", **kw):
    text=" ".join(map(str,[keyword,project,desc,bio,topics])).lower()
    s=15; sig=[f"keyword: {keyword}"]
    hits=[t for t in THESIS[category] if t.lower() in text and t.lower()!=keyword.lower()]
    s += min(5*len(hits[:4]),20); sig += [f"thesis: {x}" for x in hits[:4]]
    builder=[x for x in ["building","builder","founder","startup","product","platform","api","application","software","saas","agent","automation","infrastructure"] if x in text]
    if builder: s+=min(2*len(builder),8); sig.append("builder/product: "+", ".join(builder[:4]))
    tech=[x for x in ["python","pytorch","tensorflow","transformers","llm","machine learning","deep learning","api","agent","rag","kubernetes","docker","postgres","redis"] if x in text]
    if tech: s+=min(2*len(tech),8); sig.append("technical: "+", ".join(tech[:5]))
    age=age_days(updated)
    if age is not None:
        if age<=90: s+=8; sig.append("updated <=90 days")
        elif age<=180: s+=4; sig.append("updated <=6 months")
        elif age<=365: s+=1; sig.append("updated <=12 months")
    try: stars=int(stars or 0)
    except: stars=0
    try: likes=int(likes or 0)
    except: likes=0
    try: downloads=int(downloads or 0)
    except: downloads=0
    if stars>=100: s+=8; sig.append("100+ stars")
    elif stars>=25: s+=5; sig.append("25+ stars")
    elif stars>=10: s+=2; sig.append("10+ stars")
    if likes>=100: s+=6; sig.append("100+ HF likes")
    elif likes>=25: s+=3; sig.append("25+ HF likes")
    elif likes>=10: s+=1; sig.append("10+ HF likes")
    if downloads>=100000: s+=6; sig.append("100k+ downloads")
    elif downloads>=10000: s+=4; sig.append("10k+ downloads")
    elif downloads>=1000: s+=2; sig.append("1k+ downloads")
    if ptype=="HF Space": s+=5; sig.append("HF Space")
    s=min(s,100)
    return s, ("HIGH" if s>=55 else "MEDIUM" if s>=30 else "LOW"), "; ".join(sig)

def base_row(source, category, keyword, person, project, ptype, profile, project_url, **kw):
    sc,pri,sig=score(category,keyword,project,ptype=ptype,**kw)
    return {"Source":source,"Category":category,"Discovery Keyword":keyword,"Person / Handle":person,"Project":project,"Project Type":ptype,"Description":kw.get("desc","") or "","Bio":kw.get("bio","") or "","Company":kw.get("company","") or "","Location":kw.get("location","") or "","Website":kw.get("website","") or "","Profile URL":profile,"Project URL":project_url,"Language":kw.get("language","") or "","Framework / Library":kw.get("framework","") or "","Model / Pipeline":kw.get("model","") or "","Topics / Tags":kw.get("topics","") or "","Stars / Likes":kw.get("stars",kw.get("likes",0)) or 0,"Downloads":kw.get("downloads","") or "","Forks":kw.get("forks","") or "","Created At":kw.get("created","") or "","Last Updated":kw.get("updated","") or "","Discovery Score":sc,"Discovery Priority":pri,"Discovery Signals":sig,"Technical Analysis":"NOT ANALYSED","LinkedIn":"","LinkedIn Confidence":"","Outreach Status":""}

def hf_discovery():
    rows={}
    for i,k in enumerate(KEYWORDS,1):
        cat=TERM_CATEGORY[k]; print(f"[HF {i}/{len(KEYWORDS)}] {k}")
        models=get_json("https://huggingface.co/api/models",params={"search":k,"limit":HF_LIMIT}) or []
        for m in models:
            item=m.get("id","")
            if "/" not in item: continue
            author,repo=item.split("/",1); key=(author.lower(),repo.lower(),"model")
            if key not in rows:
                rows[key]=base_row("Hugging Face",cat,k,author,repo,"HF Model",f"https://huggingface.co/{author}",f"https://huggingface.co/{item}",likes=m.get("likes",0),downloads=m.get("downloads",0),updated=m.get("lastModified",""),topics=", ".join(m.get("tags",[]) or []),framework=m.get("library_name","") or "",model=m.get("pipeline_tag","") or "")
        spaces=get_json("https://huggingface.co/api/spaces",params={"search":k,"limit":HF_LIMIT}) or []
        for m in spaces:
            item=m.get("id","")
            if "/" not in item: continue
            author,repo=item.split("/",1); key=(author.lower(),repo.lower(),"space")
            if key not in rows:
                rows[key]=base_row("Hugging Face",cat,k,author,repo,"HF Space",f"https://huggingface.co/{author}",f"https://huggingface.co/spaces/{item}",likes=m.get("likes",0),updated=m.get("lastModified",""))
        time.sleep(.15)
    return list(rows.values())

def github_discovery():
    rows={}; profiles={}
    for i,k in enumerate(KEYWORDS,1):
        cat=TERM_CATEGORY[k]; print(f"[GH {i}/{len(KEYWORDS)}] {k}")
        data=get_json("https://api.github.com/search/repositories",headers=GH_HEADERS,params={"q":f"{k} pushed:>{GH_PUSHED_AFTER}","sort":"updated","order":"desc","per_page":GH_LIMIT}) or {}
        for item in data.get("items",[]):
            owner=item.get("owner",{})
            if owner.get("type")!="User": continue
            handle=owner.get("login",""); repo=item.get("name",""); key=(handle.lower(),repo.lower())
            if key in rows: continue
            rows[key]=base_row("GitHub",cat,k,handle,repo,"GitHub Repository",owner.get("html_url",f"https://github.com/{handle}"),item.get("html_url",""),desc=item.get("description","") or "",stars=item.get("stargazers_count",0),forks=item.get("forks_count",0),language=item.get("language","") or "",topics=", ".join(item.get("topics",[]) or []),created=item.get("created_at","")[:10],updated=item.get("updated_at","")[:10])
    for idx,row in enumerate(rows.values(),1):
        h=row["Person / Handle"]
        if h not in profiles: profiles[h]=get_json(f"https://api.github.com/users/{h}",headers=GH_HEADERS) or {}
        p=profiles[h]; row.update({"Bio":p.get("bio","") or "","Company":p.get("company","") or "","Location":p.get("location","") or "","Website":p.get("blog","") or ""})
        sc,pri,sig=score(row["Category"],row["Discovery Keyword"],row["Project"],row["Description"],row["Bio"],row["Topics / Tags"],row["Stars / Likes"],updated=row["Last Updated"],ptype=row["Project Type"])
        row.update({"Discovery Score":sc,"Discovery Priority":pri,"Discovery Signals":sig})
    return list(rows.values())

def main():
    print("="*70); print("MASTER FOUNDER DISCOVERY ENGINE — HF + GITHUB"); print("="*70)
    print("Thesis: RegTech/Compliance + Cybersecurity + Enterprise SaaS/AI + Blockchain/Crypto infrastructure")
    hf=hf_discovery(); print(f"\nHF rows: {len(hf)}")
    gh=github_discovery(); print(f"GitHub rows: {len(gh)}")
    if TEST_MODE:
        hf=hf[:TEST_ROWS_PER_SOURCE]; gh=gh[:TEST_ROWS_PER_SOURCE]
        print(f"\nTEST MODE: exporting up to {TEST_ROWS_PER_SOURCE} rows from each source.")
    df=pd.DataFrame(hf+gh).drop_duplicates(subset=["Source","Person / Handle","Project","Project Type"])
    df=df.sort_values(["Discovery Score","Stars / Likes"],ascending=False,na_position="last")
    os.makedirs(OUT_DIR,exist_ok=True)
    fn=os.path.join(OUT_DIR,f"master_founder_discovery_{datetime.now().strftime('%Y%m%d_%H%M')}.csv")
    df.to_csv(fn,index=False,encoding="utf-8-sig")
    print("\n"+"="*70); print("COMPLETE"); print("="*70)
    print(f"Rows exported: {len(df)}"); print("\nSources:\n",df["Source"].value_counts().to_string())
    print("\nCategories:\n",df["Category"].value_counts().to_string())
    print("\nPriorities:\n",df["Discovery Priority"].value_counts().to_string())
    print(f"\nSaved: {fn}")
    print("\nNext stage will inspect actual repositories/models/code. This script does not do that yet.")

if __name__=="__main__": main()
