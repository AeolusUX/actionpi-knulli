# Installing and checking the public release

[English](RELEASE.md) · [한국어](RELEASE.ko.md)

The release asset is XZ-compressed to avoid shipping gigabytes of empty card
space. The unpacked image remains 6,069,178,368 bytes. Removing files from a disk
image does not automatically shrink its partition layout; compression represents
the cleared free space efficiently.

1. Download `.img.xz` and `SHA256SUMS` from the same GitHub Release.
2. Verify the compressed checksum. On Linux use `sha256sum -c SHA256SUMS` with
   the downloaded assets present; on Windows use `Get-FileHash -Algorithm SHA256`.
3. Use a flashing program that accepts XZ, or extract the IMG first.
4. Write the whole SD card, then insert it into the Action Pi and power on.
5. **On first installation, a black screen after the boot image is normal. Allow
   about 5 minutes: SHARE expansion and settings installation will automatically
   restart the device once or twice before the menu appears. There is no need to
   worry; keep the power on and wait for setup to finish.**
6. Add your games/needed additional BIOS. Enable Wi-Fi and enter your network
   details when downloads are needed.

Raw image SHA256:
`18cfbf89a81dd4245caee0d557e8b12bf00c8627e01d81b7b2ac28b210143cc9`.
The public manifest and binary component hashes are in `release/`.

The source tree is stored in Git; the large firmware belongs in Releases.
[GitHub's release documentation](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)
sets a limit of less than 2GiB per individual asset. The compressed image is
checked against that limit before uploading. No personal stable IMG is uploaded.
`tools/verify-release.py` also verifies XZ integrity and the unpacked IMG SHA256
while recording the compressed asset SHA256 in the same streaming pass.

The normal updater path for arbitrary upstream firmware is not validated by this
adaptation. Keep a backup before experimenting with a different kernel/rootfs;
matching a version number does not establish that the recorded guards still apply.

