"""Read-only audit of source/built objects and all exported PNGs."""
import hashlib
import json
import subprocess
import sys
from collections import Counter
from io import BytesIO
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / '.tools/python'))
from PIL import Image
import UnityPy
from texture_tool import source
from UnityPy.streams import EndianBinaryReader

def digest(data):
    return hashlib.sha256(data).hexdigest()

def key(obj):
    return (obj.assets_file.name, obj.path_id, obj.type.name)

def binary_payloads(container, prefix=''):
    result = {}
    for name, item in getattr(container, 'files', {}).items():
        path = prefix + str(name)
        if isinstance(item, EndianBinaryReader):
            result[path] = digest(item.bytes)
        elif type(item).__name__ in {'WebFile', 'BundleFile'}:
            result.update(binary_payloads(item, path + '/'))
    return result

def main():
    catalog = json.loads((ROOT / 'textures/catalog.json').read_text(encoding='utf-8'))
    records = []
    for entry in catalog:
        name = entry['file']
        baseline = subprocess.run(['git', 'show', 'a9cdde1:textures/' + name], cwd=ROOT, capture_output=True, check=True).stdout
        current_bytes = (ROOT / 'textures' / name).read_bytes()
        before = Image.open(BytesIO(baseline)).convert('RGBA')
        after = Image.open(BytesIO(current_bytes)).convert('RGBA')
        records.append({'file': name, 'changed': before.tobytes() != after.tobytes(), 'size_before': before.size, 'size_after': after.size, 'size_ok': before.size == after.size, 'alpha_ok': before.getchannel('A').tobytes() == after.getchannel('A').tobytes(), 'source_sha256': digest(baseline), 'current_sha256': digest(current_bytes)})
    source_data = source('ZurichNewPrivacy.data.unityweb')
    built_data = (ROOT / 'game-local/ZurichNewPrivacy.data.unityweb').read_bytes()
    old = UnityPy.load(source_data)
    new = UnityPy.load(built_data)
    old_objects = {key(obj): obj for obj in old.objects}
    new_objects = {key(obj): obj for obj in new.objects}
    old_payloads = binary_payloads(old.file)
    new_payloads = binary_payloads(new.file)
    missing = sorted(set(old_objects) - set(new_objects))
    added = sorted(set(new_objects) - set(old_objects))
    changed_nontexture = []
    nontexture_count = 0
    texture_metadata_changes = 0
    png_matches = {}
    for obj_key in sorted(set(old_objects) & set(new_objects)):
        a, b = old_objects[obj_key], new_objects[obj_key]
        same_raw = a.get_raw_data() == b.get_raw_data()
        if obj_key[2] != 'Texture2D':
            nontexture_count += 1
            if not same_raw:
                changed_nontexture.append(obj_key)
        else:
            texture_metadata_changes += not same_raw
            tex = b.read()
            filename = f'{b.assets_file.name}_{b.path_id}_{tex.m_Name}'.replace('/', '_') + '.png'
            if filename in {e['file'] for e in catalog}:
                expected = Image.open(ROOT / 'textures' / filename).convert('RGBA')
                png_matches[filename] = tex.image.convert('RGBA').tobytes() == expected.tobytes()
    result = {'baseline_commit': 'a9cdde1', 'source_package_sha256': digest(source_data), 'built_package_sha256': digest(built_data), 'source_object_count': len(old_objects), 'built_object_count': len(new_objects), 'source_types': dict(Counter(k[2] for k in old_objects)), 'built_types': dict(Counter(k[2] for k in new_objects)), 'missing_objects': missing, 'added_objects': added, 'nontexture_objects_compared': nontexture_count, 'changed_nontexture_objects': changed_nontexture, 'texture_metadata_changes': texture_metadata_changes, 'embedded_png_matches': png_matches, 'png_files': records}
    result['source_binary_payloads'] = old_payloads
    result['built_binary_payloads'] = new_payloads
    result['binary_payload_differences'] = [name for name in sorted(set(old_payloads) | set(new_payloads)) if old_payloads.get(name) != new_payloads.get(name)]
    (ROOT / 'agent-reports').mkdir(exist_ok=True)
    (ROOT / 'agent-reports/QA_TECHNICAL.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Binary payloads:', len(old_payloads), 'differences:', result['binary_payload_differences'])
    print(json.dumps({'png': len(records), 'changed_png': sum(r['changed'] for r in records), 'size_errors': sum(not r['size_ok'] for r in records), 'alpha_errors': sum(not r['alpha_ok'] for r in records), 'source_objects': len(old_objects), 'built_objects': len(new_objects), 'missing_objects': len(missing), 'added_objects': len(added), 'nontexture_compared': nontexture_count, 'nontexture_changed': len(changed_nontexture), 'embedded_checked': len(png_matches), 'embedded_mismatches': sum(not x for x in png_matches.values())}, ensure_ascii=False))

if __name__ == '__main__':
    main()
