"""Export Zurich textures, then rebuild a playable copy from edited PNGs."""
import sys, json, shutil, argparse, gc
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / '.tools/python'))
import UnityPy

def patch_coin_uv(env, config):
    """Unfold the coin's mirrored face UVs for a readable branded inscription."""
    from UnityPy.helpers.MeshHelper import MeshHandler
    import copy
    left, top, right, bottom = config['rect']
    width, height = config['atlas_size']
    patched=[]
    for obj in env.objects:
        if obj.type.name!='Mesh' or obj.assets_file.name!='resources.assets' or obj.peek_name()!='currency_coin':
            continue
        mesh=obj.read()
        handler=MeshHandler(mesh); handler.process()
        assert len(handler.m_UV0)==85 and mesh.m_CompressedMesh.m_UVInfo==5
        geometry=copy.deepcopy(mesh.m_CompressedMesh.m_Vertices)
        uv=[list(pair) for pair in handler.m_UV0]
        # Corrected against in-game observation: the previous signs made both
        # outward-visible faces mirrored. Do not compensate by mirroring the PNG.
        face_signs=config.get('face_u_signs',[1,-1])
        assert len(face_signs)==2 and set(face_signs)=={-1,1}
        for indices, sign in zip((range(40,61),range(61,82)),face_signs):
            xs=[handler.m_Vertices[i][0] for i in indices]
            ys=[handler.m_Vertices[i][1] for i in indices]
            for i in indices:
                x,y,_=handler.m_Vertices[i]
                nx=(x-min(xs))/(max(xs)-min(xs))
                ny=(y-min(ys))/(max(ys)-min(ys))
                if sign<0: nx=1-nx
                uv[i]=[(left+0.5+nx*(right-left-1))/width,
                       1-(top+0.5+(1-ny)*(bottom-top-1))/height]
        # 30 bits preserves the original 10-bit fractions exactly (1023 divides
        # 2**30-1), including untouched sidewall and dummy-submesh UVs.
        packed=mesh.m_CompressedMesh.m_UV
        assert packed.m_Start==0 and packed.m_Range==1 and packed.m_NumItems==170
        bits=30; value=0
        for i,v in enumerate(c for pair in uv for c in pair):
            value |= round(v*((1<<bits)-1)) << (i*bits)
        packed.m_Data=list(value.to_bytes((170*bits+7)//8,'little'))
        packed.m_BitSize=bits
        assert mesh.m_CompressedMesh.m_Vertices==geometry
        mesh.save(); patched.append((obj.assets_file.name,obj.path_id))
    assert len(patched)==1, 'Expected exactly one currency_coin mesh'
    return patched

def source(name):
    base = ROOT/'subway-original'
    whole = base/'zurich'/name
    if whole.exists(): return whole.read_bytes()
    return (base/(name+'.part1')).read_bytes() + (base/(name+'.part2')).read_bytes()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('action',choices=['export','build','demo'])
    args=parser.parse_args()
    env=UnityPy.load(source('ZurichNewPrivacy.data.unityweb'))
    folder=ROOT/'textures'; folder.mkdir(exist_ok=True)
    entries=[]; changed=[]; expected={}
    for obj in env.objects:
        if obj.type.name!='Texture2D' or obj.assets_file.name=='unity_default_resources': continue
        tex=obj.read()
        if not tex.m_Width or not tex.m_Height: continue
        name=f'{obj.assets_file.name}_{obj.path_id}_{tex.m_Name}'.replace('/','_')+'.png'
        path=folder/name
        entries.append({'file':name,'name':tex.m_Name,'width':tex.m_Width,'height':tex.m_Height})
        if args.action=='export': tex.image.save(path)
        elif args.action=='demo' and tex.m_Name=='1.101.0_Zurich_trains':
            from PIL import ImageOps
            image=tex.image.convert('RGBA')
            tinted=ImageOps.colorize(ImageOps.grayscale(image),'#250025','#ff22dd').convert('RGBA')
            tinted.putalpha(image.getchannel('A'))
            tex.image=tinted; tex.save(); changed.append(tex.m_Name)
            expected[tex.m_Name]=tinted.convert('RGBA').tobytes()
        elif args.action=='build' and path.exists():
            from PIL import Image
            image=Image.open(path).convert('RGBA')
            original=tex.image.convert('RGBA')
            if image.size!=original.size: raise ValueError(f'Keep original dimensions: {name}')
            if image.tobytes()!=original.tobytes():
                tex.set_image(image, target_format=4, mipmap_count=max(1,tex.m_MipCount or 1))
                tex.save(); changed.append(tex.m_Name)
                expected[tex.m_Name]=image.convert('RGBA').tobytes()
    (folder/'catalog.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2),encoding='utf-8')
    if args.action=='export': print('Exported',len(entries),'textures'); return
    coin_config=folder/'coin-branding.json'
    patched_meshes=[]
    if args.action=='build' and coin_config.exists():
        patched_meshes=patch_coin_uv(env,json.loads(coin_config.read_text(encoding='utf-8')))
    out=ROOT/('game-demo' if args.action=='demo' else 'game-local'); out.mkdir(exist_ok=True)
    data=env.file.save()
    object_count=len(list(env.objects))
    # UnityPy retains cyclic references. Release the source object graph before
    # loading the rebuilt package for verification (important on small servers).
    obj=None
    tex=None
    env=None
    gc.collect()
    check=UnityPy.load(data)
    assert len(list(check.objects))==object_count
    for obj in check.objects:
        if obj.type.name=='Texture2D' and obj.peek_name() in changed:
            assert obj.read().image.convert('RGBA').tobytes()==expected[obj.peek_name()], 'Texture differs after repack (RGBA)'
    if patched_meshes:
        from UnityPy.helpers.MeshHelper import MeshHandler
        for obj in check.objects:
            if (obj.assets_file.name,obj.path_id) in patched_meshes:
                h=MeshHandler(obj.read()); h.process()
                assert len(h.m_UV0)==85 and h.m_UV0[45][0]!=h.m_UV0[56][0], 'Coin face still mirrored'
    (out/'ZurichNewPrivacy.data.unityweb').write_bytes(data)
    (out/'ZurichNewPrivacy.wasm.code.unityweb').write_bytes(source('ZurichNewPrivacy.wasm.code.unityweb'))
    for name in ['ZurichNewPrivacy.json','ZurichNewPrivacy.wasm.framework.unityweb','4399.z.js','master-loader.js','unity.js','UnityLoader.2019.2.js','poki-sdk.js','poki-sdk-core-v2.234.2.js']:
        shutil.copy2(ROOT/'subway-original'/name,out/name)
    html=(ROOT/'launcher-template.html').read_text(encoding='utf-8')
    shutil.copy2(ROOT/'game-input.js',out/'game-input.js')
    shutil.copy2(ROOT/'gamepad-input.js',out/'gamepad-input.js')
    (out/'index.html').write_text(html,encoding='utf-8')
    print('Built',out.name,'changed:',changed,'objects:',len(list(check.objects)))
    if patched_meshes: print('Coin face UV mapping updated:',patched_meshes)

if __name__=='__main__': main()
