"""
Download SadTalker checkpoints with resume support
Run: python download_checkpoints.py
"""
import os
import urllib.request
import sys

checkpoints_dir = os.path.join(os.path.dirname(__file__), 'checkpoints')
os.makedirs(checkpoints_dir, exist_ok=True)

files = {
    'SadTalker_V0.0.2_256.safetensors': 'https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/SadTalker_V0.0.2_256.safetensors',
    'SadTalker_V0.0.2_512.safetensors': 'https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/SadTalker_V0.0.2_512.safetensors',
    'mapping_00109-model.pth.tar': 'https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/mapping_00109-model.pth.tar',
    'mapping_00229-model.pth.tar': 'https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/mapping_00229-model.pth.tar',
    'facevid2vid_00189-model.pth.tar': 'https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/facevid2vid_00189-model.pth.tar',
    'epoch_20.pth': 'https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/epoch_20.pth',
    'shape_predictor_68_face_landmarks.dat': 'https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/shape_predictor_68_face_landmarks.dat',
    'hub.zip': 'https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/hub.zip',
}

def download_with_resume(url, filepath):
    """Download with resume support"""
    headers = {}
    if os.path.exists(filepath):
        existing_size = os.path.getsize(filepath)
        headers['Range'] = f'bytes={existing_size}-'
        mode = 'ab'
    else:
        existing_size = 0
        mode = 'wb'
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            total = response.length + existing_size if response.length else None
            downloaded = existing_size
            
            with open(filepath, mode) as f:
                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        pct = downloaded / total * 100
                        print(f'\r  {downloaded/1024/1024:.1f}/{total/1024/1024:.1f} MB ({pct:.1f}%)', end='', flush=True)
                    else:
                        print(f'\r  {downloaded/1024/1024:.1f} MB', end='', flush=True)
        print()
        return True
    except Exception as e:
        print(f'\n  Error: {e}')
        return False

print("SadTalker Checkpoint Downloader")
print("=" * 50)

for filename, url in files.items():
    filepath = os.path.join(checkpoints_dir, filename)
    if os.path.exists(filepath):
        size_mb = os.path.getsize(filepath) / 1024 / 1024
        print(f"OK   {filename} ({size_mb:.1f} MB)")
        continue
    
    print(f"DL   {filename}")
    success = download_with_resume(url, filepath)
    if success:
        print(f"DONE {filename}")
    else:
        print(f"FAIL {filename} - run again to resume")

# Extract hub.zip
hub_zip = os.path.join(checkpoints_dir, 'hub.zip')
if os.path.exists(hub_zip):
    import zipfile
    hub_dir = os.path.join(checkpoints_dir, 'hub')
    os.makedirs(hub_dir, exist_ok=True)
    with zipfile.ZipFile(hub_zip, 'r') as z:
        z.extractall(hub_dir)
    print("Extracted hub.zip")

print("\nDone! Files in checkpoints:")
for f in sorted(os.listdir(checkpoints_dir)):
    fp = os.path.join(checkpoints_dir, f)
    if os.path.isfile(fp):
        print(f"  {f}: {os.path.getsize(fp)/1024/1024:.1f} MB")
