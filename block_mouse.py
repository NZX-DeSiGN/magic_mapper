import os
import struct
import fcntl

INPUT_DEVICE = "/dev/input/event3"
UINPUT_DEVICE = "/dev/uinput"
EVIOCGRAB = 1074021776

# List of input codes to filter out
FILTERED_CODES = [1, 2, 3]
INPUT_FORMAT = "llHHi"


def read_input_event(input_device):
    with open(input_device, "rb", buffering=0) as f:
        # set the input device to exclusive mode
        fcntl.ioctl(f, EVIOCGRAB, 1)
        while True:
            event = f.read(struct.calcsize(INPUT_FORMAT))
            if event:
                (tv_sec, tv_usec, type, code, value) = struct.unpack(INPUT_FORMAT, event)
                print(code)
                # filter out the input codes in FILTERED_CODES
                if code not in FILTERED_CODES:
                    yield event


def write_input_event(input_event, uinput_device):
    return
    with open(uinput_device, "wb") as f:
        f.write(input_event)


if __name__ == "__main__":
    for event in read_input_event(INPUT_DEVICE):
        write_input_event(event, UINPUT_DEVICE)
