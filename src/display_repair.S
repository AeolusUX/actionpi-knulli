.section .text.logo,"ax"
.global repaired_logo
repaired_logo:
 paciasp
 sub sp, sp, #80
 stp x29, x30, [sp, #32]
 add x29, sp, #32
 stp x19, x20, [sp, #48]
 str x21, [sp, #64]
 mov x19, x0
 mov x20, x1
 stp xzr, xzr, [sp]
 stp wzr, wzr, [sp, #16]
 mov x1, sp
 add x2, sp, #16
 add x3, sp, #20
 bl logo_getter
 cbnz w0, .Llogo_out
 ldp w1, w2, [sp, #4]
 cbz w1, .Linvalid
 cbz w2, .Linvalid
 ldp w3, w4, [sp, #16]
 cbz w3, .Linvalid
 cbz w4, .Linvalid
 ldr w5, [sp]
 ldr w6, [sp, #12]
 cmp w6, #32
 cset w6, ne
 cmp w5, #0
 csel w6, wzr, w6, eq
 adrp x21, config
 add x21, x21, :lo12:config
 str x19, [x21]
 stp w6, w1, [x21, #8]
 stp w2, w3, [x21, #16]
 str w4, [x21, #24]
 stp x5, xzr, [x21, #32]
 mov x6, #0x100000001
 str x6, [x21, #48]
 mov x0, x21
 mov x1, x20
 bl fb_core_init
 b .Llogo_out
.Linvalid:
 mov w0, #-22
.Llogo_out:
 ldr x21, [sp, #64]
 ldp x19, x20, [sp, #48]
 ldp x29, x30, [sp, #32]
 add sp, sp, #80
 autiasp
 ret

.section .text.exit,"ax"
.global repaired_exit
repaired_exit:
 paciasp
 stp x29, x30, [sp, #-32]!
 mov x29, sp
 str x19, [sp, #16]
 adrp x19, fb_global
 ldr x0, [x19, :lo12:fb_global]
 cbz x0, .Lexit_out
 bl unregister_framebuffer
 ldr x0, [x19, :lo12:fb_global]
 ldr x1, [x0, #840]
 bl cleanup_entry
 ldr x0, [x19, :lo12:fb_global]
 str xzr, [x19, :lo12:fb_global]
 bl framebuffer_release
.Lexit_out:
 ldr x19, [sp, #16]
 ldp x29, x30, [sp], #32
 autiasp
 mov w0, #0
 ret

/* Only the sunxi client initialized with funcs=NULL. Caller guarantees that
 * registration succeeded and the containing object has not yet been freed. */
.section .text.cleanup,"ax"
.global repaired_cleanup
repaired_cleanup:
 paciasp
 stp x29, x30, [sp, #-32]!
 mov x29, sp
 stp x19, x20, [sp, #16]
 add x19, x1, #0x40
 ldr x0, [x19]
 add x20, x0, #0x100
 mov x0, x20
 bl mutex_lock
 add x0, x19, #0x10
 ldp x1, x2, [x0]
 str x2, [x1, #8]
 str x1, [x2]
 stp x0, x0, [x0]
 mov x0, x19
 bl drm_client_release
 mov x0, x20
 bl mutex_unlock
 ldp x19, x20, [sp, #16]
 ldp x29, x30, [sp], #32
 autiasp
 ret
