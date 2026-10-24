#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <stdint.h>
#include <time.h>

/* Some ES builds stop updating the selected slider. Repeat only a held
 * horizontal hat that actually wrote this panel's brightness. Native repeat
 * writes reset the timer, so a working slider is never accelerated. */
static unsigned char held_hat[56];
static int hat_down, brightness_armed;
static uint64_t held_since, panel_changed;
static uint64_t milliseconds(void) {
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return (uint64_t)t.tv_sec * 1000 + t.tv_nsec / 1000000;
}
void actionpi_brightness_written(void) {
    if (hat_down) {
        panel_changed = milliseconds();
        brightness_armed = 1;
    }
}
static int slider_event(void *event, int received) {
    if (!event) return received;
    uint64_t now = milliseconds();
    if (received) {
        uint32_t kind; memcpy(&kind, event, sizeof(kind));
        /* SDL_JoyHatEvent: which at8, hat at12, value at13. */
        if (kind == 0x602) {
            unsigned char value = ((unsigned char *)event)[13];
            hat_down = value == 2 || value == 8;
            brightness_armed = 0;
            if (hat_down) { memcpy(held_hat, event, 56); held_since = now; }
        } else if (kind == 0x100 || (kind >= 0x300 && kind <= 0x401) ||
                   (kind >= 0x603 && kind <= 0x607)) {
            hat_down = brightness_armed = 0;
        }
        return received;
    }
    if (hat_down && brightness_armed && now - held_since >= 650 &&
        now - held_since < 10000 && now - panel_changed >= 80) {
        memcpy(event, held_hat, 56);
        panel_changed = now;
        return 1;
    }
    return received;
}

/* SDL2 ARM64 SDL_Event is 56 bytes. No window dimensions or rendering changes. */
static int quit_sent;
static int request_quit(void *event) {
    const char *path = getenv("ACTIONPI_MENU_STOP");
    if (!event || quit_sent || !path || access(path, F_OK)) return 0;
    memset(event, 0, 56);
    *(unsigned int *)event = 0x100; /* SDL_QUIT */
    quit_sent = 1;
    fprintf(stderr, "MALI_MENU_AUDIT SDL_QUIT injected\n");
    return 1;
}
int SDL_PollEvent(void *event) {
    int (*fn)(void *) = dlsym(RTLD_NEXT, "SDL_PollEvent");
    return request_quit(event) ? 1 : slider_event(event, fn(event));
}
int SDL_WaitEventTimeout(void *event, int ms) {
    int (*fn)(void *, int) = dlsym(RTLD_NEXT, "SDL_WaitEventTimeout");
    if (request_quit(event)) return 1;
    if (hat_down && brightness_armed && (ms < 0 || ms > 40)) ms = 40;
    return slider_event(event, fn(event, ms));
}
void *SDL_GL_CreateContext(void *window) {
    void *(*fn)(void *) = dlsym(RTLD_NEXT, "SDL_GL_CreateContext");
    void *ctx = fn(window);
    const unsigned char *(*get_string)(unsigned int) = dlsym(RTLD_DEFAULT, "glGetString");
    fprintf(stderr, "MALI_MENU_AUDIT context=%p\n", ctx);
    if (ctx && get_string) {
        for (unsigned int id=0x1F00; id<=0x1F02; id++) {
            const unsigned char *s = get_string(id);
            fprintf(stderr, "MALI_MENU_AUDIT GL_%x=%s\n", id, s ? (const char *)s : "(null)");
        }
    }
    return ctx;
}
void SDL_GL_DeleteContext(void *ctx) {
    void (*fn)(void *) = dlsym(RTLD_NEXT, "SDL_GL_DeleteContext");
    fprintf(stderr, "MALI_MENU_AUDIT DeleteContext begin\n");
    fn(ctx);
    fprintf(stderr, "MALI_MENU_AUDIT DeleteContext end\n");
}
void SDL_DestroyWindow(void *window) {
    void (*fn)(void *) = dlsym(RTLD_NEXT, "SDL_DestroyWindow");
    fprintf(stderr, "MALI_MENU_AUDIT DestroyWindow begin\n");
    fn(window);
    fprintf(stderr, "MALI_MENU_AUDIT DestroyWindow end\n");
}
void SDL_Quit(void) {
    void (*fn)(void) = dlsym(RTLD_NEXT, "SDL_Quit");
    fprintf(stderr, "MALI_MENU_AUDIT SDL_Quit begin\n");
    fn();
    fprintf(stderr, "MALI_MENU_AUDIT SDL_Quit end\n");
}
