import subprocess

file_name = "/home/esteb/.config/qtile/screen_modes.txt"
pos_second_screen = "0x1000"
wallpaper_path = "/home/esteb/images/wallpapers/gradient5.jpg"

def get_wallpaper_path():
    return wallpaper_path

def get_info_screens(file_dir):
    xranr_result = subprocess.getoutput('xrandr | grep -A 1 " connected"').split('\n')
    parsed_results = [info.split() for info in xranr_result if info != '--']

    screens_data = []

    def get_max_hz(device_info):
        max_hz = 0
        for elem in device_info:
            clean_elem = elem.replace('*', '').replace('+', '')
            try:
                act_hz = float(clean_elem)
                max_hz = act_hz if act_hz > max_hz else max_hz
            except ValueError:
                continue
        return str(max_hz)

    for i in range(0, len(parsed_results), 2):
        device = parsed_results[i][0]
        device_info = parsed_results[i+1]
        max_res = device_info[0]
        max_freq = get_max_hz(device_info[1:])
        info_needed = {
            "device": device,
            "max_res": max_res,
            "max_hz": max_freq
        }
        screens_data.append(info_needed)

    n_screen_modes = len(screens_data) 
    screen_commands = {}

    first_screen = screens_data[0]

    if n_screen_modes > 1:
        second_screen = screens_data[1]

        screen_commands["just_first_screen"] = f"xrandr --output {first_screen["device"]} --mode {first_screen["max_res"]} --rate {first_screen["max_hz"]} --primary --output {second_screen["device"]} --off"
        screen_commands["just_second_screen"] = f"xrandr --output {second_screen["device"]} --mode {second_screen["max_res"]} --rate {second_screen["max_hz"]} --primary --output {first_screen["device"]} --off" 
        screen_commands["extend_screens"] = f"xrandr --output {first_screen["device"]} --primary --mode {first_screen["max_res"]} --pos 0x1247 --rotate normal --output {second_screen["device"]} --mode {second_screen["max_res"]} --rate {second_screen["max_hz"]} --rotate normal --output DP-1 --off --output DP-2 --off"

        subprocess.Popen(f"{screen_commands["just_second_screen"]}", shell=True)
    else:
        screen_commands["one_screen"] = f"xrandr --output {first_screen["device"]} --mode {first_screen["max_res"]} --rate {first_screen["max_hz"]}"
    
    with open(file_dir, "w") as screen_modes:
        for key in screen_commands.keys():
            screen_mode = screen_commands[key]
            screen_modes.write(f"{screen_mode}\n")
        actual_mode = 0 if (n_screen_modes == 1) else 1
        screen_modes.write(f"{actual_mode}")

def change_screen_mode():
    with open(file_name, "r+") as screen_modes:
        file_lines = screen_modes.readlines()
        modes = file_lines[:-1]
        actual_mode = file_lines[-1]
        # update the screen mode
        next_mode = (int(actual_mode) + 1) % len(modes)
        print(f"actual mode = {next_mode}")
        file_lines[-1] = str(next_mode)
        screen_modes.seek(0)
        screen_modes.writelines(file_lines)
        
        subprocess.Popen(f"{modes[next_mode][:-1]}", shell=True)
        subprocess.Popen(f"feh --bg-fill {wallpaper_path}", shell=True)

def get_screen_mode(file_dir):
    with open(file_name, "r") as screen_modes:
        actual_mode = screen_modes.readlines()[-1]
        return int(actual_mode)
