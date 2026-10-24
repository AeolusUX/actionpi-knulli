# Installing and checking the public release

The release asset is XZ-compressed to avoid shipping gigabytes of empty card
space. The unpacked image remains 6,069,178,368 bytes. Removing files from a disk
image does not automatically shrink its partition layout; compression represents
the cleared free space efficiently.

1. Download `.img.xz` and `SHA256SUMS` from the same GitHub Release.
2. Verify the compressed checksum. On Linux use `sha256sum -c SHA256SUMS` with
   the downloaded assets present; on Windows use `Get-FileHash -Algorithm SHA256`.
3. Use a flashing program that accepts XZ, or extract the IMG first.
4. Write the whole SD card, then insert it into the Action Pi and power on.
5. Allow first-install expansion and settings restoration to complete. Each has
   its own reboot. A black interval during installation is expected.
6. Add your games/needed additional BIOS. Enable Wi-Fi and enter your network
   details when downloads are needed.

Raw image SHA256:
`322efb6a52025372ef3c063fc840e6e296b4ff2a93860132a18ac578a4783842`.
The public manifest and binary component hashes are in `release/`.

The source tree is stored in Git; the large firmware belongs in Releases.
[GitHub's release documentation](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)
sets a limit of less than 2GiB per individual asset. The compressed image is
checked against that limit before uploading. No personal stable IMG is uploaded.

The normal updater path for arbitrary upstream firmware is not validated by this
adaptation. Keep a backup before experimenting with a different kernel/rootfs;
matching a version number does not establish that the recorded guards still apply.

