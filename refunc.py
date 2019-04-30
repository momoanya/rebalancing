# coding: utf-8

import pandas as pd
import numpy as np
import pickle


# Securities, list of typically two etfs and two mutual funds. Representing equity
# and fixed income. Do not vary these for now.
securities = ["XBB", "XIC", "TD_Bond", "TD_CDN_Equity"]

# Variables will be input by way of a dict. This will allow for objects and variables
# to be attached to each account. A DataFrame will be created and attached below.
# Use this dict if running internally, otherwise use this dict as a template
# for calling the function from outside.


def check_var(a):
    """
    Takes the input and does a few minor checks to ensure quality input.

    :param a: dict
    :return: None

    Will return value errors if conditions not met.
    """
    # Date of first deposit must be the same as the start date.
    # if a.start_date not in pd.to_datetime(list(a.dep_with.keys())):
    #     raise ValueError("The first deposit date must equal the start date.")

    # Check deposits are made within the right range
    if (
        min(a["dep_with"].keys()) < a["start_date"]
        or max(a["dep_with"].keys()) > a["end_date"]
    ):
        raise ValueError(
            "Deposits must be made between " + a["start_date"] + " and " + a["end_date"]
        )

    # Check that the target allocation sums to one.
    if a["atar_cash"] + a["atar_fixed_income"] + a["atar_equity"] != 1.0:
        raise ValueError(
            "The target allocation for cash, fixed income, and equity must total 1.0"
        )

    # Check the start and end dates are in range.
    if a["start_date"] < "2002-01-01" or a["start_date"] > "2018-12-31":
        raise ValueError(
            "The start date must be on or between 2002-01-01 and 2018-12-31"
        )

    if a["end_date"] < "2002-01-01" or a["end_date"] > "2018-12-31":
        raise ValueError("The end date must be on or between 2002-01-01 and 2018-12-31")

    # make sure invalid account type not selected
    if a["taxable_transactions"] & a["taxable_withdrawal"]:
        raise ValueError(
            "There are no legal accounts where transactions and withdrawals are taxed."
        )

    # Check that tax rates are between 0 and 1
    if a["tax_rate"] < 0 or a["tax_rate"] > 1:
        raise ValueError("Tax rate must be between 0 and 1")

    if a["tax_div"] < 0 or a["tax_div"] > 1:
        raise ValueError("Dividend tax rate must be between 0 and 1")

    if a["tax_gains"] < 0 or a["tax_gains"] > 1:
        raise ValueError("Capital gains tax rate must be between 0 and 1")

    # Check allocations in proper ranges
    if (
        not a["amin_cash"]
        <= a["rmin_cash"]
        <= a["atar_cash"]
        <= a["rmax_cash"]
        <= a["amax_cash"]
    ):
        raise ValueError(
            "For cash: allocation minimum <= rebalance minimum <= target <= rebalance maximum <= allocation maximum."
        )

    if (
        not a["amin_fixed_income"]
        <= a["rmin_fixed_income"]
        <= a["atar_fixed_income"]
        <= a["rmax_fixed_income"]
        <= a["amax_fixed_income"]
    ):
        raise ValueError(
            "For fixed_income: allocation minimum <= rebalance minimum <= target <= rebalance maximum <= allocation "
            "maximum."
        )

    if (
        not a["amin_equity"]
        <= a["rmin_equity"]
        <= a["atar_equity"]
        <= a["rmax_equity"]
        <= a["amax_equity"]
    ):
        raise ValueError(
            "For equity: allocation minimum <= rebalance minimum <= target <= rebalance maximum <= allocation maximum."
        )


def new_df(a):
    """
    Create new dataframe from pickled mutual fund and etf dataframe template.

    :param a: dictionary, account parameters
    :return: dataframe
    """
    # Raw price data has been munged and is in a pickle file ready for use.
    filename = "accounts_template.pickle"

    # Open the existing raw data from the pickle file.
    infile = open(filename, "rb")
    df = pickle.load(infile)
    infile.close()

    # Check that the start date is on a trade date.
    # If not, move to first trade date.
    a["start_date"] = df.index[df.index >= a["start_date"]][0]

    # Drop rows outside of the start and end dates.
    df = df.loc[a["start_date"]: a["end_date"], :]

    df = df.dropna()

    return df


def initialize(a, df):
    """
    Places the initial variables/cash into the DataFrame for account rebalancing.

    :param a: dictionary, account parameters
    :param df: dataframe, initialize first dataframe for account rebalancing
    :return: dataframe
    """

    # Deposits and withdrawals planned for the account.
    # Must find the first day greater than or equal to the deposit day
    # to avoid the possibility of landing on a a null date.
    for k, v in a["dep_with"].items():
        df.at[df.index[df.index >= k][0], "dep_with"] = v

    # Move dep_with to cash, this code only gets called on the first pass through,
    # so there are no dividends or other cash to deal with yet.
    df.loc[:, "cash"] = df.loc[:, "dep_with"].cumsum()

    # Set the initial total account values.
    df.loc[:, "total_value"] = df.loc[:, "cash"]
    df.loc[:, "market_value"] = df.loc[:, "cash"]

    # All funds are in cash, set cash asset allocation to 1.
    df.loc[:, "cash_allocation"] = 1.0

    # Set cash total value.
    df.loc[:, "cash_total"] = df.loc[:, "cash"]

    return df


def trade_period_index(a, df, re_date):
    """
    Create new dataframe with index dates matching rebalancing period, used for rebalancing account dataframes.

    :param a: account dict
    :param df: dataframe
    :param re_date: string, date rebalancing to occur.
    :return: dataframe, with periodic index for rebalancing.
    """
    if a["rebalance_period"] == "D" or a["rebalance_period"] == "B":
        dfp = df.loc[re_date:, :]
    else:
        dfp = (
            df.assign(Date=df.index)
            .resample(a["rebalance_period"])
            .last()
            .set_index("Date")
        )
    return dfp


def start_accounts(a):
    """
    Create a new account with first day invested from a dictionary with account parameters 'a'

    :param a: dictionary, account parameters
    :return: dataframe, first day invested
    """
    df = new_df(a)
    initialize(a, df)

    re_date = a["start_date"]
    r = df.loc[re_date, :].to_dict()
    df.loc[re_date, :] = pd.Series(rebalance_row(r, a))
    df.loc[re_date:, :] = propagate(re_date, df, a)

    return df


def acb(
    buy_sell,
    acb_exists,
    units_exist,
    share_price,
    units_trans,
    trade_fee,
    tax_gains_rate,
):
    """
    Calculate the new adjusted cost base per share for both purchases and sales.

    :param buy_sell: str, either 'buy' or 'sell'
    :param acb_exists: float
    :param units_exist: float
    :param share_price: float
    :param units_trans: float
    :param trade_fee: float
    :param tax_gains_rate: float
    :return: float
    """

    if buy_sell == "buy":
        if units_exist == 0 and units_trans == 0:
            return acb_exists
        else:
            new_acb = (
                (acb_exists * units_exist) + (share_price * units_trans) + trade_fee
            ) / (units_exist + units_trans)
            return new_acb
    elif buy_sell == "sell":
        if units_trans == 0:
            return 0
        else:
            tax_from_sale = (
                (units_trans * (share_price - acb_exists)) - trade_fee
            ) * tax_gains_rate

            return tax_from_sale
    else:
        raise ValueError("Transaction needs to be either 'buy' or 'sale'.")


def reset_row_allocations(r):
    """
    Returns updated pd.Series for the trade day with updated asset allocations.

    :param r: dictionary, rebalanced account details on specific date.
    :return: dictionary
    """

    if r["total_value"] == 0:
        return r
    else:
        # Determine new allocations.
        r["equity_allocation"] = (
            (r["XIC-unit"] * r["XIC-nav_per_share"])
            + (r["TD_CDN_Equity-unit"] * r["TD_CDN_Equity-nav_per_share"])
        ) / r["total_value"]

        r["fixed_income_allocation"] = (
            (r["XBB-unit"] * r["XBB-nav_per_share"])
            + (r["TD_Bond-unit"] * r["TD_Bond-nav_per_share"])
        ) / r["total_value"]

        r["cash_allocation"] = r["cash"] / r["total_value"]

    return r


def sell(r, a, trade_cash, mutual_fund, security):
    """
    Sell security for trade_cash amount.

    :param r: dictionary, trade rebalancing information
    :param a: dictionary, account parameter dictionary
    :param trade_cash: float, funds to be traded
    :param mutual_fund: string, mutual fund symbol
    :param security: string, security symbol
    :return: dictionary, trade rebalancing information updated to correct cash position.
    """
    for sec in [mutual_fund, security]:
        if r[sec + "-value"] < a["minimum_trade_dollar"]:
            continue
        elif trade_cash > r[sec + "-value"]:
            trade_cash_sec = r[sec + "-value"]
            trade_cash -= trade_cash_sec
        elif trade_cash <= r[sec + "-value"]:
            trade_cash_sec = trade_cash
            trade_cash = 0
        else:
            raise ValueError("one should not end up here")
            pass

        # Trading costs.
        if r[sec + "-fund_type"] == "ETF":
            r["costs"] += a["trade_fee"]
            trade_costs = a["trade_fee"]
            r["cash"] -= a["trade_fee"]
        else:
            trade_costs = 0

        # Reduce the units.
        trade_units = (trade_cash_sec + trade_costs) / r[sec + "-nav_per_share"]

        # Add cash to the cash account and to the sales account.
        sale_revenue = trade_units * r[sec + "-nav_per_share"]
        r["sales"] += sale_revenue

        r["cash"] += sale_revenue

        # Calculate taxes on sale.
        if a["taxable_transactions"]:
            tax_gain_realized = acb(
                "sell",
                r[sec + "-acb"],
                r[sec + "-unit"],
                r[sec + "-nav_per_share"],
                trade_units,
                a["trade_fee"],
                a["tax_gains"],
            )

            r["tax_gain"] += tax_gain_realized
            r["cash"] -= tax_gain_realized
        else:
            pass

        # Adjust the units.
        r[sec + "-unit"] -= trade_units
        r[sec + "-unit_traded"] -= trade_units

        # Set new value.
        r[sec + "-value"] = r[sec + "-unit"] * r[sec + "-nav_per_share"]

    # Determine new allocations.
    r = reset_row_allocations(r)

    r["rebalanced"] = True

    return r


def buy(r, a, trade_cash, sec):
    """
    Purchase security for trade_cash amount less fee.

    :param r: dictionary, trade rebalancing information
    :param a: dictionary, account parameter dictionary
    :param trade_cash: float, funds to be traded
    :param sec: string, security symbol
    :return: dictionary, trade rebalancing information updated to correct cash position.
    """
    # Take cash from the cash account and to the purchases account.
    r["costs"] += a["trade_fee"]

    trade_cash -= r["tax_gain"]
    r["cash"] -= trade_cash
    trade_cash -= a["trade_fee"]
    r["purchases"] += trade_cash

    # Increase the equity units.
    trade_units = trade_cash / r[sec + "-nav_per_share"]

    # Calculate acb.
    r[sec + "-acb"] = acb(
        "buy",
        r[sec + "-acb"],
        r[sec + "-unit"],
        r[sec + "-nav_per_share"],
        trade_units,
        a["trade_fee"],
        a["tax_gains"],
    )

    # Adjust units.
    r[sec + "-unit"] += trade_units
    r[sec + "-unit_traded"] += trade_units

    # Set new security value.
    r[sec + "-value"] = r[sec + "-unit"] * r[sec + "-nav_per_share"]

    # Determine new allocations.
    r = reset_row_allocations(r)

    r["rebalanced"] = True

    return r


def rebalance_cash_max(r, a, trade_cash):
    """
    Sell assets to increase cash position to the minimum rebalance level.

    :param r: dictionary, trade rebalancing information
    :param a: dictionary, account parameter dictionary
    :param trade_cash: float, funds to be traded
    :return: dictionary, trade rebalancing information updated to correct cash position
    """
    # Find the delta from the asset value to the target value.
    equity_diff = r["equity_allocation"] - a["atar_equity"]
    fixed_income_diff = r["fixed_income_allocation"] - a["atar_fixed_income"]

    # Deal with possible rounding errors.
    equity_diff = 0 if abs(equity_diff) < 1e-6 else equity_diff
    fixed_income_diff = 0 if abs(fixed_income_diff) < 1e-6 else fixed_income_diff

    if all([equity_diff == 0, fixed_income_diff == 0]):
        add_to_equity = 0
        add_to_fixed_income = 0
        r["cash_allocation"] = 0
    elif all([equity_diff <= 0, fixed_income_diff <= 0]):
        # Calculate how much to add to both proportionate to how far away from target.
        add_to_equity = trade_cash * (equity_diff / (equity_diff + fixed_income_diff))
        add_to_fixed_income = trade_cash - add_to_equity

    elif any([equity_diff < 0, fixed_income_diff < 0]):
        if equity_diff < 0:
            add_to_equity = trade_cash
            add_to_fixed_income = 0
        elif fixed_income_diff < 0:
            add_to_equity = 0
            add_to_fixed_income = trade_cash
    else:
        add_to_equity = 0
        add_to_fixed_income = 0
        r["cash_allocation"] = 0

    # Reduce cash by trade cash.
    r["cash"] -= trade_cash

    # Purchase equity if required.
    if add_to_equity > 0:
        r["XIC-unit_traded"] = (add_to_equity - a["trade_fee"]) / r["XIC-nav_per_share"]

        # Adjust the acb of XIC.
        r["XIC-acb"] = acb(
            "buy",
            r["XIC-acb"],
            r["XIC-unit"],
            r["XIC-nav_per_share"],
            r["XIC-unit_traded"],
            a["trade_fee"],
            a["tax_gains"],
        )

        r["XIC-unit"] += r["XIC-unit_traded"]
        r["XIC-value"] = r["XIC-unit"] * r["XIC-nav_per_share"]
        r["purchases"] += add_to_equity

        # Trading costs.
        r["costs"] += a["trade_fee"]

    else:
        pass

    # Purchase fixed income if required.
    if add_to_fixed_income > 0:
        r["XBB-unit_traded"] = (add_to_fixed_income - a["trade_fee"]) / r[
            "XBB-nav_per_share"
        ]

        # Adjust the acb of XBB.
        r["XBB-acb"] = acb(
            "buy",
            r["XBB-acb"],
            r["XBB-unit"],
            r["XBB-nav_per_share"],
            r["XBB-unit_traded"],
            a["trade_fee"],
            a["tax_gains"],
        )

        r["XBB-unit"] += r["XBB-unit_traded"]
        r["XBB-value"] = r["XBB-unit"] * r["XBB-nav_per_share"]
        r["purchases"] += add_to_fixed_income
        # trading costs
        r["costs"] += a["trade_fee"]

    else:
        pass

    # Determine new allocations.
    r = reset_row_allocations(r)

    r["rebalanced"] = True

    return r


def rebalance_cash_min(r, a, trade_cash):
    """
    Sell assets to increase cash position to the minimum rebalance level.

    :param r: dictionary, trade rebalancing information
    :param a: dictionary, account parameter dictionary
    :param trade_cash: float, funds to be traded
    :return: dictionary, trade rebalancing information updated to correct cash position.
    """
    # Find the delta from the asset value to the target value.
    equity_diff = r["equity_allocation"] - a["atar_equity"]
    fixed_income_diff = r["fixed_income_allocation"] - a["atar_fixed_income"]

    # Deal with rounding errors.
    equity_diff = 0 if abs(equity_diff) < 1e-6 else equity_diff
    fixed_income_diff = 0 if abs(fixed_income_diff) < 1e-6 else fixed_income_diff

    if equity_diff + fixed_income_diff == 0:
        take_from_equity = 0
        take_from_fixed_income = 0
        r["cash_allocation"] = 0
        trade_cash = 0
    # If equity_diff and fixed_income_diff are both greater than zero.
    elif all([equity_diff >= 0, fixed_income_diff >= 0]):
        # How much to sell from both proportionate to how far away from target.
        take_from_equity = trade_cash * (
            equity_diff / (equity_diff + fixed_income_diff)
        )
        take_from_fixed_income = trade_cash - take_from_equity
    elif any([equity_diff > 0, fixed_income_diff > 0]):
        if equity_diff > 0:
            take_from_equity = trade_cash
            take_from_fixed_income = 0
        elif fixed_income_diff > 0:
            take_from_equity = 0
            take_from_fixed_income = trade_cash
    else:
        # If here the there is a floating error.
        take_from_equity = 0
        take_from_fixed_income = 0
        r["cash_allocation"] = 0

    # Increase cash by trade cash.
    r["cash"] += trade_cash

    for asset, security, mutual_fund in [
        ["equity", "XIC", "TD_CDN_Equity"],
        ["fixed_income", "XBB", "TD_Bond"],
    ]:

        if asset == "equity" and take_from_equity <= 0:
            continue
        elif asset == "fixed_income" and take_from_fixed_income <= 0:
            continue
        else:
            pass

        # Sell if required.
        if take_from_equity > 0 and asset == "equity":
            trans_cash = take_from_equity
            tax_rate = a["tax_gains"]
        elif take_from_fixed_income > 0 and asset == "fixed_income":
            trans_cash = take_from_fixed_income
            tax_rate = a["tax_rate"]

        for sec in [mutual_fund, security]:
            # Set trading fee for mutual fund (free) vs. etf.
            if r[sec + "-fund_type"] == "ETF":
                trading_fee = a["trade_fee"]
            else:
                trading_fee = 0

            # Determine how much to sell in mutual funds first.
            if r[sec + "-value"] < a["minimum_trade_dollar"]:
                continue
            elif trans_cash > r[sec + "-value"]:
                trade_cash_sec = r[sec + "-value"]
                trans_cash -= trade_cash_sec
            elif trans_cash <= r[sec + "-value"]:
                trade_cash_sec = trans_cash
                trans_cash = 0
            else:
                raise ValueError("one should not end up here")
                pass
            r[sec + "-unit_traded"] = -trade_cash_sec / r[sec + "-nav_per_share"]

            if a["taxable_transactions"]:
                # Calculate taxes on sale.
                tax_gain_realized = acb(
                    "sell",
                    r[sec + "-acb"],
                    r[sec + "-unit"],
                    r[sec + "-nav_per_share"],
                    -r[sec + "-unit_traded"],
                    trading_fee,
                    tax_rate,
                )

                r["tax_gain"] += tax_gain_realized
                r["cash"] -= tax_gain_realized
            else:
                pass

            r[sec + "-unit"] += r[sec + "-unit_traded"]
            r[sec + "-value"] = r[sec + "-unit"] * r[sec + "-nav_per_share"]
            r["sales"] += trade_cash_sec
            # Trading costs.
            r["costs"] += trading_fee

        else:
            pass

    # Determine new allocations.
    r = reset_row_allocations(r)

    r["rebalanced"] = True

    return r


def mutual_fund_sweep(r):
    """
    Invests funds from cash to mutual funds.

    :param r: dictionary, trade rebalancing information
    :return: dictionary, series containing new mutual fund investments from cash
    """
    cash_sweep = r["cash"]
    total_fi_and_equity = r["fixed_income_allocation"] + r["equity_allocation"]
    to_fi = 1 - (r["fixed_income_allocation"] / total_fi_and_equity)
    to_eq = 1 - (r["equity_allocation"] / total_fi_and_equity)

    for mf, sweep in [["TD_Bond", to_fi], ["TD_CDN_Equity", to_eq]]:
        if sweep == 0:
            continue
        else:
            pass

        r[mf + "-unit_traded"] = (sweep * cash_sweep) / r[mf + "-nav_per_share"]

        # Adjust the acb of XBB.
        r[mf + "-acb"] = acb(
            "buy",
            r[mf + "-acb"],
            r[mf + "-unit"],
            r[mf + "-nav_per_share"],
            r[mf + "-unit_traded"],
            0,
            0,
        )

        r[mf + "-unit"] += r[mf + "-unit_traded"]
        r[mf + "-value"] = r[mf + "-unit"] * r[mf + "-nav_per_share"]

        r["purchases"] += sweep * cash_sweep
        r["cash"] -= sweep * cash_sweep

    # Determine new allocations.
    r = reset_row_allocations(r)

    r["rebalanced"] = True

    return r


def rebalance_row(r, a):
    """
    Rebalance one day or one row as pd.Series

    :param r: dictionary, one row of the account dataframe
    :param a: dictionary, account parameters
    :return: dictionary, modified row rebalanced
    """

    # Equity max.
    if r["equity_allocation"] > a["amax_equity"]:
        # Rebalance the equity to the rebalance max.
        trade_cash = r["total_value"] * (r["equity_allocation"] - a["rmax_equity"])
        if abs(trade_cash) > a["minimum_trade_dollar"]:
            r = sell(r, a, trade_cash, "TD_CDN_Equity", "XIC")
        else:
            pass
    else:
        pass

    # Fixed income max.
    if r["fixed_income_allocation"] > a["amax_fixed_income"]:
        # Rebalance the fixed income to the rebalance max.
        trade_cash = r["total_value"] * (
            r["fixed_income_allocation"] - a["rmax_fixed_income"]
        )
        if abs(trade_cash) > a["minimum_trade_dollar"]:
            r = sell(r, a, trade_cash, "TD_Bond", "XBB")
        else:
            pass
    else:
        pass

    # Equity min.
    if r["equity_allocation"] < a["amin_equity"]:
        # Reset market value and total value to account for taxes and commissions.
        # Rebalance to the rebalance minimum.
        trade_cash = r["total_value"] * (a["rmin_equity"] - r["equity_allocation"])

        if abs(trade_cash) > a["minimum_trade_dollar"]:
            r = buy(r, a, trade_cash, "XIC")
        else:
            pass
    else:
        pass

    # Fixed income min.
    if r["fixed_income_allocation"] < a["amin_fixed_income"]:
        # Rebalance to the rebalance minimum.
        trade_cash = r["total_value"] * (
            a["rmin_fixed_income"] - r["fixed_income_allocation"]
        )

        if abs(trade_cash) > a["minimum_trade_dollar"]:
            r = buy(r, a, trade_cash, "XBB")
        else:
            pass
    else:
        pass

    # Cash greater than max.
    if r["cash_allocation"] > a["amax_cash"]:
        # Rebalance the cash to the rebalance max.
        trade_cash = r["total_value"] * (r["cash_allocation"] - a["rmax_cash"])
        if abs(trade_cash) > a["minimum_trade_dollar"]:
            r = rebalance_cash_max(r, a, trade_cash)
        else:
            pass
    else:
        pass

    # Cash less than minimum.
    if r["cash_allocation"] < a["amin_cash"]:
        # Rebalance the cash to the rebalance min.
        trade_cash = r["total_value"] * (a["rmin_cash"] - r["cash_allocation"])
        if abs(trade_cash) > a["minimum_trade_dollar"]:
            r = rebalance_cash_min(r, a, trade_cash)
        else:
            pass
    else:
        pass

    # Rounding errors in cash will cause false trades. Set cash to zero
    # if the value of cash is between plus/minus 1 x 10**-6
    if abs(r["cash_allocation"]) < 1e-6:
        r["cash"] = 0
        r["cash_allocation"] = 0

    return r


# Adjust the acb for the DRIP units purchased.
def calc_acb(nav, unit_traded, unit, acb):
    """
    Calculate the acb of a security.

    :param nav:
    :param unit_traded:
    :param unit:
    :param acb:
    :return: np.array
    """
    res = np.empty(acb.shape)
    res[0] = acb[0]
    for i in range(1, res.shape[0]):
        if (unit[i] + unit_traded[i]) == 0:
            res[i] = 0
        else:
            res[i] = ((res[i - 1] * unit[i - 1]) + (nav[i] * unit_traded[i])) / (
                unit[i - 1] + unit_traded[i]
            )
    return res


def drip(a, df):
    """
    Allocates dividends to drip or cash.

    :param a: dictionary, account parameters
    :param df: dataframe, for rebalancing
    :return: a, df
    """
    # Reset the cash to first row value of cash.
    df.iloc[1:, 0] = df.iloc[0, 0]

    # Start slice.
    s = df.index[1:]

    # Dividends for XBB and XIC.
    df.loc[s, "dividends"] = 0
    for sec in ["XBB", "XIC"]:
        df.loc[s, "dividends"] += df.loc[s, sec + "-dividends"].mul(
            df.loc[s, sec + "-unit"]
        )

    # Income dividends to realized tax for XBB and XIC.
    df.loc[s, "tax_dividend"] = 0
    if a["taxable_transactions"]:
        for s1, trate in (("XBB", a["tax_rate"]), ("XIC", a["tax_div"])):
            df.loc[s, "tax_dividend"] += (
                (df.loc[s, s1 + "-dividends"].mul(df.loc[s, s1 + "-unit"]))
            ) * trate
    else:
        pass

    # Determine if dividends going to account or DRIP.
    if a["drip"]:
        for sec in securities:
            # Check to see if non invested, and continue loop. Typically the mutual funds.
            if df.loc[df.index[0], sec + "-unit"] == 0:
                continue

            # Set the tax rate either dividend or interest.
            if not a["taxable_transactions"]:
                t_rate = 0
            elif sec == "XBB" or sec == "TD_Bond":
                t_rate = a["tax_rate"]
            else:
                t_rate = a["tax_div"]

            # Calculate units purchased with dividends.
            # Units purchased is less the dividend tax, and the difference or tax amount
            # never makes it into the account, hence tax paid.
            drip_total_dividend = df.loc[s, sec + "-dividends"].mul(
                df.loc[s, sec + "-unit"]
            )

            df.loc[s, sec + "-unit_traded"] = (
                drip_total_dividend * (1 - t_rate)
            ) / df.loc[s, sec + "-nav_per_share"]

            df[sec + "-acb"] = calc_acb(
                *df[
                    [
                        sec + "-nav_per_share",
                        sec + "-unit_traded",
                        sec + "-unit",
                        sec + "-acb",
                    ]
                ].values.T
            )

            # New unit total.
            df.loc[s, sec + "-unit"] += df.loc[s, sec + "-unit_traded"].cumsum()

    else:

        # Sweep cash to mutual funds if indicated.
        if a["mutual_funds"]:
            # Fixed income.
            df.loc[s, "TD_Bond-unit_traded"] = 0

            df.loc[s, "TD_Bond-unit_traded"] = (
                (df.loc[s, "dividends"] - df.loc[s, "tax_dividend"])
                * a["atar_fixed_income"]
            ) / df.loc[s, "TD_Bond-nav_per_share"]

            df.loc[s, "TD_Bond-unit"] += df.loc[s, "TD_Bond-unit_traded"].cumsum()

            # Equity.
            df.loc[s, "TD_CDN_Equity-unit_traded"] = 0

            df.loc[s, "TD_CDN_Equity-unit_traded"] += (
                (df.loc[s, "dividends"] - df.loc[s, "tax_dividend"]) * a["atar_equity"]
            ) / df.loc[s, "TD_CDN_Equity-nav_per_share"]

            df.loc[s, "TD_CDN_Equity-unit"] += df.loc[
                s, "TD_CDN_Equity-unit_traded"
            ].cumsum()

            for sec in ["TD_Bond", "TD_CDN_Equity"]:
                df[sec + "-acb"] = calc_acb(
                    *df[
                        [
                            sec + "-nav_per_share",
                            sec + "-unit_traded",
                            sec + "-unit",
                            sec + "-acb",
                        ]
                    ].values.T
                )

            df.loc[s, "cash"] += (
                (df.loc[s, "TD_Bond-unit"] * df.loc[s, "TD_Bond-dividends"])
                + (
                    df.loc[s, "TD_CDN_Equity-unit"]
                    * df.loc[s, "TD_CDN_Equity-dividends"]
                )
            ).cumsum()

            # Calculate taxes on mutual fund transactions.
            if a["taxable_transactions"]:
                for s1, trate in (
                    ("TD_Bond", a["tax_rate"]),
                    ("TD_CDN_Equity", a["tax_div"]),
                ):
                    df.loc[s, "tax_dividend"] += (
                        (df.loc[s, s1 + "-dividends"].mul(df.loc[s, s1 + "-unit"]))
                    ) * trate
                    df.loc[s, "cash"] -= (
                        (df.loc[s, s1 + "-dividends"].mul(df.loc[s, s1 + "-unit"]))
                    ) * trate

        else:
            # Add dividends net of tax and deposits to the cash.
            df.loc[s, "cash"] += (
                df.loc[s, "dividends"].cumsum() - df.loc[s, "tax_dividend"].cumsum()
            )

    # Add in deposits and withdrawals.
    df.loc[s, "cash"] += df.loc[s, "dep_with"].cumsum()

    return df


def propagate(re_date, df, a):
    """
    Fills down the DataFrame from the last rebalance date to the end.

    :param re_date: account
    :param a: account dict
    :param df: dataframe
    :return: account DataFrame
    """

    df = df.loc[re_date:, :].copy()

    # Propagate the number of units and acb down the DataFrame.
    for sec in securities:
        df.loc[:, sec + "-unit"] = df.loc[df.index[0], sec + "-unit"]
        df.loc[:, sec + "-acb"] = df.loc[df.index[0], sec + "-acb"]

    # Set drip values.
    df = drip(a, df)

    # Determine the market values of the individual securities.
    for sec in securities:
        df.loc[:, sec + "-value"] = (
            df.loc[:, sec + "-unit"] * df.loc[:, sec + "-nav_per_share"]
        )

    # Set market value.
    df.loc[:, "market_value"] = df.loc[
        :, ["XBB-value", "XIC-value", "TD_Bond-value", "TD_CDN_Equity-value"]
    ].sum(axis=1)

    # Set total value.
    df.loc[:, "total_value"] = df.loc[:, "market_value"] + df.loc[:, "cash"]

    # Set cash allocation.
    df.loc[:, "cash_allocation"] = df.loc[:, "cash"] / df.loc[:, "total_value"]
    df.loc[:, "cash_total"] = df.loc[:, "cash_allocation"] * df.loc[:, "total_value"]

    # Set fixed income allocation.
    df.loc[:, "fixed_income_allocation"] = (
        df.loc[:, "XBB-value"].add(df.loc[:, "TD_Bond-value"])
        / df.loc[:, "total_value"]
    )
    df.loc[:, "fixed_income_total"] = (
        df.loc[:, "fixed_income_allocation"] * df.loc[:, "total_value"]
    )

    # Set equity allocation.
    df.loc[:, "equity_allocation"] = (
        df.loc[:, "XIC-value"].add(df.loc[:, "TD_CDN_Equity-value"])
        / df.loc[:, "total_value"]
    )
    df.loc[:, "equity_total"] = (
        df.loc[:, "equity_allocation"] * df.loc[:, "total_value"]
    )

    # Set costs.
    df.loc[1:, "costs"] = df.loc[df.index[0], "costs"]

    return df


def retarget(cash, fi, eq, aa_adj):
    """
    Assign a new asset allocation to an account parameter dictionary used for rebalancing accounts on a date.
    Used in 'rebalance_portfolio.py'

    :param cash: float, cash allocation between 0. and 1.
    :param fi: float, fixed income allocation between 0. and 1.
    :param eq: float, equity allocation between 0. and 1.
    :param aa_adj: dictionary, account parameter dictionary
    :return: dictionary, account parameter dictionary with asset allocations adjusted
    """
    aa_adj["atar_cash"] = cash
    aa_adj["atar_fixed_income"] = fi
    aa_adj["atar_equity"] = eq
    aa_adj["amax_cash"] = cash
    aa_adj["amax_fixed_income"] = fi
    aa_adj["amax_equity"] = eq
    aa_adj["amin_cash"] = cash
    aa_adj["amin_fixed_income"] = fi
    aa_adj["amin_equity"] = eq
    aa_adj["rmax_cash"] = cash
    aa_adj["rmax_fixed_income"] = fi
    aa_adj["rmax_equity"] = eq
    aa_adj["rmin_cash"] = cash
    aa_adj["rmin_fixed_income"] = fi
    aa_adj["rmin_equity"] = eq

    return aa_adj


def allocate_account(account, df, target_csh, target_fi, target_eq):
    """
    Function called to allocate dollars to the accounts. Used in 'rebalance_portfolio.py'

    :param account:
    :param df:
    :param target_csh:
    :param target_fi:
    :param target_eq:
    :return:
    """
    idx = pd.IndexSlice
    owner = account["owner"]
    account_type = account["account_type"]
    inv_balance = df.loc[idx[owner, account_type], idx["invested", :]].sum()
    if inv_balance >= target_eq:
        df.loc[idx[owner, account_type], idx["new", "eq"]] = target_eq
        target_eq = 0
        inv_balance -= df.loc[idx[owner, account_type], idx["new", "eq"]]
        if inv_balance >= target_fi:
            df.loc[idx[owner, account_type], idx["new", "fi"]] = target_fi
            target_fi = 0
            inv_balance -= df.loc[idx[owner, account_type], idx["new", "fi"]]
            df.loc[idx[owner, account_type], idx["new", "csh"]] = inv_balance
            target_csh -= inv_balance
            inv_balance = 0
        elif inv_balance < target_fi:
            df.loc[idx[owner, account_type], idx["new", "fi"]] = inv_balance
            target_fi -= inv_balance
            inv_balance = 0
            df.loc[idx[owner, account_type], idx["new", "csh"]] = 0
        else:
            pass
    elif inv_balance < target_eq:
        df.loc[idx[owner, account_type], idx["new", "eq"]] = inv_balance
        target_eq -= inv_balance
        df.loc[idx[owner, account_type], idx["new", "fi"]] = 0
        df.loc[idx[owner, account_type], idx["new", "csh"]] = 0
    else:
        pass

    return df, target_csh, target_fi, target_eq


def re_allocate(df, a, re_date):
    """
    Reallocate one account dataframe to a specific asset allocation on a specific date.

    :param df: dataframe, account
    :param a: dictionary, accouneet parameters including new asset allocation.
    :param re_date: string, date rebalancing to occcur.
    :return: dataframe, rebalanced from the re_date
    """
    r = df.loc[re_date, :].to_dict()
    df.loc[re_date, :] = pd.Series(rebalance_row(r, a))
    df.loc[re_date:, :] = propagate(re_date, df, a)

    return df


def finalize(a, df):
    """
    Final account DataFrame adjustments used once all rebalancing is complete.

    :param a: dictionary, account parameters
    :param df: dataframe, account
    :return: dataframe, final account
    """
    # Normalize total value.
    df["total_value_norm"] = df["total_value"] / df.loc[a["start_date"], "total_value"]

    # If this an RRSP, reset all tax columns to zero, and set accrued and total
    # tax equal to the tax rate times total market value.
    if not a["taxable_withdrawal"] and not a["taxable_transactions"]:
        # TFSA type account, set all taxes to zero.
        df.loc[:, "tax_dividend"] = 0
        df.loc[:, "tax_gain"] = 0
        df.loc[:, "tax_realized"] = 0
        df.loc[:, "tax_accrued"] = 0
        df.loc[:, "tax_total"] = 0
        df.loc[:, "value_after_tax"] = df.loc[:, "total_value"]
    elif a["taxable_withdrawal"]:
        # RRSP type accounts.
        df.loc[:, "tax_dividend"] = 0
        df.loc[:, "tax_gain"] = 0
        df.loc[:, "tax_realized"] = 0
        rsp_accrued = df.loc[:, "total_value"] * a["tax_rate"]
        df.loc[:, "tax_total"] = rsp_accrued
        df.loc[:, "tax_accrued"] = rsp_accrued
        # Set the total value after tax.
        df.loc[:, "value_after_tax"] = df.loc[:, "total_value"].sub(
            df.loc[:, "tax_total"]
        )
    elif not a["taxable_withdrawal"] and a["taxable_transactions"]:
        # Taxable investment accounts.
        df.loc[:, "tax_accrued"] = 0
        # Set accrued tax based on acb for each security.
        for sec in securities:
            df.loc[:, "tax_accrued"] += (
                (df.loc[:, sec + "-nav_per_share"] - df.loc[:, sec + "-acb"])
                * df.loc[:, sec + "-unit"]
            ) * a["tax_gains"]

        df["tax_realized"] = (df["tax_dividend"] + df["tax_gain"]).cumsum()

        df.loc[:, "tax_total"] = df.loc[:, "tax_accrued"] + df.loc[:, "tax_realized"]
    else:
        pass

    df["value_after_tax"] = df["total_value"] - df["tax_total"]

    # Normalize value_after_tax.
    df["value_after_tax_norm"] = (
        df["value_after_tax"] / df.loc[a["start_date"], "value_after_tax"]
    )

    return df
