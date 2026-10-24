/* Rotate the complete SDL GLES drawable, including Flycast/RetroArch menus.
 * Scoped by the launcher to Dreamcast-family GL processes on this panel only. */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
typedef unsigned int U; typedef int I; typedef unsigned char B;
typedef struct {U format;I w,h,hz;void *data;} Mode;
typedef struct State {void *ctx,*window;U fbo,tex,depth,program,vao,vbo;struct State *next;} State;
static State *states;
static __thread int internal;
static __thread int resolving;
static void *proc(const char *n) {void *(*p)(const char*)=dlsym(RTLD_NEXT,"SDL_GL_GetProcAddress");resolving++;void *v=p(n);resolving--;return v;}
#define FN(ret,n,args) static ret (*r_##n) args
FN(void,glGetIntegerv,(U,I*));FN(void,glGetBooleanv,(U,B*));FN(B,glIsEnabled,(U));
FN(void,glEnable,(U));FN(void,glDisable,(U));FN(const B*,glGetString,(U));
FN(void,glBindFramebuffer,(U,U));FN(void,glGenFramebuffers,(I,U*));FN(U,glCheckFramebufferStatus,(U));
FN(void,glFramebufferTexture2D,(U,U,U,U,I));FN(void,glGenTextures,(I,U*));FN(void,glBindTexture,(U,U));
FN(void,glTexImage2D,(U,I,I,I,I,I,U,U,const void*));FN(void,glTexParameteri,(U,U,I));
FN(void,glGenRenderbuffers,(I,U*));FN(void,glBindRenderbuffer,(U,U));FN(void,glRenderbufferStorage,(U,U,I,I));
FN(void,glFramebufferRenderbuffer,(U,U,U,U));FN(U,glCreateShader,(U));FN(void,glShaderSource,(U,I,const char*const*,const I*));
FN(void,glCompileShader,(U));FN(void,glGetShaderiv,(U,U,I*));FN(void,glGetShaderInfoLog,(U,I,I*,char*));
FN(U,glCreateProgram,(void));FN(void,glAttachShader,(U,U));FN(void,glBindAttribLocation,(U,U,const char*));
FN(void,glLinkProgram,(U));FN(void,glGetProgramiv,(U,U,I*));FN(void,glDeleteShader,(U));FN(void,glUseProgram,(U));
FN(I,glGetUniformLocation,(U,const char*));FN(void,glUniform1i,(I,I));FN(void,glActiveTexture,(U));
FN(void,glGenBuffers,(I,U*));FN(void,glBindBuffer,(U,U));FN(void,glBufferData,(U,ptrdiff_t,const void*,U));
FN(void,glGenVertexArrays,(I,U*));FN(void,glBindVertexArray,(U));FN(void,glEnableVertexAttribArray,(U));
FN(void,glVertexAttribPointer,(U,I,U,B,I,const void*));FN(void,glDrawArrays,(U,I,I));
FN(void,glViewport,(I,I,I,I));FN(void,glColorMask,(B,B,B,B));
FN(void,glInvalidateFramebuffer,(U,I,const U*));FN(void,glReadBuffer,(U));FN(void,glDrawBuffers,(I,const U*));
#define LOAD(n) do {r_##n=proc(#n);if(!r_##n){fprintf(stderr,"ACTIONPI_GL missing %s\n",#n);return 0;}}while(0)
static int load(void) {
 LOAD(glGetIntegerv);LOAD(glGetBooleanv);LOAD(glIsEnabled);LOAD(glGetString);LOAD(glEnable);LOAD(glDisable);
 LOAD(glBindFramebuffer);LOAD(glGenFramebuffers);LOAD(glCheckFramebufferStatus);LOAD(glFramebufferTexture2D);
 LOAD(glGenTextures);LOAD(glBindTexture);LOAD(glTexImage2D);LOAD(glTexParameteri);
 LOAD(glGenRenderbuffers);LOAD(glBindRenderbuffer);LOAD(glRenderbufferStorage);LOAD(glFramebufferRenderbuffer);
 LOAD(glCreateShader);LOAD(glShaderSource);LOAD(glCompileShader);LOAD(glGetShaderiv);LOAD(glGetShaderInfoLog);
 LOAD(glCreateProgram);LOAD(glAttachShader);LOAD(glBindAttribLocation);LOAD(glLinkProgram);LOAD(glGetProgramiv);
 LOAD(glDeleteShader);LOAD(glUseProgram);LOAD(glGetUniformLocation);LOAD(glUniform1i);LOAD(glActiveTexture);
 LOAD(glGenBuffers);LOAD(glBindBuffer);LOAD(glBufferData);LOAD(glGenVertexArrays);LOAD(glBindVertexArray);
 LOAD(glEnableVertexAttribArray);LOAD(glVertexAttribPointer);LOAD(glDrawArrays);LOAD(glViewport);LOAD(glColorMask);
 LOAD(glInvalidateFramebuffer);LOAD(glReadBuffer);LOAD(glDrawBuffers);return 1;
}
static State *current(void) {
 if(internal)return NULL;
 void *(*get)(void)=dlsym(RTLD_NEXT,"SDL_GL_GetCurrentContext");void *ctx=get();
 for(State *s=states;s;s=s->next)if(s->ctx==ctx)return s;
 return NULL;
}
static U shader(U kind,const char *src) {
 U s=r_glCreateShader(kind);I ok;r_glShaderSource(s,1,&src,NULL);r_glCompileShader(s);r_glGetShaderiv(s,0x8b81,&ok);
 if(!ok){char log[1024];r_glGetShaderInfoLog(s,sizeof(log),NULL,log);fprintf(stderr,"ACTIONPI_GL shader %s\n",log);return 0;}
 return s;
}
static void init(void *window,void *ctx) {
 int w,h;void(*size)(void*,I*,I*)=dlsym(RTLD_NEXT,"SDL_GL_GetDrawableSize");size(window,&w,&h);
 if(w!=720||h!=960)return;
 internal++;if(!load()){internal--;return;}
 const char *version=(const char*)r_glGetString(0x1f02);
 if(!version||!strstr(version,"OpenGL ES 3")){fprintf(stderr,"ACTIONPI_GL needs GLES3: %s\n",version?version:"");internal--;return;}
 State *s=calloc(1,sizeof(*s));if(!s){internal--;return;}s->ctx=ctx;s->window=window;
 I active,tex,rb,array,buffer,program,draw,read;
 r_glGetIntegerv(0x84e0,&active);r_glActiveTexture(0x84c0);r_glGetIntegerv(0x8069,&tex);
 r_glGetIntegerv(0x8ca7,&rb);r_glGetIntegerv(0x85b5,&array);r_glGetIntegerv(0x8894,&buffer);
 r_glGetIntegerv(0x8b8d,&program);r_glGetIntegerv(0x8ca6,&draw);r_glGetIntegerv(0x8caa,&read);
 r_glGenTextures(1,&s->tex);r_glBindTexture(0x0de1,s->tex);
 r_glTexImage2D(0x0de1,0,0x1908,960,720,0,0x1908,0x1401,NULL);
 r_glTexParameteri(0x0de1,0x2801,0x2600);r_glTexParameteri(0x0de1,0x2800,0x2600);
 r_glTexParameteri(0x0de1,0x2802,0x812f);r_glTexParameteri(0x0de1,0x2803,0x812f);
 r_glGenFramebuffers(1,&s->fbo);r_glBindFramebuffer(0x8d40,s->fbo);
 r_glFramebufferTexture2D(0x8d40,0x8ce0,0x0de1,s->tex,0);
 r_glGenRenderbuffers(1,&s->depth);r_glBindRenderbuffer(0x8d41,s->depth);r_glRenderbufferStorage(0x8d41,0x88f0,960,720);
 r_glFramebufferRenderbuffer(0x8d40,0x821a,0x8d41,s->depth);
 U status=r_glCheckFramebufferStatus(0x8d40);
 const char *vs="attribute vec2 p;attribute vec2 t;varying vec2 uv;void main(){gl_Position=vec4(p,0.,1.);uv=t;}";
 const char *fs="precision mediump float;varying vec2 uv;uniform sampler2D image;void main(){gl_FragColor=vec4(texture2D(image,uv).rgb,1.);}";
 U v=shader(0x8b31,vs),f=shader(0x8b30,fs);I ok=0;
 if(v&&f){s->program=r_glCreateProgram();r_glAttachShader(s->program,v);r_glAttachShader(s->program,f);
 r_glBindAttribLocation(s->program,0,"p");r_glBindAttribLocation(s->program,1,"t");r_glLinkProgram(s->program);r_glGetProgramiv(s->program,0x8b82,&ok);}
 if(v)r_glDeleteShader(v);
 if(f)r_glDeleteShader(f);
 /* Source (u,v)=(1-y,x) gives physical clockwise rotation (GL y is up). */
 const float vertices[]={-1,-1,1,0, 1,-1,1,1, -1,1,0,0, 1,1,0,1};
 r_glGenVertexArrays(1,&s->vao);r_glBindVertexArray(s->vao);r_glGenBuffers(1,&s->vbo);
 r_glBindBuffer(0x8892,s->vbo);r_glBufferData(0x8892,sizeof(vertices),vertices,0x88e4);
 r_glEnableVertexAttribArray(0);r_glVertexAttribPointer(0,2,0x1406,0,16,(void*)0);
 r_glEnableVertexAttribArray(1);r_glVertexAttribPointer(1,2,0x1406,0,16,(void*)8);
 r_glUseProgram(s->program);if(ok)r_glUniform1i(r_glGetUniformLocation(s->program,"image"),0);
 r_glBindVertexArray(array);r_glBindBuffer(0x8892,buffer);r_glUseProgram(program);
 r_glBindRenderbuffer(0x8d41,rb);r_glBindTexture(0x0de1,tex);r_glActiveTexture(active);
 if(status==0x8cd5&&ok){s->next=states;states=s;r_glBindFramebuffer(0x8ca9,draw?(U)draw:s->fbo);r_glBindFramebuffer(0x8ca8,read?(U)read:s->fbo);
 r_glViewport(0,0,960,720);fprintf(stderr,"ACTIONPI_GL_ROTATION logical=960x720 physical=720x960 clockwise90\n");}
 else {fprintf(stderr,"ACTIONPI_GL_ROTATION failed FBO=%x shader=%d\n",status,ok);r_glBindFramebuffer(0x8ca9,draw);r_glBindFramebuffer(0x8ca8,read);free(s);}
 internal--;
}
void *SDL_GL_CreateContext(void *window) {void*(*real)(void*)=dlsym(RTLD_NEXT,"SDL_GL_CreateContext");void *ctx=real(window);if(ctx){init(window,ctx);void(*refresh)(void)=dlsym(RTLD_DEFAULT,"actionpi_refresh_signal_bridge");if(refresh)refresh();}return ctx;}
void SDL_GL_DeleteContext(void *ctx) {void(*real)(void*)=dlsym(RTLD_NEXT,"SDL_GL_DeleteContext");State **p=&states;while(*p){if((*p)->ctx==ctx){State *s=*p;*p=s->next;free(s);break;}p=&(*p)->next;}real(ctx);}
void glBindFramebuffer(U target,U fb) {if(!r_glBindFramebuffer)r_glBindFramebuffer=proc("glBindFramebuffer");State*s=current();r_glBindFramebuffer(target,(!fb&&s)?s->fbo:fb);}
void glGetIntegerv(U key,I *value) {if(!r_glGetIntegerv)r_glGetIntegerv=proc("glGetIntegerv");r_glGetIntegerv(key,value);State*s=current();if(s&&(key==0x8ca6||key==0x8caa)&&(U)*value==s->fbo)*value=0;}
void glReadBuffer(U mode) {State*s=current();I fb;r_glGetIntegerv(0x8caa,&fb);r_glReadBuffer(s&&(U)fb==s->fbo&&mode==0x0405?0x8ce0:mode);}
void glDrawBuffers(I n,const U *modes) {State*s=current();I fb;r_glGetIntegerv(0x8ca6,&fb);if(s&&(U)fb==s->fbo&&n==1&&modes[0]==0x0405){U m=0x8ce0;r_glDrawBuffers(1,&m);}else r_glDrawBuffers(n,modes);}
void glInvalidateFramebuffer(U target,I n,const U *attachments) {
 State*s=current();I fb;r_glGetIntegerv(target==0x8ca8?0x8caa:0x8ca6,&fb);
 if(s&&(U)fb==s->fbo&&n>=0&&n<=16){U a[16];for(int i=0;i<n;i++)a[i]=attachments[i]==0x1800?0x8ce0:attachments[i]==0x1801?0x8d00:attachments[i]==0x1802?0x8d20:attachments[i];r_glInvalidateFramebuffer(target,n,a);}
 else r_glInvalidateFramebuffer(target,n,attachments);
}
static void *wrapped(const char *name) {
 if(!strcmp(name,"glBindFramebuffer")||!strcmp(name,"glBindFramebufferEXT")||!strcmp(name,"glBindFramebufferOES"))return glBindFramebuffer;
 if(!strcmp(name,"glGetIntegerv"))return glGetIntegerv;
 if(!strcmp(name,"glReadBuffer"))return glReadBuffer;
 if(!strcmp(name,"glDrawBuffers"))return glDrawBuffers;
 if(!strcmp(name,"glInvalidateFramebuffer")||!strcmp(name,"glDiscardFramebufferEXT"))return glInvalidateFramebuffer;
 return NULL;
}
void *SDL_GL_GetProcAddress(const char *name) {void *p=wrapped(name);return p?p:proc(name);}
void *eglGetProcAddress(const char *name) {void *p=resolving?NULL:wrapped(name);if(p)return p;void*(*real)(const char*)=dlsym(RTLD_NEXT,"eglGetProcAddress");return real(name);}
static void size_swap(I*w,I*h) {if(*w==720&&*h==960){*w=960;*h=720;}}
#define SIZE(name) void name(void*window,I*w,I*h){void(*real)(void*,I*,I*)=dlsym(RTLD_NEXT,#name);I a,b;real(window,&a,&b);size_swap(&a,&b);if(w)*w=a;if(h)*h=b;}
SIZE(SDL_GetWindowSize)
SIZE(SDL_GL_GetDrawableSize)
#define MODE(name) I name(I d,Mode*m){I(*real)(I,Mode*)=dlsym(RTLD_NEXT,#name);I rc=real(d,m);if(!rc&&m)size_swap(&m->w,&m->h);return rc;}
MODE(SDL_GetCurrentDisplayMode)
MODE(SDL_GetDesktopDisplayMode)
void SDL_GL_SwapWindow(void *window) {
 void(*real)(void*)=dlsym(RTLD_NEXT,"SDL_GL_SwapWindow");State*s=current();if(!s){real(window);return;}
 internal++;
 I draw,read,vp[4],program,array,buffer,active,tex,sampler;B mask[4];
 U caps[]={0x0be2,0x0b71,0x0b90,0x0b44,0x0c11,0x8c89};B enabled[6];
 r_glGetIntegerv(0x8ca6,&draw);r_glGetIntegerv(0x8caa,&read);r_glGetIntegerv(0x0ba2,vp);r_glGetIntegerv(0x8b8d,&program);
 r_glGetIntegerv(0x85b5,&array);r_glGetIntegerv(0x8894,&buffer);r_glGetIntegerv(0x84e0,&active);r_glGetBooleanv(0x0c23,mask);
 for(int i=0;i<6;i++){enabled[i]=r_glIsEnabled(caps[i]);r_glDisable(caps[i]);}
 r_glActiveTexture(0x84c0);r_glGetIntegerv(0x8069,&tex);r_glGetIntegerv(0x8919,&sampler);
 void(*bindsampler)(U,U)=proc("glBindSampler");bindsampler(0,0);
 r_glBindFramebuffer(0x8d40,0);r_glViewport(0,0,720,960);r_glColorMask(1,1,1,1);
 r_glUseProgram(s->program);r_glBindVertexArray(s->vao);r_glBindTexture(0x0de1,s->tex);r_glDrawArrays(0x0005,0,4);
 real(window);
 r_glBindFramebuffer(0x8ca9,draw);r_glBindFramebuffer(0x8ca8,read);r_glViewport(vp[0],vp[1],vp[2],vp[3]);
 r_glUseProgram(program);r_glBindVertexArray(array);r_glBindBuffer(0x8892,buffer);r_glBindTexture(0x0de1,tex);bindsampler(0,sampler);r_glActiveTexture(active);
 r_glColorMask(mask[0],mask[1],mask[2],mask[3]);for(int i=0;i<6;i++)if(enabled[i])r_glEnable(caps[i]);
 internal--;
}
