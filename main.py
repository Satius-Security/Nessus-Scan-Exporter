import requests
import sqlite3
import os
import logging
import argparse
from datetime import datetime
import time
import configparser

# Set up logging
logs_folder = 'logs'
os.makedirs(logs_folder, exist_ok=True)
log_file = os.path.join(logs_folder, 'script.log')
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Read config file
config = configparser.ConfigParser()
config.read('config.ini')

baseUrl = config.get('CONFIG', 'baseURL')
APIkeys = config.get('CONFIG', 'APIkeys')

scan_id = None
scans = '/scans'
payloadRequestExport = {"format": "nessus"}
requests.packages.urllib3.disable_warnings()


def export_scans():

    APIkeysHeader = {
        'X-ApiKeys': APIkeys
    }

    # Create a SQLite database connection
    conn = sqlite3.connect('downloaded_files.db')
    cursor = conn.cursor()

    # Create a table to store downloaded file names if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS downloaded_files (
            file_name TEXT UNIQUE
        )
    ''')

    # Create a folder to store the downloaded scans if it doesn't exist
    folder_name = 'nessus_scans'
    os.makedirs(folder_name, exist_ok=True)

    rlistscans = requests.get(baseUrl + scans, headers=APIkeysHeader, verify=False)
    scan_id_list = [scan["id"] for scan in rlistscans.json()["scans"]]
    logging.info(f'Scan IDs: {scan_id_list}')

    for scan_id in scan_id_list:
        rlistscansDetails = requests.get(baseUrl + scans + f'/{scan_id}', headers=APIkeysHeader, verify=False)
        history_id_list = [detail["history_id"] for detail in rlistscansDetails.json()["history"]]
        logging.info(f'scan_{scan_id}: {history_id_list}')

        for history_id in history_id_list:
            file_name = f"scan_{history_id}.nessus"
            file_name_done = f"scan_{history_id}.nessus_done"
            file_path = os.path.join(folder_name, file_name)

            # Check if the file name already exists in the table
            cursor.execute('SELECT file_name FROM downloaded_files WHERE file_name = ?', (file_name,))
            existing_file = cursor.fetchone()

            if existing_file:
                logging.info(f"File {file_name} already exists in the database")
                continue

            rRequestExport = requests.post(baseUrl + f'/scans/{scan_id}/export?history_id={history_id}',
                                           data=payloadRequestExport, headers=APIkeysHeader, verify=False)
            export_data = rRequestExport.json()

            if 'file' not in export_data:
                logging.error(f"Error exporting scan {scan_id}, history {history_id}: {export_data}")
                continue

            file_id = export_data["file"]
            export_status_url = baseUrl + f'/scans/{scan_id}/export/{file_id}/status'
            logging.info(f"scan ID: {scan_id}, History ID: {history_id}, File ID: {file_id}")

            # Check export status
            while True:
                rExportStatus = requests.get(export_status_url, headers=APIkeysHeader, verify=False)
                export_status_data = rExportStatus.json()
                logging.info(f"Export status response: {export_status_data}")

                if 'error' in export_status_data and export_status_data['error'] == 'The requested file was not found.':
                    logging.error(
                        f"Error exporting scan {scan_id}, history {history_id}: The requested file was not found.")
                    logging.info(f"Export status response: {rExportStatus.json()}")
                    break

                if 'status' in export_status_data and export_status_data['status'] == 'ready':
                    rDownloadExport = requests.get(baseUrl + f'/scans/{scan_id}/export/{file_id}/download',
                                                   headers=APIkeysHeader, verify=False)
                    with open(file_path, 'wb') as file:
                        file.write(rDownloadExport.content)
                        logging.info(f"File {file_name} downloaded")

                    # Create an empty '_done' file
                    file_path_done = os.path.join(folder_name, file_name_done)
                    open(file_path_done, 'w').close()
                    logging.info(f"Empty file {file_name_done} created")

                    # Insert the downloaded file name into the SQLite database
                    cursor.execute('INSERT INTO downloaded_files (file_name) VALUES (?)', (file_name,))
                    conn.commit()

                    break

                # Delay before checking export status again
                time.sleep(1)

    # Close the database connection
    conn.close()


def clean_up_database():
    # Prompt for confirmation
    confirmation = input("Are you sure you want to clean up the database? This action cannot be undone. (y/n): ")
    if confirmation.lower() != 'y':
        logging.info('Database cleanup canceled')
        return

    conn = sqlite3.connect('downloaded_files.db')
    cursor = conn.cursor()

    # Drop the downloaded_files table if it exists
    cursor.execute('DROP TABLE IF EXISTS downloaded_files')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    logging.info('Database cleaned up')


def remove_record(file_name):
    conn = sqlite3.connect('downloaded_files.db')
    cursor = conn.cursor()

    # Delete the record with the given file_name
    cursor.execute('DELETE FROM downloaded_files WHERE file_name = ?', (file_name,))
    conn.commit()
    conn.close()
    logging.info(f'Record with file name {file_name} removed from the database')


def main():
    parser = argparse.ArgumentParser(description='Nessus Scan Exporter')
    parser.add_argument('--export-data', action='store_true', help='Export scans and store them in the database')
    parser.add_argument('--cleanup-db', action='store_true', help='Clean up the database')
    parser.add_argument('--remove-record', type=str, metavar='FILE_NAME',
                        help='Remove a specific record from the database')

    args = parser.parse_args()

    if args.export_data:
        export_scans()
    elif args.cleanup_db:
        clean_up_database()
    elif args.remove_record:
        remove_record(args.remove_record)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
