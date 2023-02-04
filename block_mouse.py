import fcntl
import struct
import os
import time

INPUT_DEVICE = "/dev/input/event3"
OUTPUT_DEVICE = "/dev/uinput"

EVIOCGRAB = 1074021776

UI_SET_EVBIT = 0x40045564
UI_SET_KEYBIT = 0x40045565


def main():
    device = INPUT_DEVICE
    input_format = "llHHI"
    event_size = struct.calcsize(input_format)
    inputfd = open(device, "rb")
    fcntl.ioctl(inputfd, EVIOCGRAB, True)
    ignored_codes = []

    # Open the virtual input device
    uinput = os.open("/dev/uinput", os.O_WRONLY | os.O_NONBLOCK)

    # Set the type of events to generate
    os.ioctl(uinput, UI_SET_EVBIT, struct.pack("I", 0x01))
    os.ioctl(uinput, UI_SET_KEYBIT, struct.pack("I", 1))

    # Enable the virtual input device
    os.write(uinput, struct.pack("16sHHi", "Virtual Input", 0, 0, 0))

    while True:
        event = inputfd.read(event_size)

        (tv_sec, tv_usec, event_type, code, value) = struct.unpack(input_format, event)
        print("code: %s  value: %s" % (code, value))
        if code not in ignored_codes:
            os.write(uinput, struct.pack("iihhi", tv_sec, tv_usec, event_type, code, value))


if __name__ == "__main__":
    main()
