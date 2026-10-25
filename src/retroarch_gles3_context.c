/* SPDX-License-Identifier: MIT
 * Loaded only by ordinary RetroArch sessions, before app_output_rotation.so.
 * Upgrade SDL's GLES2 request before window/config creation so the existing
 * GLES3 rotation adapter can rotate both software-core frames and Ozone.
 */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdlib.h>
#include <string.h>

int SDL_GL_SetAttribute(int attribute, int value)
{
    int (*next)(int, int) = dlsym(RTLD_NEXT, "SDL_GL_SetAttribute");
    const char *enabled = getenv("ACTIONPI_RA_GLES3_CONTEXT");
    if (!next)
        return -1;
    /* SDL_GL_CONTEXT_MAJOR_VERSION = 17. Minor/profile/flags are preserved. */
    if (enabled && !strcmp(enabled, "1") && attribute == 17 && value > 0 && value < 3)
        value = 3;
    return next(attribute, value);
}
