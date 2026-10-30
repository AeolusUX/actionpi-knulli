"""WSL-only isolated Linux/GLES build adaptation of official 1.20.51."""
from pathlib import Path
import difflib,json,re,shutil,subprocess,tarfile
ROOT=Path('/mnt/c/Users/2nd/Documents/Codex/2026-09-16/actionpi-vulkan-continuation')
OUT=ROOT/'outputs/saturn-1.20.51-prep';TRIAL=Path('/root/actionpi-saturn-1.20.51-trial')
SRC=TRIAL/'source';YAB=SRC/'yabause';SDK=TRIAL/'sdk';BUILD=TRIAL/'build';DL=OUT/'downloads'
if not SDK.exists():shutil.copytree(ROOT/'outputs/ppsspp-1.20.4-prep/target-sdk',SDK)
for deb in DL.glob('*.deb'):subprocess.run(['dpkg-deb','-x',str(deb),str(SDK)],check=True)
for file in (OUT/'runtime-libs').iterdir():shutil.copy2(file,SDK/'usr/lib'/file.name)
for name,real in [('libssl.so','libssl.so.3'),('libcrypto.so','libcrypto.so.3'),('libsqlite3.so','libsqlite3.so.0')]:
    p=SDK/'usr/lib'/name
    if not p.exists():p.symlink_to(real)
(SDK/'usr/include/GLES3').mkdir(exist_ok=True)
for n in ['gl3.h','gl31.h','gl32.h','gl3platform.h']:shutil.copy2(DL/n,SDK/'usr/include/GLES3'/n)
(SDK/'usr/include/GLES3/gl3ext.h').write_text('#pragma once\n#include <GLES2/gl2ext.h>\n')
CHD=TRIAL/'libchdr'
if not CHD.exists():
    temp=TRIAL/'chd-unpack';temp.mkdir(exist_ok=True)
    with tarfile.open(DL/'libchdr-5a642352.tar.gz') as tf:tf.extractall(temp,filter='data')
    next(temp.iterdir()).rename(CHD)
CHDBUILD=TRIAL/'libchdr-build'
eigen=YAB/'src/retro_arena/nanogui-sdl/ext/eigen'
if not (eigen/'Eigen').exists():
    eigen.mkdir(parents=True,exist_ok=True)
    for n in ['Eigen','unsupported']:shutil.copytree(SDK/'usr/include/eigen3'/n,eigen/n,dirs_exist_ok=True)

before=OUT/'before';before.mkdir(exist_ok=True);patches=[]
def patch(rel,change):
    p=SRC/rel;b=before/rel;b.parent.mkdir(parents=True,exist_ok=True)
    if not b.exists():shutil.copy2(p,b)
    old=b.read_text();new=change(old)
    if p.read_text()!=new:p.write_text(new)
    patches.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))

prefix='/opt/actionpi-toolchain/arm-gnu-toolchain-13.3.rel1-x86_64-aarch64-none-linux-gnu/bin/aarch64-none-linux-gnu-'
toolchain=OUT/'aarch64-actionpi.cmake'
toolchain.write_text(f'''set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR aarch64)
set(CMAKE_C_COMPILER {prefix}gcc)
set(CMAKE_CXX_COMPILER {prefix}g++)
set(CMAKE_ASM_COMPILER {prefix}gcc)
set(CMAKE_FIND_ROOT_PATH {SDK} /opt/actionpi-toolchain/arm-gnu-toolchain-13.3.rel1-x86_64-aarch64-none-linux-gnu/aarch64-none-linux-gnu/libc)
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)
set(CMAKE_C_FLAGS_INIT "-march=armv8-a -mtune=cortex-a55 -I{SDK}/usr/include -I{SDK}/usr/include/aarch64-linux-gnu -DEGL_NO_X11=1 -D_GNU_SOURCE -fno-strict-aliasing -Wno-implicit-function-declaration -Wno-incompatible-pointer-types -Wno-int-conversion")
set(CMAKE_CXX_FLAGS_INIT "-march=armv8-a -mtune=cortex-a55 -I{SDK}/usr/include -I{SDK}/usr/include/aarch64-linux-gnu -DEGL_NO_X11=1 -D_GNU_SOURCE -fno-strict-aliasing")
set(CMAKE_EXE_LINKER_FLAGS_INIT "-L{SDK}/usr/lib -Wl,-rpath-link,{SDK}/usr/lib -Wl,--allow-multiple-definition")
''')
cmake='/root/.cache/actionpi-nodosumi-buildtools/cmake/data/bin/cmake'
# Build exactly the official recipe's CHD dependency, with cross flags propagated.
args=[cmake,'-S',str(CHD),'-B',str(CHDBUILD),'-DCMAKE_TOOLCHAIN_FILE='+str(toolchain),'-DCMAKE_BUILD_TYPE=Release','-DBUILD_SHARED_LIBS=OFF','-DBUILD_CHDR_TESTS=OFF']
with (OUT/'chdr-configure.log').open('w') as log:subprocess.run(args,stdout=log,stderr=subprocess.STDOUT,check=True)
with (OUT/'chdr-build.log').open('w') as log:subprocess.run([cmake,'--build',str(CHDBUILD),'-j2'],stdout=log,stderr=subprocess.STDOUT,check=True)
print('CHDR_BUILT',flush=True)

deps=YAB/'CMake/Packages/actionpi_dependencies.cmake'
deps.write_text(f'''include_directories({CHD}/include/libchdr {CHD}/include)
set(LIBCHDR_INCLUDE_DIR {CHD}/include/libchdr {CHD}/include)
set(LIBCHDR_LIB_DIR {CHDBUILD})
set(LIBCHDR_LIBRARIES {CHDBUILD}/libchdr-static.a {CHDBUILD}/deps/lzma-24.05/liblzma.a {CHDBUILD}/deps/zstd-1.5.6/build/cmake/lib/libzstd.a)
add_custom_target(libchdr)
set(zlib_INCLUDE_DIR {SDK}/usr/include)
set(zlib_STATIC_LIBRARIES {SDK}/usr/lib/libz.so)
''')
patch('yabause/src/CMakeLists.txt',lambda t:t.replace('project(yabause)',f'project(yabause)\ninclude_directories({SDK}/usr/include {SDK}/usr/include/aarch64-linux-gnu)').replace('include( ${CMAKE_SOURCE_DIR}/CMake/Packages/external_libchdr.cmake )','include( ${CMAKE_SOURCE_DIR}/CMake/Packages/actionpi_dependencies.cmake )').replace('include( ${CMAKE_SOURCE_DIR}/CMake/Packages/external_zlib.cmake )','# Matching staged system zlib.'))

# Cross-build generators run on the build PC, not the ARM64 target.
native=TRIAL/'host-tools';native.mkdir(exist_ok=True)
subprocess.run(['cc','-O2',str(YAB/'src/retro_arena/nanogui-sdl/resources/bin2c.c'),'-o',str(native/'bin2c')],check=True)
musashi=YAB/'src/musashi'
if not (musashi/'m68kopac.c').exists():
    subprocess.run(['cc','-O2',str(musashi/'m68kmake.c'),'-o',str(native/'m68kmake')],check=True)
    subprocess.run([str(native/'m68kmake'),str(musashi)],cwd=musashi,check=True,stdout=subprocess.DEVNULL)

shutil.copy2(DL/'json.hpp',YAB/'src/retro_arena/json.hpp')
(YAB/'src/retro_arena/nlohmann').mkdir(exist_ok=True)
shutil.copy2(DL/'json.hpp',YAB/'src/retro_arena/nlohmann/json.hpp')
port='''project(yabause-retro-arena)
yab_port_start()
find_package(SDL2 REQUIRED)
find_package(OpenSSL REQUIRED)
find_package(PNG REQUIRED)
add_subdirectory(pugixml)
add_subdirectory(nanogui-sdl)
include_directories(${SDL2_INCLUDE_DIR} ${PNG_INCLUDE_DIRS} ${OPENSSL_INCLUDE_DIR} ${CMAKE_CURRENT_BINARY_DIR} ${CMAKE_CURRENT_SOURCE_DIR} ${CMAKE_CURRENT_SOURCE_DIR}/include nanogui-sdl/include nanogui-sdl/ext/eigen)
add_executable(yabause-retro-arena main.cpp InputManager.cpp InputConfig.cpp MenuScreen.cpp Preference.cpp EventManager.cpp GameInfo.cpp GameListPanel.cpp actionpi_ra_disabled.c ../about.c)
target_link_libraries(yabause-retro-arena yabause pugixml ${YABAUSE_LIBRARIES} ${SDL2_LIBRARY} ${PNG_LIBRARIES} ${LIBCHDR_LIBRARIES} nanogui OpenSSL::SSL OpenSSL::Crypto sqlite3 stdc++fs dl)
yab_port_success(yabause-retro-arena)
set_target_properties(yabause-retro-arena PROPERTIES OUTPUT_NAME yabasanshiro-1.20.51)
'''
port=port.replace('sqlite3 stdc++fs dl)',f'sqlite3 stdc++fs dl {SDK}/usr/lib/libmali.so.0)')
patch('yabause/src/retro_arena/CMakeLists.txt',lambda t:port)
patch('yabause/src/retro_arena/nanogui-sdl/CMakeLists.txt',lambda t:t.replace('set(CMAKE_CXX_FLAGS "-std=c++11")','set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")').replace('add_definitions(-DNANOVG_VULKAN_IMPLEMENTATION)','add_definitions(-DNANOVG_GLES3_IMPLEMENTATION)').replace('add_executable(bin2c resources/bin2c.c)',f'add_executable(bin2c IMPORTED GLOBAL)\nset_target_properties(bin2c PROPERTIES IMPORTED_LOCATION {native}/bin2c)'))
def screen_header(t):
    t=t.replace('#include <vulkan/vulkan.h>','#if defined(NANOVG_VULKAN_IMPLEMENTATION)\n#include <vulkan/vulkan.h>\n#endif')
    return re.sub(r'(    virtual void drawAll\(\s*VkDevice.*?VkCommandBuffer commandBuffer\);)',r'#if defined(NANOVG_VULKAN_IMPLEMENTATION)\n\1\n#endif',t,flags=re.S)
patch('yabause/src/retro_arena/nanogui-sdl/include/nanogui/screen.h',screen_header)
def screen_source(t):
    start=t.index('static NVGcontext* vg');end=t.index('#if !defined(NANOVG_VULKAN_IMPLEMENTATION)',start)
    t=t[:start]+'#if defined(NANOVG_VULKAN_IMPLEMENTATION)\n'+t[start:end]+'#endif\n'+t[end:]
    t=t.replace('//#include <nanogui/opengl.h>','#include <nanogui/opengl.h>')
    start=t.index('void Screen::drawAll(\n');end=t.index('void Screen::drawWidgets()',start)
    t=t[:start]+'#if defined(NANOVG_VULKAN_IMPLEMENTATION)\n'+t[start:end]+'#endif\n'+t[end:]
    t=t.replace('void Screen::drawAll() {\n\n}', 'void Screen::drawAll() {\n    drawContents();\n    drawWidgets();\n}')
    t=t.replace('(mSize / mPixelRatio)', '(mSize.cast<float>() / mPixelRatio).cast<int>()')
    return t
patch('yabause/src/retro_arena/nanogui-sdl/src/screen.cpp',screen_source)
def scsp_linux_build(t):
    # Required for C++ compilation: the inherited Linux branch passes the
    # wrong types. This is not the paused producer/phase-lock experiment.
    t=t.replace('time(&tm);','clock_gettime(CLOCK_REALTIME, &tm);')
    t=t.replace('if( n > tm.tv_nsec){','if (tm.tv_nsec >= 1000000000L) {')
    t=t.replace('tm.tv_sec += 1;\n        }\n        pthread_mutex_lock(&sync_mutex);','tm.tv_sec += 1;\n          tm.tv_nsec -= 1000000000L;\n        }\n        pthread_mutex_lock(&sync_mutex);')
    t=t.replace('pthread_cond_timedwait(&sync_cnd,&sync_mutex,ctime(&tm))','pthread_cond_timedwait(&sync_cnd,&sync_mutex,&tm)')
    return t
patch('yabause/src/scsp.cpp',scsp_linux_build)
patch('yabause/src/m68kmusashi.c',lambda t:t.replace('#include "musashi/m68kcpu.h"\n#include "memory.h"','#include "memory.h"\n#include "musashi/m68kcpu.h"'))
patch('yabause/src/retro_arena/MenuScreen.h',lambda t:t.replace('#include <stack>','#include <stack>\n#include <memory>'))
patch('yabause/src/retro_arena/EventManager.h',lambda t:t.replace('#include <map>','#include <map>\n#include <string>'))
patch('yabause/src/retro_arena/GameInfo.cpp',lambda t:t.replace('#include "common.h"','#include "common.h"\n#include "../core.h"'))
patch('yabause/src/retro_arena/Preference.h',lambda t:t.replace('Preference::getStringArray','getStringArray'))
patch('yabause/src/retro_arena/Preference.cpp',lambda t:t.replace('Preference default("default");','Preference defaultPrefs("default");').replace('default.j.dump(2)','defaultPrefs.j.dump(2)').replace('#define LOG printf','#define LOG(...) ((void)0)'))
patch('yabause/src/memory.c',lambda t:re.sub(r'  ww_check\(addr, val, ([124])\);',r'#if CACHE_ENABLE\n  ww_check(addr, val, \1);\n#endif',t))
(YAB/'src/retro_arena/actionpi_ra_disabled.c').write_text('''/* This console trial has no RetroAchievements client. Match the official
 * wrapper's documented unavailable/uninitialized return values. */
#include "../retroachievements/yabause_ra_integration_cwrapper.h"
size_t YabauseRA_GetProgressSize(void) { return 0; }
int YabauseRA_SerializeProgress(uint8_t *buffer, size_t size) { (void)buffer; (void)size; return 0; }
int YabauseRA_DeserializeProgress(const uint8_t *buffer, size_t size) { (void)buffer; (void)size; return 0; }
''')
def linux_main(t):
    t=t.replace('#include <Shlobj.h>','#if defined(_WINDOWS)\n#include <Shlobj.h>\n#endif')
    t=t.replace('homedir += ".yabasanshiro";', 'homedir += "/.yabasanshiro/";')
    start=t.index('int __stdcall BrowseCallbackProc');end=t.index('//#undef main',start)
    t=t[:start]+'#if defined(_WINDOWS)\n'+t[start:end]+'#else\nbool selectDirectory(std::string &) { return false; }\n#endif\n'+t[end:]
    t=t.replace('int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE prevInstance, LPSTR lpCmdLine, int cmdShow)','int main(int argc, char **argv)')
    t=t.replace('  UINT value = GetACP();\n  SetConsoleOutputCP(value);','')
    t=t.replace('  char** argv = __argv;\n  int argc = __argc;','')
    start=t.index('#if 1\n  AllocConsole()');end=t.index('#endif',start)+len('#endif')
    t=t[:start]+'#if defined(_WINDOWS)\n'+t[start:end]+'\n#endif'+t[end:]
    t=t.replace('  SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE);','#if defined(_WINDOWS)\n  SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE);\n#endif')
    start=t.index('      SDL_SysWMinfo wmInfo;');end=t.index('      delete fname;',start)+len('      delete fname;')
    t=t[:start]+'#if defined(_WINDOWS)\n'+t[start:end]+'\n#else\n      fprintf(stderr,"Use the -b argument to select BIOS on this Linux trial.\\n");\n#endif'+t[end:]
    t=t.replace('  SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, 3);','  SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_ES);\n  SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, 3);')
    t=re.sub(r'(  NVGcontext \* InitNanoGuiVg\([^;]+;)',r'#if HAVE_VULKAN\n\1\n#endif',t)
    renderer='''  if (g_vidcoretype == VIDCORE_VULKAN) {
    r = new Renderer();
    r->setNativeWindow((void*)wnd);
    VIDVulkan::getInstance()->setRenderer(r);
  }
  else {'''
    assert renderer in t
    t=t.replace(renderer,'#if HAVE_VULKAN\n'+renderer[:-1]+'\n#endif\n  {')
    t=t.replace('#if 0\n        glClearColor', '#if !HAVE_VULKAN\n        glClearColor')
    t=t.replace('fflush(stdout_fp);','fflush(stdout);').replace('fflush(stderr_fp);','fflush(stderr);')
    t=t.replace('fclose(stdout_fp);','fflush(stdout);').replace('fclose(stderr_fp);','fflush(stderr);')
    # Official GLES startup registers an event on a menu which is now created
    # lazily. Register it when that menu exists, without changing emulation.
    t=t.replace('  menu->setRepeatEventCode(evRepeat);','  if (menu) menu->setRepeatEventCode(evRepeat);')
    t=t.replace('menu = new MenuScreen(wnd, width, height, g_keymap_filename, cdpath);','menu = new MenuScreen(wnd, width, height, g_keymap_filename, cdpath);\n            menu->setRepeatEventCode(evRepeat);')
    t=t.replace('#else\n          VdpRevoke();\n#endif','#else\n          VdpRevoke();\n          YuiUseOGLOnThisThread();\n#endif')
    return t
patch('yabause/src/retro_arena/main.cpp',linux_main)

# Find modules bind only to matching, staged target libraries.
mods=YAB/'CMake/Packages'
(mods/'FindSDL2.cmake').write_text(f'set(SDL2_FOUND TRUE)\nset(SDL2_INCLUDE_DIR {SDK}/usr/include/SDL2)\nset(SDL2_INCLUDE_DIRS ${{SDL2_INCLUDE_DIR}})\nset(SDL2_LIBRARY {SDK}/usr/lib/libSDL2.so)\nset(SDL2_LIBRARIES ${{SDL2_LIBRARY}})\n')
(mods/'FindOpenGL.cmake').write_text(f'set(OPENGL_FOUND TRUE)\nset(OPENGL_LIBRARIES {SDK}/usr/lib/libEGL.so {SDK}/usr/lib/libGLESv2.so)\nset(OPENGL_INCLUDE_DIR {SDK}/usr/include)\n')
(OUT/'linux-gles-build.patch').write_text(''.join(patches))
args=[cmake,'-S',str(YAB),'-B',str(BUILD),'-DCMAKE_TOOLCHAIN_FILE='+str(toolchain),'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_EXPORT_COMPILE_COMMANDS=ON','-DCMAKE_SKIP_RPATH=ON',
 '-DYAB_PORTS=retro_arena','-DYAB_WANT_DYNAREC_DEVMIYAX=ON','-DUSE_EGL=ON','-DYAB_WANT_VULKAN=OFF','-DYAB_WANT_OPENAL=OFF','-DYAB_WANT_MUSASHI=ON','-DBUILD_SHARED_LIBS=OFF','-DYAB_USE_SCSP2=OFF','-DSH2_TRACE=OFF',
 '-DOPENSSL_ROOT_DIR='+str(SDK)+'/usr','-DOPENSSL_INCLUDE_DIR='+str(SDK)+'/usr/include','-DOPENSSL_SSL_LIBRARY='+str(SDK)+'/usr/lib/libssl.so','-DOPENSSL_CRYPTO_LIBRARY='+str(SDK)+'/usr/lib/libcrypto.so',
 '-DZLIB_LIBRARY='+str(SDK)+'/usr/lib/libz.so','-DZLIB_INCLUDE_DIR='+str(SDK)+'/usr/include','-DPNG_LIBRARY='+str(SDK)+'/usr/lib/libpng16.so.16','-DPNG_PNG_INCLUDE_DIR='+str(SDK)+'/usr/include']
(OUT/'configure-command.json').write_text(json.dumps(args,indent=2)+'\n')
with (OUT/'configure.log').open('w') as log:subprocess.run(args,stdout=log,stderr=subprocess.STDOUT,check=True)
print('OFFICIAL_12051_CONFIGURED',flush=True)
