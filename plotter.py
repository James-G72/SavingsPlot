import argparse
import os
import matplotlib.pyplot as plt
import matplotlib.dates as md

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
    def _get_single_value(bc, date):
        """
        Get a single value for an account on a given date.
        :param bc: BankAccount to query
        :param date: date for value
        :return: float of value or None
        """
        direct_value = bc.get_value_on_date(date, interp=True)
        if direct_value == "":
            return 0
        else:
            if bc.type.lower() in ["credit", "mortgage"]:
                return -float(direct_value)
            else:
                return float(direct_value)

    def _format_axis(axes):
        """
        Once all plotting has been completed, format axes
        :param axes: A list of all axes to have the formatting applied to
        :return:
        """
        for axis in axes:
            axis.set_ylabel("Value (£)")
            axis.legend()
            axis.tick_params(axis="x", which="both", labelrotation=0, labelsize=6)


    fig, (ax_pos, ax_neg) = plt.subplots(nrows=2, ncols=1)
    xfmt = md.DateFormatter(OUTPUT_DATE_FORMAT)
    ax_pos.xaxis.set_major_formatter(xfmt)
    ax_neg.xaxis.set_major_formatter(xfmt)

    top_plot_types = ["current", "debit", "savings"]

    for bc_name, _bc in c.all_accounts.items():
        if bc_name in account_list:
            y_axis = [_get_single_value(_bc, date) for date in dates]
            datenums = md.date2num([date.date() for date in dates])
            if _bc.type.lower() in top_plot_types:
                ax_pos.plot(datenums, y_axis, label=bc_name)
            else:
                ax_neg.plot(datenums, y_axis, label=bc_name)

    for bc_name, _bc in c.totals.items():
        if bc_name == "Total Money":
            y_axis = [_get_single_value(_bc,date) for date in dates]
            datenums = md.date2num([date.date() for date in dates])
            if _bc.type.lower() in top_plot_types:
                ax_pos.plot(datenums,y_axis,label=bc_name)
            else:
                ax_neg.plot(datenums,y_axis,label=bc_name)

    _format_axis([ax_pos, ax_neg])
    fig.suptitle("Value of all Accounts")
    mng = plt.get_current_fig_manager()
    mng.full_screen_toggle()
    plt.show()


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
        plot_accounts(fullContext, fullContext.all_accounts.keys(), fullContext.all_dates)



if __name__ == "__main__":
    main(parse_args())
