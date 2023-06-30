# Nessus Scan Exporter

The Nessus Scan Exporter is a Python script that allows you to export Nessus scans from the Nessus API, download the scan files, and store them in a designated folder. This script can provide an automated solution to export your scan data and enable integration with other security solutions.


### Prerequisites

- Python 3.x
- Required Python packages: `requests`, `sqlite3`
- Nessus API access and API keys

### Installation

1. Clone the repository:

   ```shell
   git clone https://github.com/Satius-Security/Nessus-Scan-Exporter/
   ```

2. Install the required Python packages:

   ```shell
   pip3 install -r requirements.txt
   ```

3. Configure the script:

   - Edit a file named `BaseURL` and add the base URL of your Nessus API endpoint.
   - Edit a file named `APIkeysFile` and add your Nessus API keys.

### Scheduled Export of Nessus Scans

You can schedule the script to run periodically using task scheduler or cron job. By running the script at specified intervals, you can automate the process of exporting Nessus scans, downloading the scan files, and storing them in a designated folder. This ensures that your scan data is available for further analysis or integration with other security systems.  

### Folder Structure

After running the script, the exported Nessus scan files will be stored in the specified folder. The folder structure will look as follows:

```
nessus-scan-scraper/
├── main.py
├── BaseURL
├── APIkeysFile
├── requirements.txt
├── logs/
│   └── script.log
├── nessus_scans/
│   ├── scan_123.nessus
│   ├── scan_456.nessus
│   └── ...
└── downloaded_files.db
```

## Usage

The script provides the following command-line options:

- `--scrape-data`: Scrape scans and track the progress in the database.
- `--cleanup-db`: Clean up the database.
- `--remove-record FILE_NAME`: Remove a specific record from the database to reimport the scan file.

To scrape scans and store the progress in database:

```
python3 main.py --scrape-data
```

To clean up the database:

```
python3 main.py --cleanup-db
```

To remove a specific record from the database, provide the file name:

```
python3 main.py --remove-record FILE_NAME
```

Replace `FILE_NAME` with the name of the record you want to remove.

The `nessus_scans` folder will contain the downloaded Nessus scan files in `.nessus` format.



### Logging

The script logs its activity in a log file located in the `logs` folder. You can find the log file at `logs/script.log`. The log file contains information about the script's execution, including any errors or important messages.

### Integration with Other Security Systems

Once the Nessus scan files are exported, you can integrate them with other security systems or processes. For example, you can ingest the scan files into a Security Information and Event Management (SIEM) solution for further analysis, correlation, or alerting.

Please refer to the documentation of your specific security system or consult with your security team for guidance on how to integrate the exported Nessus scan files into your existing security infrastructure.
## About

This script was developed by Saleh Al Tarawneh under [Satius Security](https://www.satius.io/). It provides a convenient way

 to export Nessus scans, download the scan files, and store them for further analysis or integration with other security systems.

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for more details.

