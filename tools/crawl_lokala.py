import re,html,json,urllib.request,concurrent.futures as cf
def get(u,t=25):
    try:
        r=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})
        return urllib.request.urlopen(r,timeout=t).read().decode('utf-8','ignore')
    except Exception as e: return ''
base='https://lokala.cz'
slugs=set(); cats=set()
h=get(base+'/znacky')
cats|=set(re.findall(r'href="(/znacky/\d+)"',h)); slugs|=set(re.findall(r'href="/znacka/([^"]+)"',h))
for c in sorted(cats):
    for p in range(1,40):
        h=get(f'{base}{c}?page={p}' if p>1 else base+c)
        s=set(re.findall(r'href="/znacka/([^"]+)"',h))
        if not s or s<=slugs and p>1: 
            if not s: break
        slugs|=s
print(len(cats),len(slugs))
def parse(slug):
    h=get(f'{base}/znacka/{slug}')
    t=re.sub(r'<script.*?</script>|<style.*?</style>','',h,flags=re.S)
    t=html.unescape(re.sub(r'<[^>]+>','\n',t)); t=re.sub(r'\s*\n\s*','|',t)
    def f(k):
        m=re.search(k+r':\|([^|]*)',t); return m.group(1).strip() if m else ''
    web=re.search(r'Web:\|(https?://[^|\s]+)',t)
    name=re.search(r'<h1[^>]*>(.*?)</h1>',h,flags=re.S)
    return dict(slug=slug,name=html.unescape(re.sub('<[^>]+>','',name.group(1))).strip() if name else slug,
      made=f('Místo výroby'),seat=f('Sídlo značky'),owner=f('Majitel'),founded=f('Založeno'),web=web.group(1) if web else '',url=f'{base}/znacka/{slug}')
with cf.ThreadPoolExecutor(12) as ex: rows=list(ex.map(parse,sorted(slugs)))
json.dump(rows,open('lokala.json','w'),ensure_ascii=False,indent=1)
print(rows[:3])
