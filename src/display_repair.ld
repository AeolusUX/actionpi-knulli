OUTPUT_ARCH(aarch64)
logo_getter = 0x772e50;
config = 0x1650698;
fb_global = 0x1650668;
fb_core_init = 0x7774d4;
unregister_framebuffer = 0x4264b0;
framebuffer_release = 0x4295e0;
cleanup_entry = 0x777ff4;
mutex_lock = 0xc26c90;
mutex_unlock = 0xc26460;
drm_client_release = 0x4e6de4;
SECTIONS {
 .text.logo 0x7777d0 : { *(.text.logo) }
 .text.exit 0x7778a4 : { *(.text.exit) }
 .text.cleanup 0x7778f0 : { *(.text.cleanup) }
 /DISCARD/ : { *(.comment) *(.note*) *(.text) *(.data) *(.bss) }
}
ASSERT(SIZEOF(.text.logo) <= 0xd4, "logo replacement exceeds original function")
ASSERT(SIZEOF(.text.exit) <= 0x4c, "exit replacement exceeds original function")
ASSERT(SIZEOF(.text.cleanup) <= 0x60, "cleanup exceeds original debug-only callback")
