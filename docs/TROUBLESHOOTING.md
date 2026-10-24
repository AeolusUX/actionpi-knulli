# Troubleshooting

[English](TROUBLESHOOTING.md) · [한국어](TROUBLESHOOTING.ko.md)

## First installation restarts twice

A black screen after the boot image is normal during first installation. Allow
about 5 minutes and keep the power on: the device will automatically restart once
or twice before the menu appears. There is no need to worry during this setup.
SHARE expansion and the S12 settings installer account for these restarts; normal
game launches and exits do not require a reboot.

## Wi-Fi is off or PortMaster cannot download

The public defaults deliberately disable Wi-Fi and omit your saved network.
Enable Wi-Fi and enter the SSID/password in the normal settings. Install
PortMaster through the Ports installer. The distribution does not preinstall a
private copy of its downloaded application data.

## PSP exit / HOME

Use SELECT+START held for about one second. PPSSPP HOME exit is disabled after a
quit hang/fallback regression. RetroArch HOME works. Do not diagnose absent
PPSSPP HOME handling as a missing input driver.

## PortMaster sideways after an update

Its launcher selects a private PySDL2 DLL, not a system-wide SDL replacement.
The emulator dispatch preparation reapplies the known launcher setting after
installation/update. If upstream changes that shell format, report the launcher
version and error, rather than globally replacing SDL. Other ports' renderer
paths were not universally tested by this correction.

## Black screen or legacy graphics mode

Use a verified image and a known-good card first. Check whether Mali recovery was
requested or an automatic attempt failed; a fallback menu will not offer the
normal Vulkan path. For recovery, create an empty `DISABLE_MALI.txt` in BOOT and
restart. Keep recovery backups from the same image. Do not mix old trial scripts,
an unrelated Mali module and current configuration.

## Brightness direction changes

The final fix normalizes actual hardware polarity at boot and wake. Do not add
another numerical inversion. Useful narrow evidence is the PWM-normalize log,
runtime PWM arguments and whether the problem appears after cold boot or resume.
Remove SSIDs, passwords, MACs and other private details from reports before posting.

## Reporting a problem

Include release filename/checksum, device model, the emulator/backend, exact
trigger, whether it occurs before/after suspend, and whether the menu recovers.
Do not upload your whole private settings directory or game files.
