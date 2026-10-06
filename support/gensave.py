# run in /src/quake2/quake2: python3 ../support/gensave.py
import re,glob
src={f:open(f).read() for f in sorted(glob.glob('*.ag')) if f!='Save.ag'}
game=src['Game.ag']
classes={}; cur=None
for ln in game.split('\n'):
    m=re.match(r'^class (\w+)',ln)
    if m: cur=m.group(1); classes[cur]=[]; continue
    if ln and not ln[0].isspace() and not ln.startswith('#'): cur=None
    m=re.match(r'^    public\s+(\w+)\s*:\s*(.+?)\s*$',ln)
    if cur and m:
        t=m.group(2)
        if not t.startswith('lambda'): t=re.sub(r'\s*\[.*$','',t)
        classes[cur].append((m.group(1),re.sub(r'\s+',' ',t)))
want=['MoveInfo','PlayerState','ClientPersistant','ClientRespawn','Client','MonsterInfo','Edict','Level']
def norm(ret,args): return (ret.strip() or 'none',tuple(a.strip() for a in args))
sigs={}
for f,s in src.items():
    for m in re.finditer(r'^func (\w+) \[(.*?)\](?:\s*->\s*([\w ]+?))?\s*$',s,re.S|re.M):
        args=[a.split(':',1)[1] for a in m.group(2).split(',') if ':' in a]
        sigs[m.group(1)]=norm(m.group(3) or 'none',args)
used=set()
for s in src.values(): used|=set(re.findall(r'lambda (\w+)\[\]',s))
moves=[]
for s in src.values(): moves+=re.findall(r'^(\w+) : MMove\s*$',s,re.M)
lam={}
def lam_id(t):
    m=re.match(r'lambda (\w+) \[(.*)\]',t)
    key=norm(m.group(1),m.group(2).split(','))
    if key not in lam: lam[key]=(len(lam),t)
    return lam[key][0]
out=[]; W=out.append
def member(o,name,t):
    a=f'{o}.{name}'
    if t=='i32': return [f's.put_i[ {a} ]'],[f'{a} = s.get_i[]']
    if t=='bool': return [f's.put_i[ ({a}) ? 1 : 0 ]'],[f'{a} = s.get_i[] != 0']
    if t=='f32': return [f's.put_f[ {a} ]'],[f'{a} = s.get_f[]']
    if t=='vec3f': return [f's.put_v[ {a} ]'],[f'{a} = s.get_v[]']
    if t=='vec4f': return [f's.put_q[ {a} ]'],[f'{a} = s.get_q[]']
    if t=='string': return [f's.put_s[ {a} ]'],[f'{a} = s.get_s[]']
    if t=='vec i32': return [f's.put_ints[ {a} ]'],[f'{a} = s.get_ints[]']
    if t=='Edict': return [f's.put_i[ ({a}) ? {a}.number : 0 - 1 ]'],[f'{a} = save_edict[ s.get_i[] ]']
    if t=='GItem': return [f's.put_i[ save_item_no[ {a} ] ]'],[f'{a} = save_item[ s.get_i[] ]']
    if t=='MMove': return [f's.put_s[ save_move_name[ {a} ] ]'],[f'{a} = save_move[ s.get_s[] ]']
    if t.startswith('lambda'):
        k=lam_id(t); return [f's.put_s[ lam_name_{k}[ {a} ] ]'],[f'{a} = lam_find_{k}[ s.get_s[] ]']
    if t in want:
        return ([f's.put_i[ ({a}) ? 1 : 0 ]',f'if [ {a} ] save_{t}[ s, {a} ]'],
                [f'if [ s.get_i[] != 0 ]',f'    if [ !{a} ] {a} = {t} [ ]',f'    load_{t}[ s, {a} ]','el',f'    {a} = null'])
    print('SKIPPED',o,name,t); return [],[]
body=[]
for c in want:
    sv=[f'func save_{c} [ s: SaveOut, o: {c} ]']; ld=[f'func load_{c} [ s: SaveIn, o: {c} ]']
    for name,t in classes[c]:
        a,b=member('o',name,t); sv+=['    '+x for x in a]; ld+=['    '+x for x in b]
    body+=sv+['']+ld+['']
W(open('../support/save_head.ag').read())
for key,(k,t) in sorted(lam.items(),key=lambda x:x[1][0]):
    names=sorted(n for n in used if sigs.get(n)==key)
    W(f'# {len(names)} functions of one shape, by name')
    W(f'func lam_name_{k} [ f: {t} ] -> string'); W('    if [ !f ] return null')
    for n in names: W(f"    if [ f == lambda {n}[] ] return '{n}'")
    W('    return null'); W('')
    W(f'func lam_find_{k} [ n: string ] -> {t}'); W('    if [ !n ] return null')
    for n in names: W(f"    if [ n == '{n}' ] return lambda {n}[]")
    W('    return null'); W('')
W('func save_move_name [ m: MMove ] -> string'); W('    if [ !m ] return null')
for n in moves: W(f"    if [ m == {n} ] return '{n}'")
W('    return null'); W(''); W('func save_move [ n: string ] -> MMove'); W('    if [ !n ] return null')
for n in moves: W(f"    if [ n == '{n}' ] return {n}")
W('    return null'); W('')
out+=body
open('Save.ag','w').write('\n'.join(out))
print('lambda shapes',len(lam),'moves',len(moves),'lines',sum(x.count('\n')+1 for x in out))
