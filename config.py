from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys

from libqtile import bar, hook, layout, qtile
from libqtile.config import Click, Drag, Group, Key, Match, Screen
from libqtile.lazy import lazy
from qtile_extras import widget
from qtile_extras.widget.decorations import GradientDecoration, PowerLineDecoration, RectDecoration

import utils

@dataclass(frozen=True)
class Paths:
    base: Path
    home: Path
    assets: Path
    screen_modes_file: Path
    alacritty_config: Path
    xmodmap: Path
    thesis_path: Path


@dataclass(frozen=True)
class Palette:
    bg_primary: str
    bg_dark: str
    fg_white: str
    accent_cyan: str
    accent_green: str
    accent_pink: str
    battery_ok: str
    battery_low: str
    bg_windows_number: str
    bg_windows_name: str
    bg_groupbox: str
    bg_volume: str
    bg_battery: str
    bg_calendar: str
    ssd: str
    ssd_border: str
    ram: str
    ram_border: str
    cpu: str
    cpu_border: str
    network: str
    network_border: str


@dataclass(frozen=True)
class BottomBarProfile:
    screen_number: int
    height: int
    fontsize: int
    fontsize_diff: int
    groupbox_padding_x: int
    groupbox_padding_y: int
    groupbox_margin: int
    cpu_width: int
    ram_width: int
    ssd_width: int
    use_window_name_widget: bool
    width_window_name_widget: int

@dataclass(frozen=True)
class ScreenProfile:
    bottom: BottomBarProfile


@dataclass(frozen=True)
class InfoBlockStyle:
    background: str
    text: str
    graph: str
    border: str


PATHS = Paths(
    base=Path(__file__).resolve().parent,
    home=Path.home(),
    assets=Path(__file__).resolve().parent / "assets",
    screen_modes_file=Path(__file__).resolve().parent / "screen_modes.txt",
    alacritty_config=Path.home() / ".config" / "alacritty",
    xmodmap=Path.home() / ".Xmodmap",
    thesis_path=Path.home() / "Documentos" / "Memoria" / "tt-repo",
)

COLORS = Palette(
    bg_primary="#01020f",
    bg_dark="#000000",
    fg_white="#ffffff",
    accent_cyan="#00D5FF",
    accent_green="#3B8514",
    accent_pink="#7E2C42",
    battery_ok="#83FA69",
    battery_low="#C22121",
    bg_windows_name="#834370",
    bg_windows_number="#164549",
    bg_groupbox="#000000",
    bg_volume="#6F5CA0",
    bg_battery="#256C58",
    bg_calendar="#0B3676",
    ssd="#FFCB00",
    ssd_border="#D1AF26",
    ram="#1FA674",
    ram_border="#1FA674",
    cpu="#CC2727",
    cpu_border="#851600",
    network="#88B8F2",
    network_border="#175ABF",
)

KEYBIND_MOD = "mod4"
WINDOW_GROW_AMOUNT = 80
VOLUME_STEP = 1
BRIGHTNESS_STEP = "5%"
GROUP_NAMES = "123456"

VOLUME_GET_COMMAND = "pamixer --get-volume-human"
VOLUME_MUTE_CHECK_COMMAND = "pamixer --get-mute"
VOLUME_UPDATE_INTERVAL = 0.03

BLOCK_SEPARATOR_PATH = "arrow_left"
BLOCK_SEPARATOR_SIZE = 13
BLOCK_SEPARATOR_SHIFT = 0
BLOCK_SEPARATOR_MARGIN_LEFT = 13
BLOCK_SEPARATOR_MARGIN_RIGHT = 13
STICKY_WINDOWS = []

INFO_BLOCK_STYLES: dict[str, InfoBlockStyle] = {
    "ssd": InfoBlockStyle(
        background="#463604",
        text=COLORS.ssd,
        graph=COLORS.ssd,
        border=COLORS.ssd_border,
    ),
    "ram": InfoBlockStyle(
        background="#042218",
        text=COLORS.ram,
        graph="#00FFA0",
        border=COLORS.ram_border,
    ),
    "cpu": InfoBlockStyle(
        background="#260808",
        text=COLORS.cpu,
        graph=COLORS.cpu,
        border=COLORS.cpu_border,
    ),
    "network": InfoBlockStyle(
        background="#0A1C33",
        text=COLORS.network,
        graph=COLORS.network,
        border=COLORS.network_border,
    ),
    "clock": InfoBlockStyle(
        background="#12152A",
        text=COLORS.fg_white,
        graph=COLORS.fg_white,
        border=COLORS.bg_dark,
    ),
}

SCREEN_PROFILES = {
    0: ScreenProfile(
        bottom=BottomBarProfile(
            screen_number=0,
            height=30,
            fontsize=17,
            fontsize_diff=0,
            groupbox_padding_x=15,
            groupbox_padding_y=4,
            groupbox_margin=2,
            cpu_width=70,
            ram_width=50,
            ssd_width=70,
            use_window_name_widget=False,
            width_window_name_widget=0,
        ),
    ),
    1: ScreenProfile(
        bottom=BottomBarProfile(
            # ------------------------------- #
            # values for 2560p x 1440p external monitor            
            height=27,
            fontsize=14,
            groupbox_padding_x=16,
            groupbox_padding_y=4,
            use_window_name_widget=True,
            width_window_name_widget=510,
            # ------------------------------- #
            # values for 5120p x 1440p external monitor
            #width_window_name_widget=2960,
            # ------------------------------- #
            # values for 1080p external monitor            
            #height=25,
            #fontsize=13,
            #groupbox_padding_x=11,
            #groupbox_padding_y=2.5,
            #use_window_name_widget=False,
            # ------------------------------- #
            screen_number=1,
            fontsize_diff=0,
            groupbox_margin=2,
            cpu_width=60,
            ram_width=50,
            ssd_width=60,            
        ),
    ),
}

def asset_path(*parts):
    return str(PATHS.assets.joinpath(*parts))

def alacritty_command(config_name):
    return f"alacritty --config-file {PATHS.alacritty_config / config_name}"

def alacritty_command_thesis(config_name):
    return f"alacritty --config-file {PATHS.alacritty_config / config_name} -e bash -lc 'cd {PATHS.thesis_path} && make shell-clear'"


def separator_forward_slash_path(size, right_margin):
    total_size = size + right_margin
    slash_tip = size / total_size
    return [(0, 0), (slash_tip, 0), (0, 1)]

def separator_arrow_left_path(size, right_margin):
    total_size = size + right_margin
    tip_x = size / total_size
    return [(0, 0), (tip_x, 0.5), (0, 1)]

def separator_arrow_right_path(size, right_margin):
    total_size = size + right_margin
    tip_x = size / total_size
    return [(0, 0), (tip_x, 0), (0, 0.5), (tip_x, 1), (0, 1)]

def create_block_separator(separator_path=BLOCK_SEPARATOR_PATH) -> list[PowerLineDecoration]:
    match separator_path:
        case "forward_slash":
            separator_path = separator_forward_slash_path(BLOCK_SEPARATOR_SIZE, BLOCK_SEPARATOR_MARGIN_RIGHT)
        case "arrow_left":
            separator_path = separator_arrow_left_path(BLOCK_SEPARATOR_SIZE, BLOCK_SEPARATOR_MARGIN_RIGHT)
        case "arrow_right":
            separator_path = separator_arrow_right_path(BLOCK_SEPARATOR_SIZE, BLOCK_SEPARATOR_MARGIN_RIGHT)

    return [
        PowerLineDecoration(
            path=separator_path,
            size=BLOCK_SEPARATOR_SIZE + BLOCK_SEPARATOR_MARGIN_RIGHT,
            shift=BLOCK_SEPARATOR_SHIFT,
            extrawidth=BLOCK_SEPARATOR_MARGIN_LEFT,
        )
    ]

def signal_icon(filename: str, background: str):
    return widget.Image(
        filename=asset_path("signal-icons", filename),
        margin_y=3,
        background=background,
    )


def sync_group_fullscreen(group, fullscreen: bool) -> None:
    for window in group.windows:
        window.fullscreen = fullscreen


@hook.subscribe.startup_once
def init_function() -> None:
    utils.get_info_screens(str(PATHS.screen_modes_file))
    subprocess.Popen(["feh", "--bg-fill", utils.get_wallpaper_path()])
    subprocess.Popen(["picom"])
    subprocess.Popen(["xmodmap", str(PATHS.xmodmap)])


@hook.subscribe.client_managed
def set_fullscreen_for_max_layout(window) -> None:
    if window.group and window.group.layout.name == "max":
        window.fullscreen = True


@hook.subscribe.layout_change
def on_layout_change(current_layout, group) -> None:
    sync_group_fullscreen(group, current_layout.name == "max")

@lazy.function
def float_to_front(qtile):
    for window in STICKY_WINDOWS:
        window.bring_to_front()

@lazy.function
def toggle_sticky(qtile):
    window = qtile.current_window
    if window.floating:
        if window in STICKY_WINDOWS:
            STICKY_WINDOWS.remove(window)
        else:
            STICKY_WINDOWS.append(window)

@hook.subscribe.setgroup
def move_sticky_windows():
    for window in STICKY_WINDOWS:
        window.togroup(qtile.current_group.name)
        window.bring_to_front()
    qtile.current_group.windows[0].focus()

mod = KEYBIND_MOD
grow_window = WINDOW_GROW_AMOUNT


def create_keys() -> list[Key]:
    keys_navigation = [
        Key([mod], "left", lazy.layout.left(), desc="Move focus to left"),
        Key([mod], "right", lazy.layout.right(), desc="Move focus to right"),
        Key([mod], "down", lazy.layout.down(), desc="Move focus down"),
        Key([mod], "up", lazy.layout.up(), desc="Move focus up"),
    ]

    keys_window_management = [
        Key([mod, "control"], "left", lazy.layout.grow_width(-grow_window), desc="Shrink window width"),
        Key([mod, "control"], "right", lazy.layout.grow_width(grow_window), desc="Grow window width"),
        Key([mod, "control"], "down", lazy.layout.grow_height(-grow_window), desc="Shrink window height"),
        Key([mod, "control"], "up", lazy.layout.grow_height(grow_window), desc="Grow window height"),
        Key([mod, "shift"], "left", lazy.layout.integrate_left(), desc="Integrate window left"),
        Key([mod, "shift"], "right", lazy.layout.integrate_right(), desc="Integrate window right"),
        Key([mod, "shift"], "down", lazy.layout.move_down(), desc="Move window down"),
        Key([mod, "shift"], "up", lazy.layout.move_up(), desc="Move window up"),
        Key([mod], "apostrophe", lazy.layout.mode_horizontal_split(), desc="Horizontal split mode"),
        Key([mod], "plus", lazy.layout.mode_horizontal_split(), desc="Horizontal split mode"),
        Key([mod], "numbersign", lazy.layout.mode_vertical_split(), desc="Vertical split mode"),
        Key([mod], "braceright", lazy.layout.mode_vertical_split(), desc="Vertical split mode"),
        Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
        Key([mod], "q", lazy.window.kill(), desc="Kill focused window"),
        Key([mod], "f", lazy.window.toggle_fullscreen(), desc="Toggle fullscreen on the focused window"),
        Key([mod, "shift"], "h", lazy.window.togroup("hidden"), desc="Send window to hidden group"),
        Key([mod, "control"], "h", lazy.group["hidden"].toscreen(), desc="Move window to hidden group"),
        Key([mod, "control", "shift"], "Left", lazy.screen.prev_group(), desc="Move window to previous group"),
        Key([mod, "control", "shift"], "Right", lazy.screen.next_group(), desc="Move window to next group"),
        Key([mod, "shift"], "f", float_to_front(), desc="Bring floating window to front"),
        Key([mod, "control"], "f", toggle_sticky(), desc="Toggle sticky window"),
    ]

    keys_terminals = [
        Key([mod], "Return", lazy.spawn(alacritty_command_thesis("alacritty0.toml")), desc="Launch container shell terminal for thesis"),
        Key([mod], "BackSpace", lazy.spawn(alacritty_command("alacritty0.toml")), desc="Launch terminal"),
        Key([mod], "questiondown", lazy.spawn(alacritty_command("alacritty_mini.toml")), desc="Launch minimal terminal"),
        Key([mod], "equal", lazy.spawn(alacritty_command("alacritty_mini.toml")), desc="Launch minimal terminal"),
    ]

    keys_screen = [
        Key([mod], "s", lazy.next_screen(), desc="Change between screens"),
        Key([mod], "a", lazy.window.toscreen(0), desc="Move window to screen 0"),
        Key([mod], "d", lazy.window.toscreen(1), desc="Move window to screen 1"),
        Key([mod, "control"], "m", lazy.spawn(f"{sys.executable} {PATHS.base / 'change_screen_mode.py'}"), desc="Change the screens mode"),
        Key([mod, "shift"], "m", lazy.spawn(f"{sys.executable} {PATHS.base / 'get_info_screens.py'}"), desc="Update the screens modes file"),
    ]

    keys_media = [
        Key([mod], "comma", lazy.spawn(f"pamixer -d {VOLUME_STEP}"), desc="Reduce volume"),
        Key([mod], "period", lazy.spawn(f"pamixer -i {VOLUME_STEP}"), desc="Increase volume"),
        Key([mod], "m", lazy.spawn("pamixer -t"), desc="Mute the volume"),
        Key([mod, "control"], "j", lazy.spawn("playerctl previous"), desc="Previous track"),
        Key([mod, "control"], "k", lazy.spawn("playerctl play-pause"), desc="Play or pause track"),
        Key([mod, "control"], "l", lazy.spawn("playerctl next"), desc="Next track"),
        Key([mod], "End", lazy.spawn(f"brightnessctl s {BRIGHTNESS_STEP}-"), desc="Reduce brightness"),
        Key([mod], "Home", lazy.spawn(f"brightnessctl s +{BRIGHTNESS_STEP}"), desc="Increase brightness"),
        Key([mod], "h", lazy.spawn("flameshot gui"), desc="Take a screenshot"),
    ]

    keys_official_keys = [
        Key([], "XF86AudioLowerVolume", lazy.spawn(f"pamixer -d {VOLUME_STEP}"), desc="Reduce volume"),
        Key([], "XF86AudioRaiseVolume", lazy.spawn(f"pamixer -i {VOLUME_STEP}"), desc="Increase volume"),
        Key([], "XF86AudioMute", lazy.spawn("pamixer -t"), desc="Mute the volume"),
        Key([], "XF86AudioPrev", lazy.spawn("playerctl previous"), desc="Previous track"),
        Key([], "XF86AudioPlay", lazy.spawn("playerctl play-pause"), desc="Play or pause track"),
        Key([], "XF86AudioNext", lazy.spawn("playerctl next"), desc="Next track"),
        Key([], "XF86MonBrightnessDown", lazy.spawn(f"brightnessctl s {BRIGHTNESS_STEP}-"), desc="Reduce brightness"),
        Key([], "XF86MonBrightnessUp", lazy.spawn(f"brightnessctl s +{BRIGHTNESS_STEP}"), desc="Increase brightness"),
    ]

    keys_applications = [
        Key([mod], "c", lazy.spawn("code"), desc="Open VSCode"),
        Key([mod], "v", lazy.spawn("vesktop"), desc="Open Discord"),
        Key([mod], "z", lazy.spawn(f"code {PATHS.base / 'config.py'}"), desc="Open Qtile config file"),
        Key([mod], "p", lazy.spawn("zen-browser"), desc="Open Firefox browser"),
        Key([mod], "u", lazy.spawn("zen-browser -new-window https://www.u-cursos.cl/"), desc="Open U-Cursos"),
        Key([mod], "y", lazy.spawn("zen-browser -new-window https://www.youtube.com/"), desc="Open YouTube"),
        Key([mod], "n", lazy.spawn("thunar"), desc="Open file manager"),
        Key([mod], "l", lazy.spawn("rofi -show drun"), desc="Open application launcher"),
        Key([mod], "j", lazy.spawn("rofimoji"), desc="Open emoji selector"),
        Key([mod], "i", lazy.spawn("mirage"), desc="Open image viewer"),
        Key([mod], "t", lazy.spawn("sioyek"), desc="Open PDF viewer"),
        Key([mod], "x", lazy.spawn("spotify"), desc="Open Spotify"),
    ]

    keys_keyboard = [
        Key([mod], "space", lazy.spawn(f"xmodmap {PATHS.xmodmap}"), desc="Set English keyboard"),
        Key([mod, "control"], "space", lazy.spawn("setxkbmap latam"), desc="Set Latin American keyboard"),
    ]

    keys_system = [
        Key([mod, "control"], "t", lazy.spawn(f"code {PATHS.home / 'Documentos/FCFM/DCC/6to_Semestre/token.txt'}"), desc="Show GIT Tokens"),
        Key([mod, "control"], "r", lazy.reload_config(), desc="Reload the config"),
        Key([mod, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
    ]

    keys = (
        keys_navigation
        + keys_window_management
        + keys_terminals
        + keys_screen
        + keys_media
        + keys_official_keys
        + keys_applications
        + keys_keyboard
        + keys_system
    )

    for vt in range(1, 8):
        keys.append(
            Key(
                ["control", "mod1"],
                f"f{vt}",
                lazy.core.change_vt(vt).when(func=lambda: qtile.core.name == "wayland"),
                desc=f"Switch to VT{vt}",
            )
        )

    for group_name in GROUP_NAMES:
        keys.extend(
            [
                Key([mod], group_name, lazy.group[group_name].toscreen(), desc=f"Switch to group {group_name}"),
                Key(
                    [mod, "shift"],
                    group_name,
                    lazy.window.togroup(group_name, switch_group=True),
                    desc=f"Switch to and move focused window to group {group_name}",
                ),
            ]
        )

    return keys


keys = create_keys()
groups = [Group(name) for name in GROUP_NAMES]
groups.append(Group("hidden"))

layouts = [
    layout.Plasma(
        border_focus=COLORS.fg_white,
        border_width=2,
        margin=7,
        fair=True,
    ),
    layout.Max(
        border_width=0,
        margin=0,
    ),
]

widget_defaults = {
    "font": "Cascadia Code Semi-Bold",
}

def create_bottom_bar(profile: BottomBarProfile) -> bar.Bar:
    ssd_style = INFO_BLOCK_STYLES["ssd"]
    ram_style = INFO_BLOCK_STYLES["ram"]
    cpu_style = INFO_BLOCK_STYLES["cpu"]
    network_style = INFO_BLOCK_STYLES["network"]
    clock_style = INFO_BLOCK_STYLES["clock"]

    return bar.Bar(
        [
            widget.Spacer(length=10, background=COLORS.bg_windows_number),
            widget.CurrentScreen(
                fmt="{}",
                active_text="●",
                inactive_text="●",
                fontsize=profile.fontsize + 5,
                active_color="#25FF00",
                inactive_color="#000000",
                background=COLORS.bg_windows_number,
                decorations=create_block_separator("arrow_right"),
            ),
            widget.GroupBox(
                visible_groups=list(GROUP_NAMES),
                highlight_method="block",
                this_screen_border=COLORS.accent_green,
                other_current_screen_border=COLORS.accent_pink,
                this_current_screen_border=COLORS.accent_green,
                other_screen_border=COLORS.accent_pink,
                active=COLORS.fg_white,
                inactive=COLORS.bg_dark,
                center_aligned=True,
                padding_x=profile.groupbox_padding_x,
                padding_y=profile.groupbox_padding_y,
                margin=profile.groupbox_margin,
                fontsize=profile.fontsize + profile.fontsize_diff,
                font="Cascadia Code Bold",
                spacing=-1,
                background=COLORS.bg_groupbox,
                rounded=True,
                decorations=create_block_separator()
            ),
            *(
                [widget.WindowName(
                    fontsize=profile.fontsize - profile.fontsize_diff,
                    font="Noto Sans CJK SC Bold",
                    background=COLORS.bg_windows_name,
                    decorations=create_block_separator(),
                    width=profile.width_window_name_widget,
                )] if profile.use_window_name_widget else []
            ),
            signal_icon("ssd.png", ssd_style.background),
            widget.HDD(
                device="nvme0n1",
                fontsize=profile.fontsize - profile.fontsize_diff,
                format="SSD {HDDPercent}%",
                foreground=ssd_style.text,
                background=ssd_style.background,
            ),
            widget.HDDBusyGraph(
                device="nvme0n1",
                border_color=ssd_style.border,
                border_width=1.5,
                frequency=0.5,
                graph_color=ssd_style.graph,
                line_width=0,
                samples=100,
                type="box",
                width=profile.ssd_width,
                background=ssd_style.background,
                decorations=create_block_separator(),
            ),
            signal_icon("ram.png", ram_style.background),
            widget.Memory(
                format="{SwapUsed:.2f}GB/{SwapTotal:.2f}GB",
                measure_swap="G",
                fontsize=profile.fontsize - profile.fontsize_diff,
                foreground=ram_style.text,
                background=ram_style.background,
            ),
            widget.SwapGraph(
                fontsize=profile.fontsize,
                border_color=ram_style.border,
                border_width=1.5,
                frequency=0.5,
                graph_color=ram_style.graph,
                samples=100,
                type="box",
                width=profile.ram_width,
                background=ram_style.background,
            ),
            widget.Memory(
                format="{MemUsed:.2f}GB/{MemTotal:.2f}GB",
                measure_mem="G",
                fontsize=profile.fontsize - profile.fontsize_diff,
                foreground=ram_style.text,
                background=ram_style.background,
            ),
            widget.MemoryGraph(
                fontsize=profile.fontsize,
                border_color=ram_style.border,
                border_width=1.5,
                frequency=0.5,
                graph_color=ram_style.graph,
                samples=100,
                type="box",
                width=profile.ram_width,
                background=ram_style.background,
                decorations=create_block_separator(),
            ),
            signal_icon("cpu.png", cpu_style.background),
            widget.CPU(
                format="CPU {freq_current}GHz {load_percent:>4}%",
                fontsize=profile.fontsize - profile.fontsize_diff,
                foreground=cpu_style.text,
                background=cpu_style.background,
            ),
            widget.CPUGraph(
                fontsize=profile.fontsize,
                border_color=cpu_style.border,
                border_width=2,
                frequency=0.5,
                graph_color=cpu_style.graph,
                samples=100,
                type="box",
                width=profile.cpu_width,
                background=cpu_style.background,
                decorations=create_block_separator(),
            ),
            signal_icon("signal.png", network_style.background),
            widget.Wlan(
                interface="wlan0",
                format="{essid} {percent:2.0%}",
                update_interval=0.5,
                fontsize=profile.fontsize,
                disconnected_message="✈︎ ✈︎ ✈︎",
                foreground=network_style.text,
                background=network_style.background,
                decorations=create_block_separator(),
            ),

            widget.Volume(
                theme_path=asset_path("volume-icons"),
                check_mute_command=VOLUME_MUTE_CHECK_COMMAND,
                check_mute_string="true",
                update_interval=VOLUME_UPDATE_INTERVAL,
                background=COLORS.bg_volume,
                size=10,
            ),
            widget.Volume(
                fontsize=profile.fontsize,
                get_volume_command=VOLUME_GET_COMMAND,
                update_interval=VOLUME_UPDATE_INTERVAL,
                background=COLORS.bg_volume,
                unmute_format="{volume:>2}%",
                mute_format="{volume:>2}%",
                decorations=create_block_separator(),
            ),
            widget.BatteryIcon(
                theme_path=asset_path("battery-icons"),
                update_interval=0.2,
                background=COLORS.bg_battery,
            ),
            widget.Battery(
                format="{percent:2.0%}",
                fontsize=profile.fontsize,
                update_interval=0.2,
                show_short_text=False,
                foreground=COLORS.battery_ok,
                low_foreground=COLORS.battery_low,
                low_percentage=0.15,
                notify_below=5,
                notification_timeout=5,
                background=COLORS.bg_battery,
                decorations=create_block_separator(),
            ),
            widget.Image(
                filename=asset_path("signal-icons", "calendar.png"),
                background=COLORS.bg_calendar,
                margin_y=3,
            ),
            widget.Clock(
                format="%d/%m/%Y",
                fontsize=profile.fontsize,
                foreground=COLORS.accent_cyan,
                background=COLORS.bg_calendar,
                decorations=create_block_separator()
            ),
            widget.AnalogueClock(
                face_shape="circle",
                margin=4,
                adjust_y=1,
                background=clock_style.background,
            ),
            widget.Clock(
                format="%H:%M:%S %p",
                fontsize=profile.fontsize,
                foreground=clock_style.text,
                background=clock_style.background,
            ),
            widget.Spacer(length=100, background=clock_style.background),
        ],
        size=profile.height,
        background="#00000000",
        border_width=[0, 0, 20, 0],
        border_color=[COLORS.bg_primary, COLORS.bg_dark, COLORS.bg_primary, COLORS.bg_dark],
        margin=[22, 50, -40, 50],
    )


def build_screen(profile: ScreenProfile) -> Screen:
    return Screen(bottom=create_bottom_bar(profile.bottom))


def build_screens(actual_mode: int) -> list[Screen]:
    screen_modes = [
        [build_screen(SCREEN_PROFILES[0])],
        [build_screen(SCREEN_PROFILES[1])],
        [
            build_screen(SCREEN_PROFILES[0]), 
            build_screen(SCREEN_PROFILES[1])
        ],
    ]
    if 0 <= actual_mode < len(screen_modes):
        return screen_modes[actual_mode]
    return screen_modes[0]


actual_screen_mode = utils.get_screen_mode(str(PATHS.screen_modes_file))
screens = build_screens(actual_screen_mode)

mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(), start=lazy.window.get_position()),
    Drag([], "Button9", lazy.window.set_position_floating(), start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()),
    Click([mod], "Button2", float_to_front()),
    Click([], "Button8", float_to_front()),
]

dgroups_key_binder = None
dgroups_app_rules = []
follow_mouse_focus = True
bring_front_click = False
floats_kept_above = True
cursor_warp = False
floating_layout = layout.Floating(
    border_width=1,
    border_focus="#FFFFFF",
    border_normal="#1f2430",
    float_rules=[
        *layout.Floating.default_float_rules,
        Match(wm_class="zen", title="Picture-in-Picture"),
        Match(wm_class="confirmreset"),
        Match(wm_class="makebranch"),
        Match(wm_class="maketag"),
        Match(wm_class="ssh-askpass"),
        Match(title="branchdialog"),
        Match(title="pinentry"),
    ]
)
auto_fullscreen = False
focus_on_window_activation = "smart"
reconfigure_screens = True
auto_minimize = True
wl_input_rules = None
wl_xcursor_theme = None
wl_xcursor_size = 24
wmname = "LG3D"
