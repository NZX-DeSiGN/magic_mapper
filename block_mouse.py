import fcntl
import struct
import os
import time

INPUT_DEVICE = "/dev/input/event3"


EVIOCGRAB = 1074021776


def main():
    device = INPUT_DEVICE
    input_format = "llHHI"
    event_size = struct.calcsize(input_format)
    device_handle = open(device, "rb")
    fcntl.ioctl(device_handle, EVIOCGRAB, True)
    ignored_codes = ["1198", "1199"]
    forwarded_events = {}

    while True:
        now = time.time()
        event = device_handle.read(event_size)

        if event in forwarded_events:
            del(forwarded_events[event])
            continue

        (tv_sec, tv_usec, event_type, code, value) = struct.unpack(input_format, event)
        print("code: %s  value: %s" % (code, value))
        if code not in ignored_codes:
            forwarded_events[event] = now
            fcntl.ioctl(device_handle, EVIOCGRAB, False)
            send_input_event(device, event)
            fcntl.ioctl(device_handle, EVIOCGRAB, True)
        else:
            print('ignoring code %s' % code)


def send_input_event(device, event):
    """ Send the event back to the input device """
    out_file = os.open(device, os.O_RDWR)
    os.write(out_file, event)
    os.close(out_file)


if __name__ == "__main__":
    main()
