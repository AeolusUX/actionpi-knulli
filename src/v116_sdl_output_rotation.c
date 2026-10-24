/* Only the PPSSPP process receives these logical landscape SDL dimensions. */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdint.h>
typedef struct {uint32_t format;int w,h,hz;void *driver;} Mode;
static void swap_size(int *w,int *h){if(*w==720 && *h==960){*w=960;*h=720;}}
#define SIZE_FN(name) void name(void *window,int *w,int *h){\
 static void(*real)(void*,int*,int*);if(!real)real=dlsym(RTLD_NEXT,#name);\
 int a=0,b=0;real(window,&a,&b);swap_size(&a,&b);if(w)*w=a;if(h)*h=b;}
SIZE_FN(SDL_GetWindowSize)
SIZE_FN(SDL_Vulkan_GetDrawableSize)
SIZE_FN(SDL_GL_GetDrawableSize)
#define MODE_FN(name) int name(int display,Mode *mode){\
 static int(*real)(int,Mode*);if(!real)real=dlsym(RTLD_NEXT,#name);\
 int r=real(display,mode);if(!r && mode)swap_size(&mode->w,&mode->h);return r;}
MODE_FN(SDL_GetCurrentDisplayMode)
MODE_FN(SDL_GetDesktopDisplayMode)
static void rotate_event(int r,void *event){
 if(r && event){uint32_t *words=event;unsigned char *bytes=event;
  if(words[0]==0x200 && (bytes[12]==5 || bytes[12]==6))swap_size((int*)&words[4],(int*)&words[5]);
 }
}
int SDL_PollEvent(void *event){
 static int(*real)(void*);if(!real)real=dlsym(RTLD_NEXT,"SDL_PollEvent");int r=real(event);rotate_event(r,event);
 return r;
}
int SDL_WaitEventTimeout(void *event,int timeout){
 static int(*real)(void*,int);if(!real)real=dlsym(RTLD_NEXT,"SDL_WaitEventTimeout");int r=real(event,timeout);rotate_event(r,event);
 return r;
}
int SDL_WaitEvent(void *event){
 static int(*real)(void*);if(!real)real=dlsym(RTLD_NEXT,"SDL_WaitEvent");int r=real(event);rotate_event(r,event);
 return r;
}
