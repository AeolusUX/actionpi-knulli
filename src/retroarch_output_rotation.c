#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef void Renderer;
typedef void Texture;
typedef void Window;
typedef struct { int x,y,w,h; } Rect;
typedef struct { unsigned format; int w,h,refresh; void *data; } Mode;
typedef struct State { Renderer *renderer; Texture *canvas; int w,h; struct State *next; } State;
static State *states;
static State *lookup(Renderer *r) { for(State *s=states;s;s=s->next)if(s->renderer==r)return s;return NULL; }
#define REAL(ret,name,args) ret (*real_##name) args = dlsym(RTLD_NEXT,#name)

void SDL_GetWindowSize(Window *window,int *w,int *h) {
    REAL(void,SDL_GetWindowSize,(Window *,int *,int *));int x,y;
    real_SDL_GetWindowSize(window,&x,&y);
    if(x==720 && y==960) { x=960;y=720; }
    if(w)*w=x;
    if(h)*h=y;
}
static void mode_rotate(Mode *m) { if(m && m->w==720 && m->h==960) { m->w=960;m->h=720; } }
int SDL_GetCurrentDisplayMode(int display,Mode *m) { REAL(int,SDL_GetCurrentDisplayMode,(int,Mode *));int rc=real_SDL_GetCurrentDisplayMode(display,m);if(!rc)mode_rotate(m);return rc; }
int SDL_GetDesktopDisplayMode(int display,Mode *m) { REAL(int,SDL_GetDesktopDisplayMode,(int,Mode *));int rc=real_SDL_GetDesktopDisplayMode(display,m);if(!rc)mode_rotate(m);return rc; }

Renderer *SDL_CreateRenderer(Window *window,int index,unsigned flags) {
    REAL(Renderer *,SDL_CreateRenderer,(Window *,int,unsigned));
    REAL(int,SDL_GetRendererOutputSize,(Renderer *,int *,int *));
    REAL(Texture *,SDL_CreateTexture,(Renderer *,unsigned,int,int,int));
    REAL(int,SDL_SetRenderTarget,(Renderer *,Texture *));
    REAL(int,SDL_SetTextureBlendMode,(Texture *,int));
    REAL(void,SDL_DestroyTexture,(Texture *));
    Renderer *r=real_SDL_CreateRenderer(window,index,flags);
    int w=0,h=0;
    if(!r || real_SDL_GetRendererOutputSize(r,&w,&h) || w!=720 || h!=960)return r;
    Texture *canvas=real_SDL_CreateTexture(r,0x16362004u,2,960,720); /* ARGB8888, TARGET */
    State *s=calloc(1,sizeof(*s));
    if(!canvas || !s || real_SDL_SetTextureBlendMode(canvas,0) || real_SDL_SetRenderTarget(r,canvas)) {
        if(canvas)real_SDL_DestroyTexture(canvas);
        free(s);fprintf(stderr,"ACTIONPI_RA_ROTATION canvas creation failed\n");return r;
    }
    s->renderer=r;s->canvas=canvas;s->w=w;s->h=h;s->next=states;states=s;
    fprintf(stderr,"ACTIONPI_RA_ROTATION logical=960x720 physical=720x960 clockwise90\n");
    return r;
}
int SDL_SetRenderTarget(Renderer *r,Texture *texture) {
    REAL(int,SDL_SetRenderTarget,(Renderer *,Texture *));State *s=lookup(r);
    return real_SDL_SetRenderTarget(r,(!texture && s)?s->canvas:texture);
}
Texture *SDL_GetRenderTarget(Renderer *r) {
    REAL(Texture *,SDL_GetRenderTarget,(Renderer *));Texture *t=real_SDL_GetRenderTarget(r);State *s=lookup(r);
    return (s && t==s->canvas)?NULL:t;
}
void SDL_RenderPresent(Renderer *r) {
    REAL(void,SDL_RenderPresent,(Renderer *));State *s=lookup(r);
    if(!s) { real_SDL_RenderPresent(r);return; }
    REAL(Texture *,SDL_GetRenderTarget,(Renderer *));
    REAL(int,SDL_SetRenderTarget,(Renderer *,Texture *));
    REAL(void,SDL_RenderGetViewport,(Renderer *,Rect *));
    REAL(int,SDL_RenderSetViewport,(Renderer *,const Rect *));
    REAL(void,SDL_RenderGetClipRect,(Renderer *,Rect *));
    REAL(int,SDL_RenderIsClipEnabled,(Renderer *));
    REAL(int,SDL_RenderSetClipRect,(Renderer *,const Rect *));
    REAL(void,SDL_RenderGetScale,(Renderer *,float *,float *));
    REAL(int,SDL_RenderSetScale,(Renderer *,float,float));
    REAL(void,SDL_RenderGetLogicalSize,(Renderer *,int *,int *));
    REAL(int,SDL_RenderSetLogicalSize,(Renderer *,int,int));
    REAL(int,SDL_RenderCopyEx,(Renderer *,Texture *,const Rect *,const Rect *,double,const void *,int));
    REAL(int,SDL_SetRenderDrawColor,(Renderer *,unsigned char,unsigned char,unsigned char,unsigned char));
    REAL(int,SDL_GetRenderDrawColor,(Renderer *,unsigned char *,unsigned char *,unsigned char *,unsigned char *));
    REAL(int,SDL_RenderClear,(Renderer *));
    Texture *target=real_SDL_GetRenderTarget(r);Rect viewport,clip;
    float xscale,yscale;int lw,lh;unsigned char red,green,blue,alpha;
    real_SDL_RenderGetViewport(r,&viewport);real_SDL_RenderGetClipRect(r,&clip);
    int clipping=real_SDL_RenderIsClipEnabled(r);
    real_SDL_RenderGetScale(r,&xscale,&yscale);real_SDL_RenderGetLogicalSize(r,&lw,&lh);
    real_SDL_GetRenderDrawColor(r,&red,&green,&blue,&alpha);
    real_SDL_SetRenderTarget(r,NULL);real_SDL_RenderSetLogicalSize(r,0,0);
    real_SDL_RenderSetScale(r,1,1);real_SDL_RenderSetViewport(r,NULL);real_SDL_RenderSetClipRect(r,NULL);
    real_SDL_SetRenderDrawColor(r,0,0,0,255);real_SDL_RenderClear(r);
    Rect dest={(s->w-960)/2,(s->h-720)/2,960,720};
    real_SDL_RenderCopyEx(r,s->canvas,NULL,&dest,90,NULL,0);real_SDL_RenderPresent(r);
    real_SDL_SetRenderTarget(r,target);real_SDL_RenderSetLogicalSize(r,lw,lh);
    real_SDL_RenderSetScale(r,xscale,yscale);real_SDL_RenderSetViewport(r,&viewport);
    real_SDL_RenderSetClipRect(r,clipping?&clip:NULL);real_SDL_SetRenderDrawColor(r,red,green,blue,alpha);
}
void SDL_DestroyRenderer(Renderer *r) {
    REAL(void,SDL_DestroyRenderer,(Renderer *));State **link=&states;
    while(*link) { if((*link)->renderer==r) { State *s=*link;*link=s->next;free(s);break; }link=&(*link)->next; }
    real_SDL_DestroyRenderer(r); /* SDL owns and destroys all textures including our canvas. */
}
