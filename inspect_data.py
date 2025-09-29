import argparse
import os
import datetime as dt
from ast import literal_eval

from data_handler import BankAccount,Context,ACCOUNT_TYPES,OUTPUT_DATE_FORMAT

DATA_DIRECTORY = os.path.join(os.getcwd(), "files")
SAVE_FILE_NAME = "test_data.csv"


def parse_args():
    """
    Wrapper for argparse.
    :return: command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--action", help="Via commandline the programme can be instructed", required=True, choices=["print", "edit", "auto_update"])
    parser.add_argument("-t", "--target", help="The path to a .csv file that contains banking information")

    return parser.parse_args()


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


def edit_context(context):
    """
    Allow for the Context instance to be manually edited by the user on run_time
    :param context: Context object to be edited.
    :return: Updated Context object.
    """
    while True:
        print("   ---   Edit Mode  ---")
        while True:
            print("You have the following options:")
            # Note that options are displayed starting from 1.
            for idx, option in enumerate(EDIT_OPTIONS):
                print(f"    ({idx+1}) - {option}")
            resp = input("Please select an option using its list number: ")
            if not resp.isdigit():
                print(f"    Value '{resp}' is not a digit. Retrying.")
            elif int(resp) > idx + 1:
                print(f"    Value {int(resp)} exceeds the list length. Retrying.")
            elif int(resp) <= 0:
                print(f"    Value {int(resp)} is negative. Retrying.")
            else:
                break
                # TODO this might need to be thought through more. Else seems weird
        # Exiting the top loop, we can now perform the edit function selected
        print("")
        EDIT_FUNCTIONS[int(resp)-1](context)

        # Do we want to do anything else?
        resp = validate_user_input_list("\nDo you want to make any other edits in this session? (y/n): ",
                                        ["y","n"])
        if resp.lower() == "n":
            break

    return context


def validate_user_input_list(question, reference_answers, exact=False):
    """
    A function to wrap the process of checking user inputs against a set of acceptable answers.
    :param question: String to be presented to the user.
    :param reference_answers: List of allowable string responses.
    :param exact: If True, then the match must be case-sensitive.
    :return: Validated User response.
    """
    if not isinstance(reference_answers, list):
        reference_answers = [reference_answers]

    while True:
        question_resp = input(question)
        if exact and question_resp in reference_answers:
            break
        elif not exact and question_resp.lower() in [x.lower() for x in reference_answers]:
            break
        else:
            print(f"Response '{question_resp}' invalid. Please enter {' , '.join(reference_answers[:-1])} or {reference_answers[-1]}. Retrying.")

    return question_resp


def validate_user_input_types(question, types):
    """
    A function to wrap the process of checking user inputs against a set of acceptable types.
    :param question: String to be presented to the user.
    :param types: List of allowable string responses.
    :return: Validated User response.
    """
    def _get_type(input_string):
        """
        A function to return all types I might care about
        :param input_string: String from user to evaluate
        :return: type assessment
        """
        try:
            return type(literal_eval(input_string))
        except (ValueError, SyntaxError):
            # Caught exceptions mean a string.
            return str

    if not isinstance(types, list):
        types = [types]

    while True:
        question_resp = input(question)
        if any([_get_type(question_resp) == x for x in types]):
            break
        else:
            print(f"Response '{question_resp}' not a valid type. Please enter {' , '.join(types[:-1])} or {types[-1]}. Retrying.")

    return question_resp


def double_check_user_input(question):
    """
    A function to wrap the process of repeating the answer back to the User.
    :param question: String to be presented to the user.
    :return: string response from the user.
    """
    while True:
        question_resp = input(question)
        print(f"You have entered: {question_resp}")
        check_resp = validate_user_input_list("Is that correct? (y/n): ",["y","n"],exact=False)
        if check_resp.lower() == "y":
            break

    return question_resp


def _add_account(c):
    """
    Add an entry for a new account, which will attempt to backfill all current dates.
    :param c: Context object to edit
    :return: edited Context object
    """
    print("   ---  Add an Account  ---\n")
    while True:
        account_name = double_check_user_input("What is the name of the account to be added?: ")

        account_type = validate_user_input_list("What type of account is it?: ",ACCOUNT_TYPES)

        _bc = BankAccount(account_name, account_type)
        # Get a value for the account for all dates

        for date in c.all_dates:
            while True:
                value_resp = input(f"What was the value of {account_name} on {date.strftime(OUTPUT_DATE_FORMAT)}? "
                                   f"(if account was not active at that time, just hit enter): ")
                if not value_resp.isdigit() and value_resp != "":
                    print(f"{value_resp} is not a valid account value. Retrying")
                else:
                    break
            _bc.add_entry(value_resp, date)
            print(f"Value {value_resp} assigned to {date}")

        # Confirm the account is acceptable with the user
        print(f"Please check the values and dates for {account_name}:")
        _bc.print_status()
        check_resp = validate_user_input_list("\nAre the above details correct? (y/n): ",["y","n"])
        if check_resp.lower() == "y":
            c.add_account(_bc)
            print(f"    New account: {account_name} added successfully.")
            break
        else:
            print("Please re-enter the details.")

    return c


def _add_date(c):
    """
    Add an entry for a new date, which will attempt to do this for all accounts.
    :param c: Context object to edit
    :return: edited Context object
    """
    print("   ---  Add a Date  ---\n")
    while True:
        while True:
            new_date_str = double_check_user_input("What is the date to be added? (please use format 01-Jan-1990): ")
            try:
                new_date = dt.datetime.strptime(new_date_str, OUTPUT_DATE_FORMAT)
                break
            except:
                print(f"{new_date_str} cannot be passed using datetime format {OUTPUT_DATE_FORMAT}. Retrying")

        # Iterate through all bank accounts to add a value for that date
        temp_value_store = {}
        for bc_name in c.all_accounts.keys():
            bc_value = validate_user_input_types(f"What was the value of {bc_name} on {new_date_str}?: ",
                                                 [int, float, str])
            temp_value_store[bc_name] = bc_value

        print(f"Please check the values and dates for {new_date_str}:")
        for n, v in temp_value_store.items():
            print(f"    {n} ({c.all_accounts[n].type}) - £{v}")
        check_resp = validate_user_input_list("\nAre the above details correct? (y/n): ",["y","n"])
        if check_resp.lower() == "y":
            # TODO Unless something changes, we will want to move the 3 lines below into a Context function to ensure date is appended.
            for bc_name in c.all_accounts.keys():
                c.all_accounts[bc_name].add_entry(temp_value_store[bc_name], new_date)
            c.all_dates.append(new_date)
            print(f"\nNew date: {new_date_str} added successfully.")
            break
        else:
            print("Please re-enter the details.")

    return c


def _remove_account(c):
    """
    Remove an entry for an account.
    :param c: Context object to edit
    :return: edited Context object
    """
    print("   ---  Remove an Account  ---\n")
    while True:
        print("The bank accounts currently loaded are:")
        for bc_name in c.all_accounts.keys():
            print(f"    {bc_name}")
        target_account = double_check_user_input("Which account would you like to remove?: ")
        if target_account.lower() in [x.lower() for x in c.all_accounts.keys()]:
            check_resp = validate_user_input_list(f"Type 'Delete' to confirm deletion of {target_account}. Type 'Cancel' to abort: ",
                                        ["delete", "cancel"]).lower()
            if check_resp.lower() == "delete":
                break
            else:
                print("Aborting.")
                # Return the context without having made changes
                return c
        else:
            print(f"{target_account} does not exist. Retrying.")
    # Confirming the key to delete by running the same check as was run to validate the account selection.
    for key in c.all_accounts.keys():
        if key.lower() == target_account.lower():
            del c.all_accounts[key]
            print(f"{key} deleted.")
            break

    return c


def _remove_date(c):
    """
    Remove an entry for a date. This will be removed from all accounts
    :param c: Context object to edit
    :return: edited Context object
    """
    print("   ---  Remove a Date  ---\n")
    while True:
        print("The dates currently loaded are:")
        for date in c.all_dates:
            print(f"    {date.strftime(OUTPUT_DATE_FORMAT)}")
        target_date = double_check_user_input("Which date would you like to remove? (please use format 01-Jan-1990): ")
        if target_date in [x.strftime(OUTPUT_DATE_FORMAT) for x in c.all_dates]:
            check_resp = validate_user_input_list(f"Type 'Delete' to confirm deletion of {target_date}. Type 'Cancel' to abort: ",
                                        ["delete", "cancel"]).lower()
            if check_resp.lower() == "delete":
                break
            else:
                print("Aborting.")
                # Return the context without having made changes
                return c
        else:
            print(f"{target_date} does not exist. Retrying.")

    for bc_name, _bc in c.all_accounts.items():
        del _bc.history[target_date]
    for date in c.all_dates:
        if date.strftime(OUTPUT_DATE_FORMAT) == target_date:
            c.all_dates.remove(date)
            break
    print(f"{target_date} deleted.")

    return c


def _edit_single_value(c):
    """
    Remove a single entry for a given account, on a given date
    :param c: Context object to edit
    :return: edited Context object
    """
    print("   ---  Remove a Single Entry  ---\n")
    while True:
        print("The bank accounts currently loaded are:")
        for bc_name in c.all_accounts.keys():
            print(f"    {bc_name}")
        target_account = double_check_user_input("Which account would you like to edit?: ")
        if target_account.lower() in [x.lower() for x in c.all_accounts.keys()]:
                break
        else:
            print(f"{target_account} is not a loaded account. Retrying")

    for name, _bc in c.all_accounts.items():
        if name.lower() == target_account.lower():
            # Setting to the direct key name to avoid capitalisation issues
            target_account = name
            break

    while True:
        print(f"The dates currently loaded  for {target_account} are:")
        for date in c.all_accounts[target_account].history.keys():
            print(f"    {date}")
        target_date = double_check_user_input("Which date would you like to edit? (please use format 01-Jan-1990): ")
        if target_date in c.all_accounts[target_account].history.keys():
            break
        else:
            print(f"{target_date} is not present. Retrying")

    while True:
        print(f"Current value of {target_account} on {target_date} - {c.all_accounts[target_account].history[target_date]}")
        new_value = validate_user_input_types("What is the new value: ", [int, float, str])
        check_resp = validate_user_input_list(f"Overwrite the value {c.all_accounts[target_account].history[target_date]}"
                                              f" with {new_value}? (y/n): ", ["y", "n"])
        if check_resp == "y":
            break

    c.all_accounts[target_account].history[target_date] = new_value
    print(f"The ew value of {target_account} on {target_date} is {new_value}")

    return c


def exit_programme(context, save_path, overwrite_save=False):
    """
    Save stuff maybe
    :param context: The current Context object to be handled before exiting.
    save_path: Full Windows Path to a csv file.
    :param overwrite_save: Replace a file if it already exists.
    :return: None
    """
    # TODO work out how this function fits in and any additional functionality
    context.save_to_csv(save_path, overwrite_save)

# Defining a list of functions now that they have been created
EDIT_OPTIONS = ["Add Account", "Add Date", "Remove Account", "Remove Date", "Edit Single Value"]
EDIT_FUNCTIONS = [_add_account, _add_date, _remove_account, _remove_date, _edit_single_value]


def main(args):
    """
    Script entry with arguments from parseargs.
    :param args: Parseargs executed.
    :return: None
    """
    os.makedirs(DATA_DIRECTORY, exist_ok=True)
    file_path = os.path.join(DATA_DIRECTORY, SAVE_FILE_NAME)

    fullContext = initialise_context(file_path)

    if args.action == "auto_update":
        assert os.path.exists(args.target), f"{args.target} is an invalid filepath. Cannot update."
        fullContext.update_from_file(args.target)
    elif args.action == "print":
        fullContext.full_report()
    elif args.action == "edit":
        fullContext = edit_context(fullContext)

    # Exit by saving to the file
    exit_programme(fullContext, file_path, overwrite_save=True)


if __name__ == "__main__":
    main(parse_args())
