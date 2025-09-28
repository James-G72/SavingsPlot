import datetime as dt
import os
import csv

ACCOUNT_TYPES = ["Current",
                 "Debit",
                 "Savings",
                 "Credit",
                 "Mortgage"]
# List of date formats to expect. This is used to avoid confusion for d-m and m-d formatting
CHECK_DATE_FORMATS = ["%d-%m-%y",
                      "%d-%b-%y",
                      "%d-%b-%y"]
OUTPUT_DATE_FORMAT = "%d-%b-%Y"

class BankAccount(object):
    """
    A class that contains information about a single bank account.
    """
    def __init__(self, account_name, account_type, currency="GBP"):
        """
        Each instance has a name and an assumed currency of GBP
        :param account_name: Display name for the account in any summaries and graphs
        :param account_type: Type of bank account from ACCOUNT_TYPES.
        :param currency: Currency to be associated with any values.
        """
        assert account_type in ACCOUNT_TYPES, (f"Invalid account type {account_type} passed for {account_name}./"
                                               f"Account types must be from: {ACCOUNT_TYPES}")
        self.name = account_name
        self.currency = currency

        # Historical values over time are stored in a dictionary
        self.history = {}

    def get_value_on_date(self, date, interp=False):
        """
        Return the value within the bank account on a given date. If interp is False, and there is not an entry for that date,
        then the function will return None
        :param date: Datetime object for the requested date
        :param interp: If the date is not preset, should one be interpolated.
        :return: value on the date
        """
        #TODO once storage structure is defined, fill in the entry retrieval function

        return None

    def add_entry(self, value, date):
        """
        Create a new entry for a given date
        :param value: Account value
        :param date: Date for the associated value.
        :return: None
        """
        date_object = handle_date_string(date)
        date_str = dt.datetime.strftime(date_object, OUTPUT_DATE_FORMAT)

        self.history[date_str] = value


class Context(object):
    """
    Wrapper for the full programme content at run-time. Handles loading and saving of data.
    """
    def __init__(self, historical):
        """
        Establish programme context
        :param historical: absolute filepath to a previous data export
        """
        # A tag to track if there is any change during runtime
        self.updated_this_run = False

        assert os.path.exists(historical), f"Given historical data filepath ({historical}) does not exist."
        self.all_accounts = {}
        self._load_historical(historical)

        t = 1

    def _unpack_csv(self, abs_path):
        """
        A general function for unpacking a csv of the expected format into
        :param abs_path: Absolute path to the csv
        :return: dates (list of dates), data (dict of account values)
        """
        try:
            with open(abs_path, newline="") as csv_file:
                read_in = csv.reader(csv_file, delimiter=",")
                temp_data = {}
                temp_types = {}
                for idx, row in enumerate(read_in):
                    if idx == 0:
                        dates = row[2:]
                    else:
                        temp_data[row[0]] = row[2:]
                        temp_types[row[0]] = row[1]
        except:
            print(f"Something is wrong with {abs_path}")
            # TODO make this handle exceptions properly

        return dates, temp_data, temp_types

    def _load_historical(self, abs_path):
        """
        Update the initial state from the saved state.
        :param abs_path: path to a data set of financial data
        :return: None
        """
        dates, temp_accout_data, temp_account_types = self._unpack_csv(abs_path)
        for account in temp_accout_data.keys():
            _bc = BankAccount(account, temp_account_types[account], "GBP")
            for date, value in zip(dates, temp_accout_data[account]):
                _bc.add_entry(value, date)

            self.all_accounts[account] = _bc
        self.all_dates = [handle_date_string(x)for x in dates]

    def _check_valid_csv(self, filepath):
        """
        Check if a csv is of the correct format. Checks in this function define the valid csv format.
        :param filepath: string to file location
        :return: bool, True means csv is a valid data source
        """
        # TODO need to define csv structure and build import and export functionality

        return False

    def test_updated(self):
        if not self.updated_this_run:
            if self.initial_data_state != self.data_state:
                self.updated_this_run = True

        return self.updated_this_run

    def quick_report(self):
        """
        Give a short report of the internal state of the context.
        :return: None
        """
        print(f"Data loaded for {len(self.all_accounts.keys())} bank accounts on {len(self.all_dates)} dates.")
        for key in self.all_accounts.keys():
            real_entries = [x for x in self.all_accounts[key].history.items() if x[1] != ""]
            print(f"    {key}: {len(real_entries)}")
        print("Dates span from {} to {}. ({:.2f} years)".format(
            dt.datetime.strftime(min(self.all_dates), OUTPUT_DATE_FORMAT),
            dt.datetime.strftime(max(self.all_dates), OUTPUT_DATE_FORMAT),
            (max(self.all_dates) - min(self.all_dates)).days/365))


    def full_report(self):
        """
        Give a detailed report of the internal state of the context.
        :return: None
        """
        # TODO Once we have the internal structure for contexts, work out how to report this to command line
        t = 1

    def update_from_file(self, full_path, overwrite=False):
        """
        Update the Context to reflect a new file. This is toggled between additive or a fresh start by the overwrite parameter.
        :param full_path: Full Windows Path to the
        :param overwrite:
        :return:
        """
        # TODO work out if the overwrite functionality is better implemented as just initialising a new context from the main of any script.

        return None

    def save_to_file(self, full_path, allow_overwrite=False):
        """
        Save the full contents of the context to a csv file.
        :param full_path:
        :param allow_overwrite: Allow the file to be overwritten if it already exists
        :return: True if saved successfully
        """
        # TODO work out how is best to build the structure in a csv


def handle_date_string(date_str):
    """
    Wrapping the dateutil functionality to ensure a datetime object is returned
    :param date_str: String assumed to be a date.
    :return: Datetime object
    """
    for try_format in CHECK_DATE_FORMATS:
        try:
            date_obj = dt.datetime.strptime(date_str, try_format)
            break
        except:
            pass

    assert "date_obj" in locals(), "Invalid date format provided."
    assert date_obj.date() <= dt.date.today(), f"A date has bee passed that is in the future."

    return date_obj
