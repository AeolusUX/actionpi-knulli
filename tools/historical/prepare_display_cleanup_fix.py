from pathlib import Path
import difflib, hashlib, json

root=Path(__file__).resolve().parents[1]
src=Path('/opt/actionpi-candidate-5b956b75/source/bsp/drivers/drm')
out=root/'outputs/mali-rebuild-prep/display-cleanup-fix'
dest=out/'source/bsp/drivers/drm'; dest.mkdir(parents=True,exist_ok=True)
name='sunxi_fbdev_core.c'; original=(src/name).read_text(); s=original
old='\tunsigned int w, h;\n\n\tsunxi_drm_get_logo_info(drm, &logo, &w, &h);'
new='''\tunsigned int w, h;
\tint ret;

\tret = sunxi_drm_get_logo_info(drm, &logo, &w, &h);
\tif (ret)
\t\treturn ret;
\tif (!w || !h || !logo.width || !logo.height)
\t\treturn -EINVAL;'''
assert s.count(old)==1;s=s.replace(old,new)
old='int sunxi_fbdev_exit(void)\n{\n\tfb_core_exit(&create_info);'
new='int sunxi_fbdev_exit(void)\n{\n\tif (!__fb_info)\n\t\treturn 0;\n\tfb_core_exit(&create_info);'
assert s.count(old)==1;s=s.replace(old,new)
a=s.index('int fb_core_init(struct fb_create_info *create, struct display_channel_state *out_state)\n{')
b=s.index('int fb_core_exit(struct fb_create_info *create)\n{',a)
part=s[a:b]
part=part.replace('\tint ret;','\tint ret;\n\tbool client_registered = false;',1)
needle='\tret = platform_fb_memory_alloc('
assert part.count(needle)==1
part=part.replace(needle,'\tclient_registered = true;\n\tret = platform_fb_memory_alloc(',1)
part=part.replace('\t\tgoto exit_fb;','\t\tgoto free_fb;')
old='exit_fb:\n\tplatform_fb_exit(create, info->par);\nfree_fb:\n\tframebuffer_release(info);'
new='free_fb:\n\t/* Unlink/release the embedded client before freeing its allocation. */\n\tif (client_registered)\n\t\tplatform_fb_exit(create, info->par);\n\tframebuffer_release(info);'
assert old in part;part=part.replace(old,new)
s=s[:a]+part+s[b:]
old='\tframebuffer_release(__fb_info);\n\treturn 0;'
assert s.count(old)==1;s=s.replace(old,'\tframebuffer_release(__fb_info);\n\t__fb_info = NULL;\n\treturn 0;',1)
(dest/name).write_text(s)
platform=(src/'sunxi_fbdev_platform.c').read_text()
assert 'drm_client_unregister(create->drm, &info->client);' in platform
assert '\t\tlist_del(&client->list);' in platform
(dest/'sunxi_fbdev_platform.c').write_text(platform)
patch=''.join(difflib.unified_diff(original.splitlines(True),s.splitlines(True),fromfile='a/bsp/drivers/drm/'+name,tofile='b/bsp/drivers/drm/'+name))
(out/'0001-fbdev-propagate-logo-error-and-unwind-client.patch').write_text(patch)
(out/'source-manifest.json').write_text(json.dumps({'candidate_commit':'5b956b750422abd5e9e9c5523540d2aaf41a7939','files':{n:{'baseline_sha256':hashlib.sha256((src/n).read_bytes()).hexdigest(),'prepared_sha256':hashlib.sha256((dest/n).read_bytes()).hexdigest()} for n in [name,'sunxi_fbdev_platform.c']},'platform_cleanup':'Unmodified source; nonempty unregister implementation is REQUIRED with core change. Actual vendor binary has empty helpers.'},indent=2))
print('Prepared isolated source pair, patch and manifest; original source untouched.')
