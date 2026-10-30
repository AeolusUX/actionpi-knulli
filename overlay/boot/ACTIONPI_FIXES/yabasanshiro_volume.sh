#!/bin/sh
# Action Pi standalone: preserve volume instead of doubling/halving on launch.
[ "$3" = "yabasanshiro" ] || exit 0
case "$1" in
    gameStart)
        current="$(knulli-audio getSystemVolume 2>/dev/null)"
        saved="$(knulli-settings-get audio.volume 2>/dev/null)"
        # Restore a persisted nonzero choice only if the transient sink is zero.
        # A deliberately saved zero remains muted.
        if [ "$current" = "0" ]; then
            case "$saved" in ''|*[!0-9]*) ;; *)
                if [ "$saved" -gt 0 ] && [ "$saved" -le 100 ]; then
                    knulli-audio setSystemVolume "$saved" >/dev/null 2>&1
                fi ;;
            esac
        fi
        ;;
    gameStop)
        # Keep the user's game volume; undo only the legacy temporary boost cap.
        knulli-settings-set audio.volume.boost 100 >/dev/null 2>&1
        ;;
esac
exit 0
