/* PySDL2 resolves functions from a named DLL, bypassing LD_PRELOAD hooks.
 * Link this adapter to the original SDL2 and select it for PortMaster only. */
#include "retroarch_output_rotation.c"

int SDL_GetRendererOutputSize(Renderer *r,int *w,int *h) {
    REAL(int,SDL_GetRendererOutputSize,(Renderer *,int *,int *));
    int x=0,y=0,rc=real_SDL_GetRendererOutputSize(r,&x,&y);
    if(!rc && lookup(r)) { x=960;y=720; }
    if(w)*w=x;
    if(h)*h=y;
    return rc;
}
