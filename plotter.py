import datetime as dt
import argparse
import os
import matplotlib.pyplot as plt

from data_handler import BankAccount, Context, initialise_context
from data_handler import ACCOUNT_TYPES, OUTPUT_DATE_FORMAT, DATA_DIRECTORY, SAVE_FILE_NAME


def parse_args():
    """
    Wrapper for argparse.
    :return: command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-acc", "--accounts", help="Which bank accounts to plot", required=True)

    return parser.parse_args()


def plot_accounts(c, account_list, dates):
    """
    Plot any number of accounts and dates on a single graph.
    :param c: Context object to plot from
    :param account_list:
    :param dates: List of dates to plot
    :return: None
    """
    t = 1


def main(args):
    """
    Script entry with arguments from parseargs.
    :param args: Parseargs executed.
    :return: None
    """
    os.makedirs(DATA_DIRECTORY, exist_ok=True)
    file_path = os.path.join(DATA_DIRECTORY, SAVE_FILE_NAME)

    fullContext = initialise_context(file_path)

    if args.accounts == "all":
        t = 1



if __name__ == "__main__":
    main(parse_args())
