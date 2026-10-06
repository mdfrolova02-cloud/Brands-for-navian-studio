import re,json,sys,html,urllib.request,urllib.parse,concurrent.futures as cf
UA={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36','Accept-Language':'cs,en;q=0.8'}
def get(u,t=15):
    try:
        return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=t).read().decode('utf-8','ignore')
    except Exception: return ''
EM=re.compile(r'[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}')
BAD=('example','sentry','wixpress','domain.','email.','yourname','.png','.jpg','.webp','.svg','godaddy','schema.org','jquery')
def enrich(url):
    out={'emails':[],'ig':'','fb':'','pages':[]}
    if not url: return out
    root=url if url.startswith('http') else 'https://'+url
    pages=[root]
    h=get(root); out['pages'].append(root)
    allh=h
    for l in re.findall(r'href=["\']([^"\']+)["\']',h):
        if re.search(r'kontakt|contact|o-nas|about|impressum',l,re.I) and len(pages)<4:
            u=urllib.parse.urljoin(root,l)
            if u not in pages and urllib.parse.urlparse(u).netloc.replace('www.','')==urllib.parse.urlparse(root).netloc.replace('www.',''): pages.append(u)
    for u in pages[1:]:
        allh+=get(u); out['pages'].append(u)
    ems=set(m.lower() for m in EM.findall(html.unescape(allh)) if not any(b in m.lower() for b in BAD))
    out['emails']=sorted(ems)
    ig=re.findall(r'instagram\.com/([A-Za-z0-9._]+)',allh)
    ig=[i for i in ig if i.lower() not in ('p','explore','accounts','reel','reels','sharer','share','about','tv','stories')]
    out['ig']=ig[0] if ig else ''
    fb=re.findall(r'facebook\.com/([A-Za-z0-9._\-]+)',allh)
    fb=[f for f in fb if f.lower() not in ('sharer','sharer.php','tr','plugins','dialog','share')]
    out['fb']=fb[0] if fb else ''
    return out
def ig_followers(handle):
    if not handle: return ''
    h=get(f'https://www.instagram.com/{handle}/',20)
    m=re.search(r'([\d.,KkMm]+)\s*Followers',html.unescape(h))
    return m.group(1) if m else ''
if __name__=='__main__':
    rows=json.load(open(sys.argv[1]))
    def go(r):
        e=enrich(r['web']); e['followers']=ig_followers(e['ig']); r.update(e); return r
    with cf.ThreadPoolExecutor(8) as ex: rows=list(ex.map(go,rows))
    json.dump(rows,open(sys.argv[2],'w'),ensure_ascii=False,indent=1)
