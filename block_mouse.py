import fcntl
import struct
import os
import time

INPUT_DEVICE = "/dev/input/event3"
OUTPUT_DEVICE = "/dev/uinput"

EVIOCGRAB = 1074021776


def main():
    device = INPUT_DEVICE
    input_format = "llHHI"
    event_size = struct.calcsize(input_format)
    inputfd = open(device, "rb")
    outputfd = open(OUTPUT_DEVICE, "wb")
    fcntl.ioctl(inputfd, EVIOCGRAB, True)
    ignored_codes = ["1198", "1199"]
    forwarded_events = {}

    while True:
        now = time.time()
        event = inputfd.read(event_size)

        if event in forwarded_events:
            del(forwarded_events[event])
            continue

        (tv_sec, tv_usec, event_type, code, value) = struct.unpack(input_format, event)
        print("code: %s  value: %s" % (code, value))
        if code not in ignored_codes:
            forwarded_events[event] = now
            outputfd.write(event)
        else:
            print('ignoring code %s' % code)


if __name__ == "__main__":
    main()
