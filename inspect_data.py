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
    Allow for the Context instance to be manually edited by the user on run_time.
    :param context: Context object to be edited.
    :return: Updated Context object.
    """
    # TODO work out how best to make it editable

    return context


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
    elif args.edit:
        fullContext = edit_context(fullContext)

    # Exit by saving to the file
    exit_programme(fullContext, file_path, overwrite_save=True)


if __name__ == "__main__":
    main(parse_args())
