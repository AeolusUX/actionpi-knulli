#define _GNU_SOURCE
#include <dlfcn.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Public SDL2 structure prefixes; no private renderer or kernel ABI access. */
typedef struct { uint32_t format; void *palette; uint8_t bits,bytes; } Format;
typedef struct { uint32_t flags; Format *format; int w,h,pitch; void *pixels; } Surface;
typedef void Window;
typedef struct { int x,y,w,h; } Rect;
typedef struct State { Window *window; Surface *canvas; struct State *next; } State;
static State *states;
_Static_assert(offsetof(Surface,format)==8 && offsetof(Surface,pixels)==32,"64bit SDL2 surface ABI");
#define REAL(ret,name,args) ret (*real_##name) args = dlsym(RTLD_NEXT,#name)
static State *lookup(Window *w) { for(State *s=states;s;s=s->next)if(s->window==w)return s;return NULL; }

void SDL_GetWindowSize(Window *window,int *w,int *h) {
    REAL(void,SDL_GetWindowSize,(Window *,int *,int *));int x=0,y=0;
    real_SDL_GetWindowSize(window,&x,&y);
    if(x==720 && y==960) { x=960;y=720; }
    if(w)*w=x;
    if(h)*h=y;
}

Surface *SDL_GetWindowSurface(Window *window) {
    REAL(Surface *,SDL_GetWindowSurface,(Window *));
    Surface *physical=real_SDL_GetWindowSurface(window);
    if(!physical || physical->w!=720 || physical->h!=960)return physical;
    State *s=lookup(window);
    if(s)return s->canvas;
    REAL(Surface *,SDL_CreateRGBSurfaceWithFormat,(uint32_t,int,int,int,uint32_t));
    REAL(void,SDL_FreeSurface,(Surface *));
    Surface *canvas=real_SDL_CreateRGBSurfaceWithFormat(0,960,720,physical->format->bits,physical->format->format);
    s=calloc(1,sizeof(*s));
    if(!s || !canvas) { free(s);if(canvas)real_SDL_FreeSurface(canvas);return physical; }
    s->window=window;s->canvas=canvas;s->next=states;states=s;
    fprintf(stderr,"ACTIONPI_OD_ROTATION logical=960x720 physical=720x960 clockwise90\n");
    return canvas;
}

static int rotate_surface(const Surface *src,Surface *dst) {
    unsigned bpp=src->format->bytes;
    if(!src->pixels || !dst->pixels || bpp<1 || bpp>4 || dst->format->format!=src->format->format ||
       dst->w!=src->h || dst->h!=src->w || src->pitch<src->w*(int)bpp || dst->pitch<dst->w*(int)bpp)return -1;
    for(int y=0;y<src->h;y++)for(int x=0;x<src->w;x++) {
        unsigned char *from=(unsigned char *)src->pixels+(size_t)y*src->pitch+(size_t)x*bpp;
        unsigned char *to=(unsigned char *)dst->pixels+(size_t)x*dst->pitch+(size_t)(dst->w-1-y)*bpp;
        memcpy(to,from,bpp);
    }
    return 0;
}

int SDL_UpdateWindowSurface(Window *window) {
    REAL(int,SDL_UpdateWindowSurface,(Window *));State *s=lookup(window);
    if(!s)return real_SDL_UpdateWindowSurface(window);
    REAL(Surface *,SDL_GetWindowSurface,(Window *));
    REAL(int,SDL_LockSurface,(Surface *));
    REAL(void,SDL_UnlockSurface,(Surface *));
    Surface *physical=real_SDL_GetWindowSurface(window);
    if(!physical || real_SDL_LockSurface(s->canvas))return -1;
    if(real_SDL_LockSurface(physical)) { real_SDL_UnlockSurface(s->canvas);return -1; }
    int rc=rotate_surface(s->canvas,physical);
    real_SDL_UnlockSurface(physical);real_SDL_UnlockSurface(s->canvas);
    return rc ? rc : real_SDL_UpdateWindowSurface(window);
}

int SDL_UpdateWindowSurfaceRects(Window *window,const Rect *rects,int count) {
    REAL(int,SDL_UpdateWindowSurfaceRects,(Window *,const Rect *,int));
    if(!lookup(window))return real_SDL_UpdateWindowSurfaceRects(window,rects,count);
    return SDL_UpdateWindowSurface(window);
}

void SDL_DestroyWindow(Window *window) {
    REAL(void,SDL_DestroyWindow,(Window *));REAL(void,SDL_FreeSurface,(Surface *));
    State **link=&states;
    while(*link) {
        if((*link)->window==window) { State *s=*link;*link=s->next;real_SDL_FreeSurface(s->canvas);free(s);break; }
        link=&(*link)->next;
    }
    real_SDL_DestroyWindow(window);
}
