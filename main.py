import os
import sys
import win32file
import win32con
import win32api
import win32security
import struct

# Log file paths
OUTPUT_LOG = "output.log"
ERROR_LOG = "error.log"

# Open log files
output_log = open(OUTPUT_LOG, "w", encoding="utf-8")
error_log = open(ERROR_LOG, "w", encoding="utf-8")

def list_files(directory):
    """
    Recursively list all files in a directory and write them to the output log.
    """
    try:
        for entry in os.scandir(directory):
            if entry.is_file():
                output_log.write(entry.path + "\n")
            elif entry.is_dir():
                list_files(entry.path)  # Recursively list files in subdirectories
    except PermissionError:
        error_log.write(f"Permission denied: {directory}\n")
    except Exception as e:
        error_log.write(f"Error accessing {directory}: {str(e)}\n")

def monitor_change_journal(drive):
    """
    Monitor the NTFS Change Journal for the specified drive.
    """
    try:
        # Open the volume handle
        volume_handle = win32file.CreateFile(
            f"\\\\.\\{drive}:",
            win32file.GENERIC_READ | win32file.GENERIC_WRITE,
            win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE,
            None,
            win32file.OPEN_EXISTING,
            win32file.FILE_FLAG_BACKUP_SEMANTICS,
            None,
        )

        # Query the USN journal
        journal_data = win32file.DeviceIoControl(
            volume_handle,
            win32con.FSCTL_QUERY_USN_JOURNAL,
            None,
            64,
        )

        # Parse the USN journal data
        usn_journal_id, first_usn, next_usn, lowest_valid_usn, max_usn, maximum_size, allocation_delta = struct.unpack(
            "<QQQQQQQ", journal_data
        )

        # Read the USN journal
        while True:
            buffer = win32file.DeviceIoControl(
                volume_handle,
                win32con.FSCTL_READ_USN_JOURNAL,
                struct.pack("<QQQ", next_usn, 0, 0),
                4096,
            )

            # Parse USN records
            usn_record_offset = 0
            while usn_record_offset < len(buffer):
                record_length, major_version, minor_version, file_reference_number, parent_file_reference_number, usn, timestamp, reason, source_info, security_id, file_attributes, file_name_length, file_name_offset = struct.unpack(
                    "<IHHQQLQLLLLHH", buffer[usn_record_offset : usn_record_offset + 60]
                )

                # Extract the file name
                file_name = buffer[
                    usn_record_offset + file_name_offset : usn_record_offset + file_name_offset + file_name_length
                ].decode("utf-16le")

                # Write the file name to the output log
                output_log.write(f"{drive}:\\{file_name}\n")

                # Move to the next record
                usn_record_offset += record_length

    except Exception as e:
        error_log.write(f"Error monitoring {drive}: {str(e)}\n")

def main():
    # List all drives
    drives = win32api.GetLogicalDriveStrings().split("\x00")[:-1]

    for drive in drives:
        drive_letter = drive[0]
        print(f"Processing drive {drive_letter}:")

        # List all files on the drive
        list_files(drive)

        # Monitor the NTFS Change Journal for the drive
        monitor_change_journal(drive_letter)

    # Close log files
    output_log.close()
    error_log.close()

if __name__ == "__main__":
    main()
