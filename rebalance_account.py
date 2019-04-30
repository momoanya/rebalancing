# coding: utf-8

import account_templates as at
import numpy as np
import pandas as pd
import refunc as rf


# Securities, list of typically two etfs and two mutual funds. Representing equity
# and fixed income. Do not vary these for now.
securities = rf.securities

# todo: return optinon check it out
def rebalance_account(a):
    """
    Initializes accounts and calls rebalancing methods.

    Organizes the accounts as inputs. Initializes each account in a dict and
    calls for the creation of a DataFrame. Feeds the dict into the methods
    and returns a fully balanced and calculated account based upon
    the initial criteria.

    :param a: dictionary as below
    dict:
    A single account is represented by a dict.
    Each dict has object attributes. The following
    dict is the template and should be copied and used.

    dict(
    "name": "TESTING DICTIONARY",

    # One line description of the account
    "description": "Figuring it out",

    # The date range for analysis,
    # must be between 2002-01-01 and 2018-12-31.
    "start_date": "2003-01-03",
    "end_date": "2007-12-31",

    # All deposits including initial deposit should be stated here.
    # List of dates and deposits/withdrawals in dictionary format.
    # Negative number for withdrawals. The dates in the template are
    # the defaults.
    "dep_with": {"2003-01-03": 100000},

    # Transactions subject to tax
    # TFSA:          transactions = False,      withdrawals = False
    # RRSP:          transaeections = False,      withdrawals = True
    # Taxable:       transactions = True,      withdrawals = False
    "taxable_transactions": True,

    # RRSPs have tax on withdrawal, this shown accrued in taxes
    "taxable_withdrawal": False,

    # Marginal tax rates for Ontario at $75,000 income
    # for general tax like rsp withdrawal or interest income.
    "tax_rate": 0.3148,

    # Tax rate on Canadian dividends as a percent of tax_rate.
    "tax_div": 0.0892,

    # Inclusion rate tax rate on capital gains realized.
    "tax_gains": 0.1574,

    # Schedule for portfolio rebalancing,
    # Alias	Description
    # D	    Day
    # M	    Month end
    # Q	    Quarter end
    # A	    Year end
    # BA	Business year end
    "rebalance_period": "Q",

    # Trading Fees
    # Trade_fee or slippage defaults to $7.50, 0 if no fee.
    "trade_fee": 7.50,

    # Minimum trade size.
    "minimum_trade_dollar": 100.00,

    # Dividends reinvested with no cost, drip=True
    # otherwise to cash for later rebalancing.
    "drip": True,

    # Mutual funds used for cash management, cost reduction.
    "mutual_funds": False,

    # Asset allocations, all values between 0 and 1.

    # Target allocations must add up to 1.0.
    "atar_cash": 0,
    "atar_fixed_income": 0.5,
    "atar_equity": 0.5,

    # Maximum allocation limits.
    "amax_cash": 0.025,
    "amax_fixed_income": 0.55,
    "amax_equity": 0.55,

    # Minimum allocation limits.
    "amin_cash": -0.005,
    "amin_fixed_income": 0.45,
    "amin_equity": 0.45,

    # Rebalance from maximum to rmax level.
    "rmax_cash": 0,
    "rmax_fixed_income": 0.50,
    "rmax_equity": 0.50,

    # Rebalance from minimum to rmin level.
    "rmin_cash": 0,
    "rmin_fixed_income": 0.5,
    "rmin_equity": 0.5,
    }

    :return:
    df: dataframe

    """
    # todo: check if I should delete this? Is it just one test causing problems?
    # Check the input variables.
    # rf.check_var(a)

    df = rf.new_df(a)

    # Initial set up, deposit cash et.
    df = rf.initialize(a, df)

    # Set the first day of the period.
    re_date = a["start_date"]

    dfp = rf.trade_period_index(a, df, re_date)

    while re_date <= pd.to_datetime(a["end_date"]):

        # Set the row of the df to a pd.Series and call to function rebalance_row,
        # that will return a rebalanced account on that day.
        r = df.loc[re_date, :].to_dict()

        # Then reset the df row to the adjusted rebalanced pd.Series.
        df.loc[re_date, :] = pd.Series(rf.rebalance_row(r, a))

        # Propagate all values down from last rebalance date.
        df.loc[re_date:, :] = rf.propagate(re_date, df, a)

        # Create a DataFrame for setting time periods for trading such as monthly, quarterly etc.
        # This will be used to filter below and determine if there is a valid rebalancing date.

        dft = df.filter(items=dfp.index, axis=0)

        # Create masks to filter for first row to be rebalanced.
        # Test for maximum levels.
        mask1 = (dft["cash_allocation"] > a["amax_cash"]) & (
            ((dft["cash_allocation"] - a["rmax_cash"]) * dft["total_value"])
            > a["minimum_trade_dollar"]
        )
        mask2 = (dft["fixed_income_allocation"] > a["amax_fixed_income"]) & (
            (
                (dft["fixed_income_allocation"] - a["rmax_fixed_income"])
                * dft["total_value"]
            )
            > a["minimum_trade_dollar"]
        )
        mask3 = (dft["equity_allocation"] > a["amax_equity"]) & (
            ((dft["equity_allocation"] - a["rmax_equity"]) * dft["total_value"])
            > a["minimum_trade_dollar"]
        )
        # Test for minimum levels.
        mask4 = (dft["cash_allocation"] < a["amin_cash"]) & (
            ((dft["cash_allocation"] - a["rmin_cash"]) * dft["total_value"])
            < -a["minimum_trade_dollar"]
        )
        mask5 = (dft["fixed_income_allocation"] < a["amin_fixed_income"]) & (
            (
                (dft["fixed_income_allocation"] - a["rmin_fixed_income"])
                * dft["total_value"]
            )
            < -a["minimum_trade_dollar"]
        )
        mask6 = (dft["equity_allocation"] < a["amin_equity"]) & (
            ((dft["equity_allocation"] - a["rmin_equity"]) * dft["total_value"])
            < -a["minimum_trade_dollar"]
        )
        # if a["mutual_funds"]:
        #     mask7 = dft["cash"] > a["minimum_trade_dollar"]
        # else:
        #     dft["false"] = False
        #     mask7 = dft["false"]

        # Finalize account if there masks conditions not met.
        if dft[mask1 | mask2 | mask3 | mask4 | mask5 | mask6].empty:
            df = rf.finalize(a, df)
            df["pct_change"] = df.value_after_tax.pct_change()
            df["log_ret"] = np.log(df.value_after_tax) - np.log(
                df.value_after_tax.shift(1)
            )
            return df

        else:
            # Get the date for the next rebalancing.
            re_date = dft[mask1 | mask2 | mask3 | mask4 | mask5 | mask6].iloc[0].name


if __name__ == "__main__":

    a_dict = at.params
    result = rebalance_account(a_dict)
    print(result)
