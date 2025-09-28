import argparse
import os

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
        resp = validate_user_input("\nDo you want to make any other edits? (y/n): ", ["y", "n"])
        if resp.lower() == "n":
            break

    return context


def validate_user_input(question, reference_answers, exact=False):
    """
    A function to wrap the process of checking user inputs against a set of acceptable answers.
    :param question: String to be presented to the user.
    :param reference_answers: List of allowable string responses.
    :param exact: If True, then the match must be case-sensitive.
    :return: Validated User response.
    """
    while True:
        question_resp = input(question)
        if exact and question_resp in reference_answers:
            break
        elif not exact and question_resp.lower() in [x.lower() for x in reference_answers]:
            break
        else:
            print(f"Response '{question_resp}' invalid. Please enter {' , '.join(reference_answers[:-1])} or {reference_answers[-1]}. Retrying.")

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
        check_resp = validate_user_input("Is that correct? (y/n): ", ["y", "n"], exact=False)
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

        account_type = validate_user_input("What type of account is it?: ", ACCOUNT_TYPES)

        _bc = BankAccount(account_name, account_type)
        # Get a value for the account for all dates

        for date in c.all_dates:
            while True:
                value_resp = input(f"What was the value of {account_name} on {date.strftime(OUTPUT_DATE_FORMAT)}?: ")
                if not value_resp.isdigit():
                    print(f"{value_resp} is not a valid account value. Retrying")
                else:
                    break
            _bc.add_entry(value_resp, date)
            print(f"Value {value_resp} assigned to {date}")

        # Confirm the account is acceptable with the user
        print(f"Please check the values and dates for {account_name}:")
        _bc.print_status()
        check_resp = validate_user_input("\nDo you want to make any other edits? (y/n): ", ["y", "n"])
        if check_resp.lower() == "y":
            c.add_account(_bc)
            print(f"    New account: {account_name} added successfully.")
            break
        else:
            print("Please re-enter the details.")


def _add_date(c):
    """
    Add an entry for a new date, which will attempt to do this for all accounts.
    :param c: Context object to edit
    :return: edited Context object
    """
    print("   ---  Add a Date  ---\n")




def _remove_account(c):
    """
    Remove an entry for an account.
    :param c: Context object to edit
    :return: edited Context object
    """
    print("   ---  Remove an Account  ---\n")


def _remove_date(c):
    """
    Remove an entry for a date. This will be removed from all accounts
    :param c: Context object to edit
    :return: edited Context object
    """
    print("   ---  Remove a Date  ---\n")


def _edit_single_value(c):
    """
    Remove a single entry for a given account, on a given date
    :param c: Context object to edit
    :return: edited Context object
    """
    print("   ---  Remove a Single Entry  ---\n")


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
