from pathlib import Path
import sys,difflib
s=Path(sys.argv[1]);out=Path(sys.argv[2]);p=s/'core/libretro/libretro.cpp';old=p.read_text();new=old
for mode in ('BIND','UNBIND'):
 needle='      if (settings.pvr.rend == 0 || settings.pvr.rend == 3)\n         glsm_ctl(GLSM_CTL_STATE_'+mode+', NULL);'
 if '#if defined(HAVE_OPENGL) || defined(HAVE_OPENGLES)\n'+needle not in new:
  assert new.count(needle)==1,(mode,'unexpected source')
  new=new.replace(needle,'#if defined(HAVE_OPENGL) || defined(HAVE_OPENGLES)\n'+needle+'\n#endif')
if new!=old:
 (out/'vulkan-only.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/core/libretro/libretro.cpp',tofile='b/core/libretro/libretro.cpp')))
 p.write_text(new)
if s.name=='xtreme':
 p=s/'core/rend/gles/postprocess.cpp';old=p.read_text();new=old
 needle='\tglBindFramebuffer(GL_FRAMEBUFFER, framebuffer);\n}\n\nvoid PostProcessor::Render(GLuint output_fbo)\n{'
 if needle in new:
  new=new.replace(needle,'\tglBindFramebuffer(GL_FRAMEBUFFER, framebuffer);*/\n}\n\nvoid PostProcessor::Render(GLuint output_fbo)\n{/*')
  p.write_text(new)
  (out/'disabled-postprocessor-comment-fix.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/core/rend/gles/postprocess.cpp',tofile='b/core/rend/gles/postprocess.cpp')))
