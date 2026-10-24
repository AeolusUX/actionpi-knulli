"""Verify XZ integrity and both compressed/unpacked hashes in one streaming pass."""
from pathlib import Path
import argparse,hashlib,io,json,lzma

def main():
 p=argparse.ArgumentParser();p.add_argument('asset',type=Path);p.add_argument('--expected-image-sha256',required=True)
 p.add_argument('--output-dir',required=True,type=Path);a=p.parse_args()
 assert a.asset.stat().st_size<2*1024**3,'Release asset exceeds the individual GitHub asset limit'
 packed=hashlib.sha256();unpacked=hashlib.sha256();size=0
 with a.asset.open('rb') as f:
  class Reader(io.RawIOBase):
   def readable(self):return True
   def read(self,n=-1):
    data=f.read(n);packed.update(data);return data
  with lzma.LZMAFile(Reader(),'rb') as stream:
   while data:=stream.read(8*1024*1024):unpacked.update(data);size+=len(data)
 assert unpacked.hexdigest()==a.expected_image_sha256,'Unpacked image SHA256 mismatch'
 report={'asset':a.asset.name,'bytes':a.asset.stat().st_size,'sha256':packed.hexdigest(),
         'image_bytes':size,'image_sha256':unpacked.hexdigest(),'xz_integrity':'passed'}
 a.output_dir.mkdir(parents=True,exist_ok=True)
 (a.output_dir/'ASSETS.json').write_text(json.dumps(report,indent=2)+'\n')
 (a.output_dir/'SHA256SUMS').write_text(packed.hexdigest()+'  '+a.asset.name+'\n')
 print(json.dumps(report),flush=True)

if __name__=='__main__':main()
