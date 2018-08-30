import signal
import glob
import logging
import argparse
import time
import sys
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('dirwatcher.log')
formatter = logging.Formatter(
    "%(asctime)s:%(levelname)s:%(threadName)s:%(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

checked_files = {}


def receive_signal(signum, stack):
    """Logs Interrupt and Termination signals"""
    if signum == 2:
        logger.info("Program terminated upon user request")
        sys.exit(0)
    if signum == 15:
        logger.exception("Program terminated!")


def check_magic(file):
    """Opens a file and reads each line looking for the magic word"""
    magic_word = "SHAZAM"
    with open(file) as f:
        for i, line in enumerate(f.readlines()):
            if magic_word in line and i not in checked_files[file]:
                logger.info(
                    "{} found at line {} in {}".format(magic_word, i+1, file))
                checked_files[file].append(i)


def main():
    parser = argparse.ArgumentParser(
        description="Monitor a directory for created text files")
    parser.add_argument('dir', help="Directory to be monitored")

    args = parser.parse_args()

    logger.info("Program searching in {}".format(args.dir))

    try:
        os.chdir(args.dir)
    except Exception:
        logger.exception("Directory not found")
        print "\nDirectory not found!\n"
        sys.exit(0)

    signal.signal(signal.SIGINT, receive_signal)
    signal.signal(signal.SIGTERM, receive_signal)

    while True:
        text_files = glob.glob(args.dir + "*.txt")
        if len(text_files) > len(checked_files):
            for file in text_files:
                if file not in checked_files:
                    logger.info(" {} found in {}".format(file, args.dir))
                    checked_files[file] = []
        elif len(text_files) < len(checked_files):
            for file in checked_files:
                if file not in text_files:
                    logger.info(" {} removed from {}".format(file, args.dir))
                    checked_files.pop(file, None)
        for file in text_files:
            check_magic(file)
        time.sleep(.5)


if __name__ == '__main__':
        main()
