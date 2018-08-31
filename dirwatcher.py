import signal
import logging
import argparse
import time
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('dirwatcher.log')
formatter = logging.Formatter(
    "%(asctime)s:%(levelname)s:%(threadName)s:%(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

checked_files = {}
running_flag = True


def receive_signal(signum, stack):
    """Logs Interrupt and Termination signals"""
    logger.warning("Received signal: {}".format(signum))
    global running_flag
    if signum == signal.SIGINT:
        running_flag = False
    if signum == signal.SIGTERM:
        running_flag = False


def check_magic(file, directory):
    """Opens a file and reads each line looking for the magic word"""
    magic_word = "SHAZAM"
    with open(directory + "/" + file) as f:
        for i, line in enumerate(f.readlines()):
            if magic_word in line and i not in checked_files[file]:
                logger.info(
                    "{} found at line {} in {}".format(magic_word, i+1, file))
                checked_files[file].append(i)


def dir_watcher_loop(args):
        directory = os.path.abspath(args.dir)
        text_files = [f for f in os.listdir(directory) if ".txt" in f]
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
            check_magic(file, directory)


def main():
    start_time = time.time()
    parser = argparse.ArgumentParser(
        description="Monitor a directory for created text files")
    parser.add_argument('dir', help="Directory to be monitored")

    args = parser.parse_args()

    logger.info("Program searching in {}".format(args.dir))

    signal.signal(signal.SIGINT, receive_signal)
    signal.signal(signal.SIGTERM, receive_signal)

    while running_flag:
        try:
            dir_watcher_loop(args)
            time.sleep(2)
        except Exception:
            logger.exception("Unhandled exception!")
    logger.info("Program uptime: {} seconds".format(time.time() - start_time))


if __name__ == '__main__':
        main()
