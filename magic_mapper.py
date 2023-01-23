import time
import os
import struct
import subprocess
import json
import fcntl

BUTTONS = {
    398: "red",
    399: "green",
    400: "yellow",
    401: "blue",
    402: "ch_up",
    403: "ch_down",
    115: "vol_up",
    114: "vol_down",
    207: "play",
    119: "pause",
    2: "1",
    3: "2",
    4: "3",
    5: "4",
    6: "5",
    7: "6",
    8: "7",
    9: "8",
    10: "9",
    11: "0",
    1038: "prime",
    1037: "netflix",
    1042: "disney",
    1043: "lg_channels",
    1086: "alexa",
    1117: "google",
}

INPUT_DEVICE = "/dev/input/event3"
IGNORED_CODES = [0, 1, 1198, 1199]


def cycle_energy_mode(inputs):
    """cycle energy modes between min med max off"""
    modes = ["max", "med", "min", "off"]
    if inputs.get("reverse_order"):
        modes.reverse()
    current_mode = get_picture_settings()["settings"]["energySaving"]

    if current_mode in modes:
        next_mode = modes.index(current_mode) + 1
    else:  # It's probably in auto mode so just start at the first mode
        next_mode = 0

    if next_mode >= len(modes):
        next_mode = 0

    inputs["mode"] = modes[next_mode]
    set_energy_mode(inputs)


def toggle_eye_comfort(inputs):
    """Toggle the eye comfort mode aka reduce blue light"""
    current_mode = get_picture_settings()["settings"]["eyeComfortMode"]
    print("current eye comfort mode: current_mode %s" % current_mode)
    if current_mode == "off":
        new_mode = "on"
    else:
        new_mode = "off"
    endpoint = "luna://com.webos.settingsservice/setSystemSettings"
    payload = {"category": "picture", "settings": {"eyeComfortMode": new_mode}}
    luna_send(endpoint, payload)
    if inputs.get("notifications"):
        show_message("Reduce blue light mode: %s" % new_mode)


def screen_off(inputs):
    """Turns the screen off, but not the TV itself.
    Press any button but power and vol to turn it back on.
    """
    endpoint = "luna://com.webos.service.tvpower/power/turnOffScreen"
    payload = {}
    luna_send(endpoint, payload)


def set_energy_mode(inputs):
    """Sets the energy savings mode
    Valid values: min med max off auto screen_off
    screen_off may not work on some models, best to use the screen_off function instead
    """
    mode = inputs["mode"]
    endpoint = "luna://com.webos.settingsservice/setSystemSettings"
    payload = {"category": "picture", "settings": {"energySaving": mode}}
    luna_send(endpoint, payload)
    if inputs.get("notifications"):
        show_message("Energy mode: %s" % mode)


def increase_oled_light(inputs):
    increment_oled_light(inputs, direction="up")


def reduce_oled_light(inputs):
    increment_oled_light(inputs, direction="down")


def set_oled_backlight(inputs):
    backlight = inputs["backlight"]
    endpoint = "luna://com.webos.settingsservice/setSystemSettings"
    payload = {"category": "picture", "settings": {"backlight": backlight}}
    luna_send(endpoint, payload)
    if inputs.get("notifications"):
        show_message("OLED Backlight: %s" % backlight)


def launch_app(inputs):
    """Launch an app by app_id
    Inputs: app_id  - Use list_apps.py to get the app_id
    """
    app_id = inputs["app_id"]
    endpoint = "luna://com.webos.service.applicationmanager/launch"
    payload = {"id": app_id}
    luna_send(endpoint, payload)


def send_ir_command(inputs):
    """Send an IR command to a configured device
    This relies on you using the device connection manager to setup your IR device (ie a soundbar)
    Once setup you can use this function to have the remote send IR commands
    """
    tv_input = inputs["tv_input"]  # "OPTICAL", other inputs untested
    keycode = inputs["keycode"]  # "IR_KEY_VOLUP" "IR_KEY_POWER"
    device_type = inputs["device_type"]  # "audio"

    endpoint = "luna://com.webos.service.irdbmanager/sendIrCommand"
    payload = {
        "keyCode": keycode,
        "buttonState": "single",
        "connectedInput": tv_input,
        "deviceType": device_type,
    }
    luna_send(endpoint, payload)


def curl(inputs):
    """Execute the system curl binary with the provided inputs
    Note this script has to work on Python 2.7 and 3.x, and very
    few Python libraries are included in WebOS, so we'll just
    keep it simple and use the system curl binary vs urllib.
    """

    url = inputs.get("url")
    if not url:
        print("ERROR: curl function called but url not supplied")

    method = inputs.get("method", "GET").upper()

    command_string = "curl -vs -X %s" % method
    command = command_string.split()

    headers = inputs.get("headers")
    if headers:
        if type(headers) == list:
            for header in headers:
                command.append("-H")
                command.append(header)
        elif type(headers) != str:  # Python 2.7 on the C9 returns unicode instead of str
            headers = str(headers)
            command.append("-H")
            command.append(headers)

    data = inputs.get("data")
    if data:
        command.append("-d")
        command.append(data)

    command.append(url)
    print("Running curl command: %s" % " ".join(command))

    try:
        output = subprocess.check_output(command)
    except subprocess.CalledProcessError as error:
        print("WARNING: curl command failed")
        print(error)
        return

    return output


def press_button(inputs):
    """Simulate a button press on the remote
    This is useful to simulate the play and pause buttons for remotes that don't have these buttons
    Inputs: button_name (str)
    """
    button = inputs["button"]
    keycode = get_keycode(button)
    print("Simulating keystroke with button '%s' (keycode %s)" % (button, keycode))
    send_keystroke(INPUT_DEVICE, keycode)


###################################
# Private Functions
# The fuctions below here should not be called by magic_mapper_config.json
####################################


def get_button_map():
    """Read the json config file"""
    config_path = os.path.join(os.path.dirname(__file__), "magic_mapper_config.json")
    with open(config_path) as config_file:
        button_map = json.load(config_file)
    return button_map


def fire_event(code, button_map):
    """Execute the function configured for the button"""
    button_name = BUTTONS[code]
    if button_name not in button_map:
        print("Button %s not configured in magic_mapper_config.json " % button_name)
        return

    print("firing event for code: %s button: %s" % (code, button_name))
    func_name = button_map[button_name]["function"]
    print("func_name: %s" % func_name)
    inputs = button_map[button_name].get("inputs", {})
    globals()[func_name](inputs)


def luna_send(endpoint, payload):
    # Execute luna send and return the output

    command = ["/usr/bin/luna-send", "-n", "1"]
    command.append(endpoint)
    command.append(json.dumps(payload))
    print("running command: %s" % command)
    output = subprocess.check_output(command)
    return output


def increment_oled_light(inputs, direction):
    increment = inputs.get("increment", 10)
    current_value = int(get_picture_settings()["settings"]["backlight"])

    if direction == "up":
        new_value = current_value + increment
        if new_value > 100:
            new_value = 100
    elif direction == "down":
        new_value = current_value - increment
        if new_value < 0:
            new_value = 0

    inputs["backlight"] = new_value
    set_oled_backlight(inputs)


def get_picture_settings():
    # Return the current settings
    endpoint = "luna://com.webos.settingsservice/getSystemSettings"
    payload = {"category": "picture"}
    output = luna_send(endpoint, payload)
    settings = json.loads(output)
    return settings


def show_message(message):
    """Shows a "toast" message"""
    endpoint = "luna://com.webos.notification/createToast"
    payload = {"message": message}
    luna_send(endpoint, payload)


def get_keycode(button):
    """Returns the keycode associated with the button name"""
    keys = [k for k, v in BUTTONS.items() if v == button]
    return keys[0]


def send_keystroke(device, keycode):
    """Send a keystroke to the input device
        We use this to simulate button presses like play/pause since those require special handling
        Use the press_button function for magic_mapper_config.py
    };
    """
    send_input_event(device, keycode, 1, 1)
    send_input_event(device, 0, 0, 0)
    send_input_event(device, keycode, 0, 1)
    send_input_event(device, 0, 0, 0)


def send_input_event(device, keycode, value, event_type):
    """Low level function to write to the input device file
    Don't call this from magic_mapper_config.json
    """
    input_format = "llHHI"

    out_file = os.open(device, os.O_RDWR)
    now = time.time()
    tv_sec = int(now)
    tv_usec = int((now - tv_sec) * 1000000)

    data = [tv_sec, tv_usec, event_type, keycode, value]
    print("writing: %s" % data)

    event = struct.pack(input_format, *data)
    os.write(out_file, event)
    os.close(out_file)


def input_loop(button_map):
    # Read from the input device
    # https://stackoverflow.com/a/16682549/866057
    device = INPUT_DEVICE
    input_format = "llHHI"
    event_size = struct.calcsize(input_format)
    device_handle = open(device, "rb")

    buttons_waiting = {}

    while True:
        event = device_handle.read(event_size)
        (tv_sec, tv_usec, type, code, value) = struct.unpack(input_format, event)
        # print("debug code_wait: %s - code: %s - value: %s" % (code_wait, code, value))
        now = time.time()

        if code in IGNORED_CODES:
            continue

        # Button Down
        if value == 1:
            if code in buttons_waiting and now - buttons_waiting[code] < 1.0:
                print("WARNING: Got code %s DOWN while waiting for UP" % code)
            buttons_waiting[code] = now
            if code in BUTTONS:
                print("%s button down" % BUTTONS[code])
            continue

        # Button Up
        if value == 0:
            if code not in buttons_waiting:
                print("WARNING: Got code %s UP with no DOWN" % code)
                continue
            elif code not in BUTTONS:
                print("Unknown button pressed. (code=%s)" % code)
            elif now - buttons_waiting[code] > 1.0:
                print("Ignoring long press of %s" % BUTTONS[code])
            else:
                print("%s button up" % BUTTONS[code])
                fire_event(code, button_map)
            del(buttons_waiting[code])


def main():
    """MAIN"""

    button_map = get_button_map()
    input_loop(button_map=button_map)


if __name__ == "__main__":
    main()
