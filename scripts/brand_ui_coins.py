"""Assemble the generated MEGA BATTLE coin face into existing atlas regions."""
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.tools/python'))
from PIL import Image,ImageDraw,ImageChops

def main():
    plan=json.loads((ROOT/'art/ui-coin-regions.json').read_text(encoding='utf-8'))
    art=Image.open(ROOT/plan['art']).convert('RGBA')
    backup=ROOT/'output/ui_coin_branding'
    backup.mkdir(parents=True,exist_ok=True)
    checks=[]
    for key,atlas in plan['atlases'].items():
        path=ROOT/'textures'/atlas['file']
        original_path=backup/(key+'_before.png')
        if not original_path.exists(): original_path.write_bytes(path.read_bytes())
        before=Image.open(original_path).convert('RGBA');after=before.copy()
        allowed=Image.new('L',before.size)
        for sprite in atlas['sprites']:
            sx,sy,sw,sh=sprite['rect']
            for x0,y0,x1,y1 in sprite['face_boxes']:
                assert 0<=x0<x1<=sw and 0<=y0<y1<=sh
                w,h=x1-x0,y1-y0
                # Technical projection of one generated face onto the coin plane.
                face=art.resize((w,h),Image.Resampling.LANCZOS)
                mask=Image.new('L',(w*4,h*4))
                ImageDraw.Draw(mask).ellipse((0,0,w*4-1,h*4-1),fill=255)
                mask=mask.resize((w,h),Image.Resampling.LANCZOS)
                after.paste(face,(sx+x0,sy+y0),mask)
                ImageDraw.Draw(allowed).rectangle((sx+x0,sy+y0,sx+x1-1,sy+y1-1),fill=255)
        after.putalpha(before.getchannel('A'))
        assert before.size==after.size
        assert before.getchannel('A').tobytes()==after.getchannel('A').tobytes()
        difference=ImageChops.difference(before,after).convert('RGB')
        outside=difference.copy();outside.paste((0,0,0),(0,0),allowed)
        assert outside.getbbox() is None,'Unexpected changes outside coin faces'
        after.save(path)
        checks.append({'file':atlas['file'],'sprites_updated':len(atlas['sprites']),
                       'alpha_exact':True,'outside_faces_exact':True})
        print(atlas['file'],len(atlas['sprites']),'sprites; alpha/outside faces exact')
    (backup/'checks.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')

if __name__=='__main__':main()
