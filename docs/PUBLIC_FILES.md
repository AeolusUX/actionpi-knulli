# Public file boundaries

[English](PUBLIC_FILES.md) · [한국어](PUBLIC_FILES.ko.md)

Published code is staged using an explicit allowlist from the **public distribution**.
The original private working directory and complete conversation are not uploaded.

## Included

- Curated development history with confirmed outcomes and failed approaches.
- Current startup/session/opacity/rotation/input/power helpers.
- Exact upstream Mali driver source at the pinned commit, with original notices.
- Recovered kernel config and candidate config/options, source cleanup patch,
  guarded assembly repair and verification summary.
- Historical image conversion and PWM tools, identified as historical where they
  require unpublished earlier input images.
- Sanitized public defaults, PortMaster installer entry, release manifest,
  component hashes, final image/checksum and a compressed release asset.
- Build, installation, recovery, test-coverage and source/provenance documentation.

## Excluded

- Personal v115/v119/v120 images, the private BIOS archive and private captures.
- Saved personal Wi-Fi SSIDs/passwords and recovery copies containing them.
- GitHub credentials, browser session material, authentication screenshots,
  known-hosts files and SSH private/host keys.
- Raw user conversations, private network logs, machine IDs, cookies, histories,
  Bluetooth pairing records, game captures, diagnostic memory dumps and game ROMs.
- Compiler installations, Git databases and untracked build artifacts from the
  driver working tree.

The source image's base rootfs and its original BIOS were deliberately retained
unchanged. This is distinct from excluding the additional personal BIOS archive.
The public packaging zeroed 3,289,493,504 free FAT bytes and scrubbed 122 file
tails plus 26 deleted records, so removing a filename was not the only cleanup.

The downloadable IMG belongs in GitHub **Releases**, not the Git source history.
The source tree is small enough to inspect and clone without downloading firmware.
