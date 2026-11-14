"""Export Zurich textures, then rebuild a playable copy from edited PNGs."""
import sys, json, shutil, argparse
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / '.tools/python'))
import UnityPy

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
    out=ROOT/('game-demo' if args.action=='demo' else 'game-local'); out.mkdir(exist_ok=True)
    data=env.file.save()
    check=UnityPy.load(data)
    assert len(list(check.objects))==len(list(env.objects))
    for obj in check.objects:
        if obj.type.name=='Texture2D' and obj.peek_name() in changed:
            assert obj.read().image.convert('RGBA').tobytes()==expected[obj.peek_name()], 'Texture differs after repack (RGBA)'
    (out/'ZurichNewPrivacy.data.unityweb').write_bytes(data)
    (out/'ZurichNewPrivacy.wasm.code.unityweb').write_bytes(source('ZurichNewPrivacy.wasm.code.unityweb'))
    for name in ['ZurichNewPrivacy.json','ZurichNewPrivacy.wasm.framework.unityweb','4399.z.js','master-loader.js','unity.js','UnityLoader.2019.2.js','poki-sdk.js','poki-sdk-core-v2.234.2.js']:
        shutil.copy2(ROOT/'subway-original'/name,out/name)
    html=(ROOT/'launcher-template.html').read_text(encoding='utf-8')
    (out/'index.html').write_text(html,encoding='utf-8')
    print('Built',out.name,'changed:',changed,'objects:',len(list(check.objects)))

if __name__=='__main__': main()
