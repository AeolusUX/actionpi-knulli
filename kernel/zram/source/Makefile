obj-m += zram.o zsmalloc.o lzo.o lzo-rle.o lzo_compress.o
zram-y := zcomp.o zram_drv.o
lzo_compress-y := lzo1x_compress.o
ccflags-y += -g -DCONFIG_ZSMALLOC_MODULE=1 -DCONFIG_CRYPTO_LZO_MODULE=1 -DCONFIG_LZO_COMPRESS_MODULE=1
ccflags-y += -include $(src)/actionpi_zram_config.h
