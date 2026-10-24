#define _GNU_SOURCE
#include <dlfcn.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
extern void actionpi_brightness_written(void);

/* Direct raw30->raw130 was visibly brighter. Never invert this panel's values.
 * Observe ES writes only to arm the missing brightness slider hold repeat. */
static int panel_fd(int fd) {
 static int is_es=-1;
 if(is_es<0){char exe[512];ssize_t k=readlink("/proc/self/exe",exe,sizeof(exe)-1);if(k<0)return 0;exe[k]=0;const char *base=strrchr(exe,'/');is_es=base&&!strcmp(base+1,"emulationstation");}
 if(!is_es)return 0; /* Child utilities already use the corrected common tool. */
 char p[64],target[512];snprintf(p,sizeof(p),"/proc/self/fd/%d",fd);
 ssize_t n=readlink(p,target,sizeof(target)-1);if(n<0)return 0;target[n]=0;
 const char *suffix="/backlight/backlight0/brightness";size_t len=strlen(suffix);
 int match=(size_t)n>=len&&!strcmp(target+n-len,suffix);
 return match;
}
static int panel_number(const void *buf,size_t count) {
 if(!count||count>16)return 0;
 char text[32];memcpy(text,buf,count);text[count]=0;char *end;
 long value=strtol(text,&end,10);
 return end!=text&&(!*end||!strcmp(end,"\n"))&&value>=0&&value<=167;
}
ssize_t write(int fd,const void *buf,size_t count) {
 static __thread ssize_t(*real)(int,const void*,size_t);if(!real)real=dlsym(RTLD_NEXT,"write");
 int panel=panel_number(buf,count)&&panel_fd(fd);
 ssize_t result=real(fd,buf,count);
 if(panel&&result==(ssize_t)count)actionpi_brightness_written();
 return result;
}
size_t fwrite(const void *buf,size_t size,size_t count,FILE *stream) {
 static __thread size_t(*real)(const void*,size_t,size_t,FILE*);if(!real)real=dlsym(RTLD_NEXT,"fwrite");
 int panel=size&&count<=16/size&&panel_number(buf,size*count)&&panel_fd(fileno(stream));
 size_t result=real(buf,size,count,stream);
 if(panel&&result==count)actionpi_brightness_written();
 return result;
}
