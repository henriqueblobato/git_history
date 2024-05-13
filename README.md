## Git Log Parser Script

### Overview:

This script parses Git logs to extract commit messages associated with JIRA cards. It organizes the parsed data into a tabulated format, displaying dates, corresponding weekdays, and time track messages.

### Requirements:

- Python 3.x
- Git installed and configured
- Required Python packages: argparse, datetime, logging, os, re, subprocess, dataclasses, tabulate

### Usage:

1. Clone the Repository: Ensure you have the repository cloned locally and navigate to its directory.

2. Run the Script:
    - Open a terminal in the directory where the script resides.
    - Execute the script with appropriate arguments.

    ```bash
    python script_name.py [-p PROJECT_DIR] [-l LAST_DAYS] [-s START_DATE]
    ```

    - PROJECT_DIR: Optional. Path to the project directory. Default is the current directory.
    - LAST_DAYS: Optional. Number of business days to go back in history. Default is 30 days.
    - START_DATE: Optional. Set a specific start date in the format YYYY-MM-DD.

3. View Results: The script generates a tabulated output showing the parsed Git log data.

### Example:

```bash
python git_log_parser.py -p /path/to/project -l 45 -s 2024-04-01
```

This command retrieves Git logs from the project directory /path/to/project, spanning the last 45 business days, starting from April 1, 2024.

### Output:

The output consists of a table displaying the following columns:

- Date: Date of the log entry.
- Day of Week: Corresponding weekday.
- Time Track Message: Commit messages associated with JIRA cards for that day.

Additionally, missing days (without commits) within the specified timeframe are displayed with empty message fields.

### Adding as an alias:
```bash
echo "alias tt='python /path/to/git_log_parser.py'" >> ~/.bashrc
```