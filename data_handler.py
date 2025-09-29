import datetime
import datetime as dt
import os
import csv

ACCOUNT_TYPES = ["current",
                 "debit",
                 "savings",
                 "credit",
                 "mortgage"]
# List of date formats to expect. This is used to avoid confusion for d-m and m-d formatting
CHECK_DATE_FORMATS = ["%d-%m-%y",
                      "%d-%b-%y",
                      "%d-%b-%Y"]
OUTPUT_DATE_FORMAT = "%d-%b-%Y"
DATA_DIRECTORY = os.path.join(os.getcwd(), "files")
SAVE_FILE_NAME = "test_data.csv"


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
        assert account_type.lower() in ACCOUNT_TYPES, (f"Invalid account type {account_type} passed for {account_name}./"
                                               f"Account types must be from: {ACCOUNT_TYPES}")
        self.name = account_name.title()
        self.type = account_type.title()
        self.currency = currency

        # Historical values over time are stored in a dictionary
        self.history = {}

    def _interpolate_value(self, date):
        """
        Interpolate the bank account value at a given date.
        :param date: Datetime object for the requested date
        :return: Value at date
        """
        # TODO implement a rational interpolation function
        t = 1

    def get_value_on_date(self, date, interp=False):
        """
        Return the value within the bank account on a given date. If interp is False, and there is not an entry for that date,
        then the function will return None
        :param date: Datetime object for the requested date
        :param interp: If the date is not preset, should one be interpolated.
        :return: value on the date
        """
        if not interp and date.strftime(OUTPUT_DATE_FORMAT) not in self.history.keys():
            return ""
        elif interp and date.strftime(OUTPUT_DATE_FORMAT) not in self.history.keys():
            return self._interpolate_value(date)
        elif date.strftime(OUTPUT_DATE_FORMAT) in self.history.keys():
            return self.history[date.strftime(OUTPUT_DATE_FORMAT)]
        else:
            return None

    def add_entry(self, value, date):
        """
        Create a new entry for a given date
        :param value: Account value
        :param date: Date for the associated value.
        :return: None
        """
        if not isinstance(date, datetime.datetime):
            date_object = handle_date_string(date)
        else:
            date_object = date
        date_str = dt.datetime.strftime(date_object, OUTPUT_DATE_FORMAT)

        self.history[date_str] = value

    def print_status(self):
        """
        Report the intertnal state of the bank account.
        :return: None
        """
        for date in self.history.keys():
            print(f"    {date} : {self.history[date]}")



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

    def add_account(self, account):
        """
        Add an account to the internal store.
        :param account: BackAccount object
        :return: None
        """
        # TODO I made this a function of the context as we will want to check to see if there are any dates in conflice
        self.all_accounts[account.name] = account

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
        print("")

    def date_report(self, date, interp=False):
        """
        Report the status of all bank accounts on a given date.
        :param date:
        :param interp: If the date is not preset, should one be interpolated.
        :return:
        """
        print(f"Reporting all bank accounts for {date.strftime(OUTPUT_DATE_FORMAT)}:")
        for n, _bc in self.all_accounts.items():
            v = _bc.get_value_on_date(date)
            t = _bc.type
            # TODO use padding to make this neat
            print(f"    {n} ({t}) - £{v}")

    def full_report(self):
        """
        Give a detailed report of the internal state of the context.
        :return: None
        """
        # TODO Once we have the internal structure for contexts, work out how to report this to command line
        print("Full report isn't implemented yet")

    def _build_csv_row(self, account_key, dates):
        """
        A specific function for building the corresponding csv for for an account.
        This could be simplified by assuming that the order in self.all_dates matches the
        internal BankAccount object order, but it will be better to explicitly build the row.
        :param account_key: The name of the account for this row.
        :param dates: A list of dates that forms the header of the csv.
        :return:
        """
        new_row = []
        _bc = self.all_accounts[account_key]
        new_row.append(account_key)
        new_row.append(_bc.type)
        for date_str in dates:
            if date_str in _bc.history.keys():
                new_row.append(_bc.history[date_str])
            else:
                new_row.append("")

        return new_row

    def save_to_csv(self, full_path, allow_overwrite=False):
        """
        Save the full contents of the context to a csv file.
        :param full_path: Absolute Windows path to a csv
        :param allow_overwrite: Allow the file to be overwritten if it already exists
        :return: True if saved successfully
        """
        path_used = os.path.exists(full_path)
        if path_used and not allow_overwrite:
            print(f"Cannot save to {full_path} without overwriting.")
            return

        # Prepare the rows for the csv output
        # TODO make sure that the dates are in chronological order
        dates_out = [dt.datetime.strftime(x, OUTPUT_DATE_FORMAT) for x in self.all_dates]
        rows_out = {}
        for key in self.all_accounts.keys():
            rows_out[key] = self._build_csv_row(key, dates_out)

        try:
            with open(full_path, "w", newline="") as csv_file:
                write_out = csv.writer(csv_file, delimiter=",")
                write_out.writerow(["Account", "Type"] + dates_out)
                for acc in self.all_accounts.keys():
                    write_out.writerow(rows_out[acc])
        except:
            print(f"Could not write to {full_path}")


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


def initialise_context(target_file):
    """
    Load an instance of the Context class from the location provided.
    :param target_file: A csv file with historical bank account data.
    :return: A Context object to encapsulate the current saved data.
    """
    c = Context(target_file)

    # Report to the user the top-level of the context that has just been loaded
    c.quick_report()

    return c
