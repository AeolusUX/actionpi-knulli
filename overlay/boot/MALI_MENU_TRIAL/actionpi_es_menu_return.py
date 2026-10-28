"""Open the saved ES system's game list after a supervised game only.

Restore the user's startup preference after ES closes, or on the next boot
after an interrupted session. Other ES settings and LastSystem are untouched.
"""
from pathlib import Path
import json,os,re,sys,xml.etree.ElementTree as ET

SETTINGS=Path('/userdata/system/configs/emulationstation/es_settings.cfg')
JOURNAL=Path('/boot/MALI_MENU_TRIAL/es-menu-return-state.json')
PATTERN=re.compile(r'''<bool\b(?=[^>]*\bname\s*=\s*['"]StartupOnGameList['"])[^>]*/>''')
OVERRIDE='<bool name="StartupOnGameList" value="true" />'

def atomic(path,text):
 tmp=path.with_name(path.name+'.menu-return-tmp')
 with tmp.open('w',encoding='utf8',newline='\n') as f:
  f.write(text);f.flush();os.fsync(f.fileno())
 tmp.replace(path)

def inspect(text):
 root=ET.fromstring(text);assert root.tag=='config'
 nodes=[n for n in root.findall('bool') if n.get('name')=='StartupOnGameList'];assert len(nodes)<=1
 matches=list(PATTERN.finditer(text));assert len(matches)==len(nodes)
 return matches[0].group() if matches else None

def restore():
 try:
  if not JOURNAL.exists():return
  record=json.loads(JOURNAL.read_text());assert record['version']==1
  original=record['original'];assert original is None or (len(original)<2048 and PATTERN.fullmatch(original))
  text=SETTINGS.read_text();current=inspect(text)
  # Respect an explicit user change away from the temporary true value.
  if current is not None and ET.fromstring(current).get('value','').lower() in ('true','1','yes'):
   restored=PATTERN.sub(lambda _:original or '',text,count=1)
   if restored!=text:atomic(SETTINGS,restored)
  JOURNAL.unlink()
 except Exception as exc:print('ACTIONPI_ES_RETURN restore:',type(exc).__name__,file=sys.stderr)

def prepare():
 try:
  restore()
  if JOURNAL.exists():return
  text=SETTINGS.read_text();original=inspect(text)
  if original is not None and ET.fromstring(original).get('value','').lower() in ('true','1','yes'):return
  updated=PATTERN.sub(OVERRIDE,text,count=1) if original is not None else text.replace('</config>','\t'+OVERRIDE+'\n</config>',1)
  assert updated!=text;inspect(updated)
  atomic(JOURNAL,json.dumps({'version':1,'original':original})+'\n')
  atomic(SETTINGS,updated)
 except Exception as exc:print('ACTIONPI_ES_RETURN prepare:',type(exc).__name__,file=sys.stderr)
