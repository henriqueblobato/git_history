import argparse
import datetime
import logging
import os
import re
import subprocess
from dataclasses import dataclass
from tabulate import tabulate

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)


@dataclass
class GitLogParser:
    script_dir: str = os.path.dirname(__file__)
    jira_pattern: str = r'\b[A-Z]+-\d+\b'
    git_username: str = None
    last_days: int = 30

    def __post_init__(self):
        self.git_username = self.get_git_user()

    @staticmethod
    def get_git_user():
        command = 'git config user.name'
        try:
            result = subprocess.run(command, capture_output=True, shell=True, text=True)
            return result.stdout.strip()
        except Exception as e:
            logging.error(f"Error executing Git command: {e}")
            return None

    @staticmethod
    def get_git_log_for_date(date):
        command = (
            f'git log --all --format="%h|%an|%cd|%s" --date="format-local:%Y-%m-%d %H:%M:%S" '
            f'--after="{date} 00:00" --before="{date} 23:59"'
        )
        try:
            result = subprocess.run(command, capture_output=True, shell=True, text=True)
            return result.stdout.split('\n')
        except Exception as e:
            logging.critical(f"Error executing Git command: {e}")
            raise e

    @staticmethod
    def get_business_days(start_date, end_date):
        business_days = []
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() not in (5, 6):  # 5 and 6 are Saturday and Sunday
                business_days.append(current_date)
            current_date += datetime.timedelta(days=1)
        return business_days

    def parse_git_log(self, log):
        messages = {}
        for line in log:
            if not line:
                continue
            commit_hash, commit_owner, commit_date, commit_message = line.split('|')
            if self.git_username.lower() in commit_owner.lower():
                jira_cards = re.findall(self.jira_pattern, commit_message)
                for card in jira_cards:
                    messages.setdefault(card, []).append(commit_message.replace(card, '').strip())
        return {card: ' / '.join(message) for card, message in messages.items()}

    def grouped_messages(self, start_date, today):
        delta = datetime.timedelta(days=1)
        grouped_messages = {}
        current_date = start_date
        while current_date <= today:
            log_for_date = self.get_git_log_for_date(current_date)
            parsed_messages = self.parse_git_log(log_for_date)
            for card, message in parsed_messages.items():
                if current_date not in grouped_messages:
                    grouped_messages[current_date] = []
                grouped_messages[current_date].append(f"{card} {message}")
            current_date += delta
        return grouped_messages

    def run(self):
        today = datetime.date.today()
        start_date = today - datetime.timedelta(days=self.last_days)
        business_days = self.get_business_days(start_date, today)
        logging.info(f"Getting logs from {start_date} to {today} ({len(business_days)} business days)")

        grouped_messages = self.grouped_messages(start_date, today)
        table_data = []
        for date, messages in grouped_messages.items():
            content = [date.strftime('%Y-%m-%d'), date.strftime('%A'), ' + '.join(messages)]
            table_data.append(content)
            # print(content, sep=' | ')

        headers = ["Date", "Day of Week", "Time Track Message"]
        missing_days = [date for date in business_days if date not in grouped_messages]

        table_data.extend([[date.strftime('%Y-%m-%d'), date.strftime('%A'), ''] for date in missing_days])
        table_data.sort(key=lambda x: x[0])
        print(tabulate(table_data, headers=headers, tablefmt="rounded_grid", numalign="left", maxcolwidths=[10, 15, 100]))


def parse_date(date_string):
    return datetime.datetime.strptime(date_string, '%Y-%m-%d').date()


def parse_arguments():
    _parser = argparse.ArgumentParser()
    _parser.add_argument('-p', '--project-dir', required=False, help='Directory to change to before executing the script')
    _parser.add_argument(
        '-l', '--last-days', required=False, default=30, type=int, help='Number of business days to go back in history'
    )
    _parser.add_argument('-s', '--start', type=parse_date, help='Set a start date (YYYY-MM-DD)')
    _args = _parser.parse_args()
    return _args


if __name__ == "__main__":
    args = parse_arguments()
    # print(vars(args))
    if not args.project_dir:
        logging.warning("Using current directory as project directory")
        print(os.getcwd())
        args.project_dir = os.getcwd()
    if not os.path.isdir(args.project_dir):
        logging.error(f"Invalid directory: {args.project_dir}")
        exit(1)
    if not os.path.isdir(os.path.join(args.project_dir, '.git')):
        logging.error(f"Directory is not a Git repository: {args.project_dir}")
        exit(1)
    os.chdir(args.project_dir)

    if args.start:
        parser = GitLogParser(last_days=(datetime.date.today() - args.start).days)
    else:
        parser = GitLogParser(last_days=args.last_days)

    parser.run()
