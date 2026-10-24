/* PPSSPP-only logical landscape surface over the portrait KMS scanout.
 * The real driver always receives its original physical extent and transform.
 * Uses the same local loader forwarding route already validated for this device.
 */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
typedef void *H;
typedef int32_t R;
typedef void (*F)(void);
typedef F (*Getter)(H,const char*);
typedef struct {uint32_t w,h;} Extent;
typedef struct {uint32_t min_count,max_count;Extent current,min,max;uint32_t layers,supported,current_transform,alpha,usage;} Caps;
typedef struct {uint32_t type;const void *next;uint32_t flags;uint64_t surface;uint32_t min_count,format,color;Extent extent;uint32_t layers,usage,sharing,count;const uint32_t *queues;uint32_t transform,alpha,mode,clipped;uint64_t old;} Swap;
typedef struct {uint64_t mode;Extent visible;uint32_t refresh;} DisplayMode;
typedef struct {uint32_t type;const void *next;uint32_t flags;uint64_t mode;uint32_t plane,stack,transform;float global_alpha;uint32_t alpha;Extent extent;} DisplaySurface;
_Static_assert(sizeof(Caps)==52,"Vulkan surface capabilities ABI");
_Static_assert(sizeof(Swap)==104,"Vulkan swapchain info ABI");
_Static_assert(sizeof(DisplayMode)==24,"Vulkan display mode ABI");
_Static_assert(sizeof(DisplaySurface)==64,"Vulkan display surface ABI");
static Getter ig,dg;static void *real_lib;
static R (*caps_fn)(H,uint64_t,Caps*);
static R (*swap_fn)(H,const Swap*,const void*,uint64_t*);
static R (*modes_fn)(H,uint64_t,uint32_t*,DisplayMode*);
static R (*surface_fn)(H,const DisplaySurface*,const void*,uint64_t*);
static Caps physical;static uint64_t surface_id;static int configured;
static void init(void){
 if(ig)return;
 real_lib=dlopen("/usr/lib/libvulkan.so.1",RTLD_NOW|RTLD_LOCAL|RTLD_DEEPBIND);
 if(!real_lib){fprintf(stderr,"OUTPUT_ROTATION_LOADER_ERROR %s\n",dlerror());return;}
 ig=(Getter)dlsym(real_lib,"vkGetInstanceProcAddr");dg=(Getter)dlsym(real_lib,"vkGetDeviceProcAddr");
}
static Extent transpose(Extent e){return (Extent){e.h,e.w};}
static R logical_modes(H p,uint64_t display,uint32_t *count,DisplayMode *out){
 R r=modes_fn(p,display,count,out);
 if(r>=0 && out && count)for(uint32_t i=0;i<*count;i++)if(out[i].visible.w==720 && out[i].visible.h==960)out[i].visible=transpose(out[i].visible);
 return r;
}
static R physical_surface(H i,const DisplaySurface *in,const void *alloc,uint64_t *out){
 if(in && in->extent.w==960 && in->extent.h==720){
  DisplaySurface copy=*in;copy.extent=transpose(copy.extent);
  R r=surface_fn(i,&copy,alloc,out);fprintf(stderr,"OUTPUT_ROTATION_SURFACE physical=720x960 result=%d\n",r);return r;
 }
 return surface_fn(i,in,alloc,out);
}
static R rotated_caps(H p,uint64_t surface,Caps *out){
 R r=caps_fn(p,surface,out);
 if(r==0 && out && out->current.w==720 && out->current.h==960 && (out->supported&1)){
  physical=*out;surface_id=surface;configured=1;
  out->current=transpose(out->current);out->min=transpose(out->min);out->max=transpose(out->max);
  out->supported|=2;out->current_transform=2;
  fprintf(stderr,"OUTPUT_ROTATION logical=960x720 transform=90 physical=720x960\n");
 }
 return r;
}
static R physical_swap(H d,const Swap *in,const void *alloc,uint64_t *out){
 if(configured && in && in->surface==surface_id && in->transform==2){
  if(in->extent.w!=physical.current.w || in->extent.h!=physical.current.h){
   fprintf(stderr,"OUTPUT_ROTATION_EXTENT_REJECT %ux%u\n",in->extent.w,in->extent.h);return -3;
  }
  Swap copy=*in;copy.transform=1;
  R r=swap_fn(d,&copy,alloc,out);
  fprintf(stderr,"OUTPUT_ROTATION_SWAPCHAIN physical=%ux%u identity result=%d\n",copy.extent.w,copy.extent.h,r);return r;
 }
 return swap_fn(d,in,alloc,out);
}
F vkGetDeviceProcAddr(H d,const char *name){
 init();if(!dg)return 0;F f=dg(d,name);
 if(f && !strcmp(name,"vkCreateSwapchainKHR")){swap_fn=(void*)f;return(F)physical_swap;}return f;
}
F vkGetInstanceProcAddr(H i,const char *name){
 init();if(!ig)return 0;
 if(!strcmp(name,"vkGetDeviceProcAddr"))return(F)vkGetDeviceProcAddr;
 if(!strcmp(name,"vkGetInstanceProcAddr"))return(F)vkGetInstanceProcAddr;
 F f=ig(i,name);
 if(f && !strcmp(name,"vkGetDisplayModePropertiesKHR")){modes_fn=(void*)f;return(F)logical_modes;}
 if(f && !strcmp(name,"vkCreateDisplayPlaneSurfaceKHR")){surface_fn=(void*)f;return(F)physical_surface;}
 if(f && !strcmp(name,"vkGetPhysicalDeviceSurfaceCapabilitiesKHR")){caps_fn=(void*)f;return(F)rotated_caps;}
 if(f && !strcmp(name,"vkCreateSwapchainKHR")){swap_fn=(void*)f;return(F)physical_swap;}return f;
}
R vkCreateInstance(const void *a,const void *b,H *c){init();return((R(*)(const void*,const void*,H*))dlsym(real_lib,"vkCreateInstance"))(a,b,c);}
R vkEnumerateInstanceExtensionProperties(const char *a,uint32_t *b,void *c){init();return((R(*)(const char*,uint32_t*,void*))dlsym(real_lib,"vkEnumerateInstanceExtensionProperties"))(a,b,c);}
R vkEnumerateInstanceLayerProperties(uint32_t *a,void *b){init();return((R(*)(uint32_t*,void*))dlsym(real_lib,"vkEnumerateInstanceLayerProperties"))(a,b);}
R vkEnumerateInstanceVersion(uint32_t *v){init();F f=dlsym(real_lib,"vkEnumerateInstanceVersion");if(!f){*v=1U<<22;return 0;}return((R(*)(uint32_t*))f)(v);}
