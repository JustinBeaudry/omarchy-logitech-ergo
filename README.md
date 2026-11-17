# Logitech ERGO K860 for Omarchy

Small, reversible keyboard integration for [Omarchy](https://omarchy.org/).
No root daemon, key interception, or replacement of your personal bindings.

## What this fixes

The K860 can remember a **Mac layout** even when connected to Linux. Its lock
key in **PC mode** sends **Super+L**, which Omarchy normally uses to cycle
workspace layouts—not lock the screen.

This project provides:

- Optional hardware setup through [Solaar](https://pwr-solaar.github.io/Solaar/):
  PC/Linux layout and shortcut functions without holding Fn.
- A managed Lua mapping: **Super+L → lock screen**.
- An idempotent installer, backups, validation, rollback on configuration errors,
  and an uninstaller that preserves unrelated settings.

**Scope:** tested with an ERGO K860 over a Unifying receiver on Omarchy 4.5.0-3
and Hyprland 0.56.2. The lock mapping was confirmed on the physical keyboard.
Bluetooth, other Logitech keyboards, and older `.conf`-based Omarchy releases
are not tested/supported by this installer. This is a community project, not
an official Logitech or Omarchy integration.

## Install

Requires Git, Python 3.10+, and Omarchy's Lua configuration
(`~/.config/hypr/bindings.lua`, with the `o.rebind` helper).
Run as your normal desktop user, **not root**.

```sh
git clone https://github.com/JustinBeaudry/omarchy-logitech-ergo.git
cd omarchy-logitech-ergo
# Review the script before running it.
./omarchy-logitech-ergo install
```

This changes **Super+L globally**, not only on the K860. It replaces Omarchy's
“Cycle workspace layout” binding. **Super+Alt+L** still cycles layouts backward;
**Super+Ctrl+L** remains another lock shortcut. Other existing bindings are left
alone. If you have already customized Super+L, review this tradeoff first.

### Optional: set the keyboard to Linux/PC mode

Install Solaar using Omarchy's package command (this may prompt for sudo):

```sh
omarchy pkg add solaar
solaar show
./omarchy-logitech-ergo configure-keyboard
```

The keyboard must be awake and connected. If access is denied after installing
Solaar's udev rules, reconnect the receiver or log out and back in. Do not make
hidraw devices world-writable or run the GUI as root.

The command sets Solaar's `multiplatform` option to `Windows`—the appropriate
PC layout for Linux—and `fn-swap` to `on`. Thus the printed shortcuts work
without Fn; **Fn+F1–F12** produces normal function keys. PC mode can also change
the positions/meaning of modifier keys compared with Mac mode.

With multiple keyboards, select one explicitly:

```sh
./omarchy-logitech-ergo configure-keyboard --device YOUR_DEVICE_SERIAL
```

Hardware configuration is separate from installing the Lua mapping. It is not
transactional: if the second setting fails, the first may already be applied.
Use `solaar config 'ERGO K860'` to inspect the current settings. No Solaar
background process is required for the lock mapping. If hardware settings do
not survive a reconnect on your setup, rerun the command or use Solaar's own
startup support; this project does not install an autostart entry.

## Mapping status

| Key | Behavior / status |
| --- | --- |
| Lock | Super+L → `omarchy system lock`; physically confirmed |
| Brightness, volume, mute, previous/play/next | Existing Omarchy media bindings; not overridden here |
| Calculator | Existing Omarchy `XF86Calculator` binding; not overridden here |
| Screenshot | Existing Omarchy `Print` binding; actual emitted chord may depend on keyboard mode |
| Task view, app switching, show desktop, search | Not mapped by this project yet; need observed key events |
| Easy-Switch 1/2/3 | Hardware host selection; unchanged |

Some shortcut keys worked during initial testing, but this is **not** a claim
that every media/screenshot/calculator key has been individually verified.
Please report your connection type, versions, printed key label, and emitted
key/chord when proposing another mapping. For example, `wev` (if installed)
can show Wayland key events for keys not consumed by the compositor. Do not
share full typing traces or sensitive input.

## Files, backups, and removal

The installer appends a clearly marked `require("logitech-ergo")` block to
`~/.config/hypr/bindings.lua` and creates `~/.config/hypr/logitech-ergo.lua`.
It backs up existing files under
`~/.config/omarchy-logitech-ergo/backups/<UTC timestamp>/` before changes.
It refuses to overwrite a custom module or symlinked config files.

By default it runs `hyprctl reload` and `hyprctl configerrors`. If validation
fails, it restores the files from before that invocation and reloads again.
Existing Hyprland errors must be fixed before installation. The desktop may
briefly observe intermediate file changes because Hyprland watches its config.

```sh
./omarchy-logitech-ergo uninstall
```

Uninstall removes only the managed loader/module, preserving subsequent edits
to your other bindings. It does not restore the whole backup, uninstall Solaar,
or change keyboard hardware settings. Omarchy's default Super+L binding returns
on reload unless you have another personal override.

To undo the optional hardware setup, use your **previous** values, for example:

```sh
# Only if these were your previous/preferred settings:
solaar config 'ERGO K860' multiplatform MacOS
solaar config 'ERGO K860' fn-swap off
```

For offline/staged configuration:

```sh
./omarchy-logitech-ergo install --config-home /path/to/config --no-reload
```

`--config-home` defaults to `$XDG_CONFIG_HOME` or `~/.config`. Use `--no-reload`
when editing a configuration other than the one loaded by your current session.

## Update and contribute

```sh
git pull --ff-only
./omarchy-logitech-ergo install
python3 -m unittest discover -s tests -v
```

The installer deliberately refuses to replace a locally modified managed module;
move that customization into your personal bindings, or back it up and remove
it before reinstalling. Prefer small, documented, opt-in mappings over silently
reassigning existing Omarchy shortcuts. Open an issue for keys still missing.

## License

MIT.
