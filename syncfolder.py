import os
import shutil
import time
import argparse
import logging

def setup_logging(log_file):

    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Set the level to DEBUG to capture all messages

    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # Set formatter for both handlers
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

def sync_folders(source_folder, replica_folder):

    logging.debug(f"Starting synchronization from {source_folder} to {replica_folder}")

    # Copy files and folders from source to replica
    for root, dirs, files in os.walk(source_folder):
        logging.debug(f"Visiting folder: {root}")

        # Find the relative path to maintain the same structure in the replica
        relative_path = os.path.relpath(root, source_folder)
        replica_root = os.path.join(replica_folder, relative_path)

        # If the directory doesn't exist in the replica, create it
        if not os.path.exists(replica_root):
            os.makedirs(replica_root)
            logging.info(f"Created folder: {replica_root}")

        # Copy files from source to replica
        for file in files:
            source_file = os.path.join(root, file)  # Full path of the file in the source folder
            replica_file = os.path.join(replica_root, file)  # Where it should go in the replica folder

            # If the file doesn't exist in the replica, copy it
            if not os.path.exists(replica_file):
                shutil.copy2(source_file, replica_file)  # Copy the file
                logging.info(f"Copied file: {replica_file}")
            else:
                logging.debug(f"File already exists in replica: {replica_file}")

    # Remove files and folders from the replica that are not in the source
    for root, dirs, files in os.walk(replica_folder):
        logging.debug(f"Visiting replica folder: {root}")
        relative_path = os.path.relpath(root, replica_folder)
        source_root = os.path.join(source_folder, relative_path)

        # If a folder in the replica does not exist in the source, delete it
        if not os.path.exists(source_root):
            shutil.rmtree(root)  # Remove the entire folder
            logging.info(f"Removed folder: {root}")
            continue

        # Remove files from the replica if they do not exist in the source
        for file in files:
            replica_file = os.path.join(root, file)
            source_file = os.path.join(source_root, file)

            if not os.path.exists(source_file):
                os.remove(replica_file)  # Remove the file
                logging.info(f"Removed file: {replica_file}")
            else:
                logging.debug(f"File exists in source: {source_file}")

def main():
    # Get the paths and interval from the command line
    parser = argparse.ArgumentParser(description="Simple folder synchronization tool with logging.")
    parser.add_argument("source", help="Path to the source folder.")
    parser.add_argument("replica", help="Path to the replica folder.")
    parser.add_argument("interval", type=int, help="Time interval in seconds between syncs.")
    parser.add_argument("logfile", help="Path to the log file where operations will be recorded.")
    args = parser.parse_args()

    # Set up logging to a directory you have permission to write to
    log_file = args.logfile
    if not os.path.isabs(log_file):  # Check if the path is absolute
        log_file = os.path.abspath(log_file)

    # Ensure the directory exists and is writable
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)  # Create the directory if it doesn't exist

    setup_logging(log_file)

    try:
        # Run the synchronization process every interval seconds
        while True:
            sync_folders(args.source, args.replica)  # Synchronize the folders
            time.sleep(args.interval)  # Wait for the specified time before the next sync
    except KeyboardInterrupt:
        logging.info("Synchronization process interrupted by user.")
        print("\nSynchronization process interrupted. Exiting...")

if __name__ == "__main__":
    main()
