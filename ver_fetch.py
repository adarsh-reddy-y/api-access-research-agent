import sys,re,requests
from bs4 import BeautifulSoup
UA={"User-Agent":"Mozilla/5.0 (compatible; research-bot/1.0)"}
def txt(u):
    try:
        r=requests.get(u,headers=UA,timeout=25)
        if "html" in r.headers.get("content-type",""):
            s=BeautifulSoup(r.text,"html.parser")
            for t in s(["script","style","nav","footer"]): t.decompose()
            return r.status_code,re.sub(r"\s+"," ",s.get_text(" "))
        return r.status_code,re.sub(r"\s+"," ",r.text)
    except Exception as e: return str(type(e).__name__),""
def go(u,pat,n=3,w=170):
    c,t=txt(u); print(f"## {u} [{c}] chars={len(t)}")
    ms=[t[max(0,m.start()-w):m.end()+w] for m in re.finditer(pat,t,re.I)][:n]
    if not ms: print("  head:",t[:300])
    for m in ms: print("  >",m)
if __name__=="__main__":
    go(sys.argv[1],sys.argv[2],int(sys.argv[3]) if len(sys.argv)>3 else 3)
