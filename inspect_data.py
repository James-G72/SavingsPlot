import argparse
import os

from data_handler import Context

DATA_DIRECTORY = os.path.join(os.getcwd(), "files")
SAVE_FILE_NAME = "latest_data.csv"


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
        print("")
        while True:
            resp = input("Do you want to make any other edits? (y/n): ")
            if resp.lower() not in ["y", "n"]:
                print(f"Response '{resp}' invalid. Please enter either 'y' or 'n'. Retrying.")
            else:
                break
                # TODO same as above todo, is this sensible to else?
        if resp.lower() == "n":
            break

    return context


def _add_account(c):
    """
    Add an entry for a new account, which will attempt to backfill all current dates.
    :param c: Context object to edit
    :return: edited Context object
    """
    print("   ---  Add an Account  ---")


def _add_date(c):
    """
    Add an entry for a new date, which will attempt to do this for all accounts.
    :param c: Context object to edit
    :return: edited Context object
    """
    print("   ---  Add a Date  ---")


def _remove_account(c):
    """
    Remove an entry for an account.
    :param c: Context object to edit
    :return: edited Context object
    """
    print("   ---  Remove an Account  ---")


def _remove_date(c):
    """
    Remove an entry for a date. This will be removed from all accounts
    :param c: Context object to edit
    :return: edited Context object
    """
    print("   ---  Remove a Date  ---")


def _edit_single_value(c):
    """
    Remove a single entry for a given account, on a given date
    :param c: Context object to edit
    :return: edited Context object
    """
    print("   ---  Remove a Single Entry  ---")


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
    exit_programme(fullContext, file_path, overwrite_save=False)


if __name__ == "__main__":
    main(parse_args())
