import empyrical as ep
import pandas as pd
import pickle
import rebalance_account as ra
from rebalance_portfolio import rebalance_portfolio
import account_templates as at


# Initial parameter dictionary. Values will be set by the generator.
params = {
    "name": "Scenario Dictionary",
    "description": "Values will be set manually by the loops",
    "start_date": "2001-01-01",
    "end_date": "2018-12-31",
    "dep_with": {"2001-01-01": 100000},
    "taxable_transactions": True,
    "taxable_withdrawal": False,
    "tax_rate": 0.3148,
    "tax_div": 0.0892,
    "tax_gains": 0.1574,
    "rebalance_period": "D",
    "trade_fee": 7.50,
    "minimum_trade_dollar": 0.0,
    "drip": True,
    "mutual_funds": True,
    "atar_cash": 0,
    "atar_fixed_income": 0.5,
    "atar_equity": 0.5,
    "amax_cash": 0.025,
    "amax_fixed_income": 0.55,
    "amax_equity": 0.55,
    "amin_cash": -0.005,
    "amin_fixed_income": 0.45,
    "amin_equity": 0.45,
    "rmax_cash": 0,
    "rmax_fixed_income": 0.50,
    "rmax_equity": 0.50,
    "rmin_cash": 0,
    "rmin_fixed_income": 0.5,
    "rmin_equity": 0.5,
}


def fin_funcs(df):
    """
    Financial calculations taken from Quantopians Empirical Library.

    :param df: dataframe containing daily returns calculated on a percentage change and also by log scale.
    :return: Dictionary of financial ratios both for percent change returns and log returns.
    """
    returns_pct = df["pct_change"]

    risk_free_rate = 0.0

    annual_return_pct = ep.annual_return(
        returns_pct, period="daily", annualization=None
    )
    cumm_return_pct = ep.cum_returns(returns_pct, starting_value=0).iloc[-1]
    cagr_pct = ep.cagr(returns_pct, period="daily", annualization=None)
    sharpe_pct = ep.sharpe_ratio(
        returns_pct, risk_free=risk_free_rate, period="daily", annualization=None
    )
    annual_volatility_pct = ep.annual_volatility(
        returns_pct, period="daily", alpha=2.0, annualization=None
    )
    max_drawdown_pct = ep.max_drawdown(returns_pct)
    calmar_pct = ep.calmar_ratio(returns_pct, period="daily", annualization=None)
    sortino_pct = ep.sortino_ratio(
        returns_pct,
        required_return=0,
        period="daily",
        annualization=None,
        _downside_risk=None,
    )
    tail_ratio_pct = ep.tail_ratio(returns_pct)

    financials = {
        "annual_return": annual_return_pct,
        "cumm_return": cumm_return_pct,
        "cagr": cagr_pct,
        "sharpe": sharpe_pct,
        "annual_volatility": annual_volatility_pct,
        "max_drawdown": max_drawdown_pct,
        "calmar": calmar_pct,
        "sortino": sortino_pct,
        "tail_ratio": tail_ratio_pct,
    }

    # Originally set up program to analyse both pct_change and log returns, but the difference between log and
    # pct_change was not material to the final analysis. Consequently pct_change used exclusively. The code below
    # is left in tact should log returns at the account level be desired.

    # returns_log = df["log_ret"]
    # Log returns not used in final scenario.
    # annual_return_log = ep.annual_return(
    #     returns_log, period="daily", annualization=None
    # )
    # cumm_return_log = ep.cum_returns(returns_log, starting_value=0).iloc[-1]
    # cagr_log = ep.cagr(returns_log, period="daily", annualization=None)
    # sharpe_log = ep.sharpe_ratio(
    #     returns_log, risk_free=risk_free_rate, period="daily", annualization=None
    # )
    # annual_volatility_log = ep.annual_volatility(
    #     returns_log, period="daily", alpha=2.0, annualization=None
    # )
    # max_drawdown_log = ep.max_drawdown(returns_log)
    # calmar_log = ep.calmar_ratio(returns_log, period="daily", annualization=None)
    # sortino_log = ep.sortino_ratio(
    #     returns_log,
    #     required_return=0,
    #     period="daily",
    #     annualization=None,
    #     _downside_risk=None,
    # )
    # tail_ratio_log = ep.tail_ratio(returns_log)

    # financials = {
    #     ("return_percent_change", "annual_return"): annual_return_pct,
    #     ("return_percent_change", "cumm_return"): cumm_return_pct,
    #     ("return_percent_change", "cagr"): cagr_pct,
    #     ("return_percent_change", "sharpe"): sharpe_pct,
    #     ("return_percent_change", "annual_volatility"): annual_volatility_pct,
    #     ("return_percent_change", "max_drawdown"): max_drawdown_pct,
    #     ("return_percent_change", "calmar"): calmar_pct,
    #     ("return_percent_change", "sortino"): sortino_pct,
    #     ("return_percent_change", "tail_ratio"): tail_ratio_pct,
    #     ("return_log", "annual_return"): annual_return_log,
    #     ("return_log", "cumm_return"): cumm_return_log,
    #     ("return_log", "cagr"): cagr_log,
    #     ("return_log", "sharpe"): sharpe_log,
    #     ("return_log", "annual_volatility"): annual_volatility_log,
    #     ("return_log", "max_drawdown"): max_drawdown_log,
    #     ("return_log", "calmar"): calmar_log,
    #     ("return_log", "sortino"): sortino_log,
    #     ("return_log", "tail_ratio"): tail_ratio_log,
    #     }

    return financials


def fin_funcs_port(df):
    """
    Financial calculations taken from Quantopians Empirical Library.
    :param df: dataframe containing daily returns calculated for a portfolio and as well for the related accounts.
    :return: Dictionary of financial ratios both for percent change returns and log returns.
    """
    returns_port = df["portfolio"]
    returns_acct = df["account"]

    risk_free_rate = 0.0

    annual_return_port = ep.annual_return(
        returns_port, period="daily", annualization=None
    )
    annual_return_acct = ep.annual_return(
        returns_acct, period="daily", annualization=None
    )

    cumm_return_port = ep.cum_returns(returns_port, starting_value=0).iloc[-1]
    cumm_return_acct = ep.cum_returns(returns_acct, starting_value=0).iloc[-1]

    cagr_port = ep.cagr(returns_port, period="daily", annualization=None)
    cagr_acct = ep.cagr(returns_acct, period="daily", annualization=None)

    sharpe_port = ep.sharpe_ratio(
        returns_port, risk_free=risk_free_rate, period="daily", annualization=None
    )
    sharpe_acct = ep.sharpe_ratio(
        returns_acct, risk_free=risk_free_rate, period="daily", annualization=None
    )

    annual_volatility_port = ep.annual_volatility(
        returns_port, period="daily", alpha=2.0, annualization=None
    )
    annual_volatility_acct = ep.annual_volatility(
        returns_acct, period="daily", alpha=2.0, annualization=None
    )
    max_drawdown_port = ep.max_drawdown(returns_port)
    max_drawdown_acct = ep.max_drawdown(returns_acct)

    calmar_port = ep.calmar_ratio(returns_port, period="daily", annualization=None)
    calmar_acct = ep.calmar_ratio(returns_acct, period="daily", annualization=None)

    sortino_port = ep.sortino_ratio(
        returns_port,
        required_return=0,
        period="daily",
        annualization=None,
        _downside_risk=None,
    )
    sortino_acct = ep.sortino_ratio(
        returns_acct,
        required_return=0,
        period="daily",
        annualization=None,
        _downside_risk=None,
    )

    tail_ratio_port = ep.tail_ratio(returns_port)
    tail_ratio_acct = ep.tail_ratio(returns_acct)

    financials = {
        ("return_portfolio", "annual_return"): annual_return_port,
        ("return_portfolio", "cumm_return"): cumm_return_port,
        ("return_portfolio", "cagr"): cagr_port,
        ("return_portfolio", "sharpe"): sharpe_port,
        ("return_portfolio", "annual_volatility"): annual_volatility_port,
        ("return_portfolio", "max_drawdown"): max_drawdown_port,
        ("return_portfolio", "calmar"): calmar_port,
        ("return_portfolio", "sortino"): sortino_port,
        ("return_portfolio", "tail_ratio"): tail_ratio_port,
        ("return_account", "annual_return"): annual_return_acct,
        ("return_account", "cumm_return"): cumm_return_acct,
        ("return_account", "cagr"): cagr_acct,
        ("return_account", "sharpe"): sharpe_acct,
        ("return_account", "annual_volatility"): annual_volatility_acct,
        ("return_account", "max_drawdown"): max_drawdown_acct,
        ("return_account", "calmar"): calmar_acct,
        ("return_account", "sortino"): sortino_acct,
        ("return_account", "tail_ratio"): tail_ratio_acct,
    }

    return financials


def set_account_type(d, a):
    """
    Set the taxable parameters for investment, rsp, and tfsa accounts.
    :param d: dictionary
    :param a: string, type of account, [inv, rsp, tfsa]
    """
    if a == "inv":
        d["taxable_transactions"] = True
        d["taxable_withdrawal"] = False
        d["dep_with"][d["start_date"]] = 100000
    elif a == "rsp":
        d["taxable_transactions"] = False
        d["taxable_withdrawal"] = True
        # Pretax dollars, the taxes post rsp are accounted for.
        d["dep_with"][d["start_date"]] = 100000 / (1 - d["tax_rate"])
    elif a == "tfsa":
        d["taxable_transactions"] = False
        d["taxable_withdrawal"] = False
        d["dep_with"][d["start_date"]] = 100000
    else:
        raise ValueError("account_type loop has a value error that is:", a)

    return d


def set_tax_rate(d, tx):
    """
    Sets the three tax rates for low, medium and high tax rates.

    :param d: string, ['low', 'medium', 'high']
    :return d: dictionary, account parameters

    Rates taken from Ernst and Young,
    https://www.ey.com/ca/en/services/tax/tax-calculators-2019-personal-tax
    """
    if tx == "high":
        # $150,000 annual income
        d["tax_rate"] = 0.4641
        d["tax_div"] = 0.3175
        d["tax_gains"] = 0.2320
    elif tx == "medium":
        # $100,000 annual income
        d["tax_rate"] = 0.4341
        d["tax_div"] = 0.2952
        d["tax_gains"] = 0.2170
    elif tx == "low":
        # $50,000 annual income
        d["tax_rate"] = 0.2965
        d["tax_div"] = 0.0756
        d["tax_gains"] = 0.1482
    else:
        raise ValueError(
            "There is a tax variable that is not [high, medium, low] or there's a problem with the tax level: ",
            tx,
        )

    return d


def specify_allocation(d, at, rr):
    # Allocations for low, med, high risk.
    # Format of tuple is (target, narrow_low, narrow_high, wide_low, wide_high)
    a_low = (0.25, 0.225, 0.275, 0.175, 0.325)
    a_med = (0.50, 0.450, 0.550, 0.350, 0.650)
    a_hgh = (0.75, 0.672, 0.825, 0.525, 0.975)

    if at == "75/25":
        fit = a_hgh[0]
        eqt = a_low[0]
        if rr == "narrow":
            fih = a_hgh[2]
            fil = a_hgh[1]
            eqh = a_low[2]
            eql = a_low[1]
        elif rr == "broad":
            fih = a_hgh[4]
            fil = a_hgh[3]
            eqh = a_low[4]
            eql = a_low[3]
    elif at == "50/50":
        fit = a_med[0]
        eqt = a_med[0]
        if rr == "narrow":
            fih = a_med[2]
            fil = a_med[1]
            eqh = a_med[2]
            eql = a_med[1]
        elif rr == "broad":
            fih = a_med[4]
            fil = a_med[3]
            eqh = a_med[4]
            eql = a_med[3]
    elif at == "25/75":
        eqt = a_hgh[0]
        fit = a_low[0]
        if rr == "narrow":
            eqh = a_hgh[2]
            eql = a_hgh[1]
            fih = a_low[2]
            fil = a_low[1]
        elif rr == "broad":
            eqh = a_hgh[4]
            eql = a_hgh[3]
            fih = a_low[4]
            fil = a_low[3]
    else:
        raise ValueError("The asset allocations are not setting properly", at, rr)

    # Cash is the same for all allocations.
    d["atar_cash"] = 0
    d["amax_cash"] = 0.025
    d["amin_cash"] = -0.005
    d["rmax_cash"] = 0
    d["rmin_cash"] = 0

    d["atar_fixed_income"] = fit
    d["rmax_fixed_income"] = fit
    d["rmin_fixed_income"] = fit
    d["amax_fixed_income"] = fih
    d["amin_fixed_income"] = fil

    d["atar_equity"] = eqt
    d["rmax_equity"] = eqt
    d["rmin_equity"] = eqt
    d["amax_equity"] = eqh
    d["amin_equity"] = eql

    return d


def save_dict(result_dict, n):
    # Use this code below to save results to pickle and reset the dictionary.
    if result_dict:
        filename = "scenario_data/data_port_asset_allocation/port_" + str(n) + ".pickle"
        with open(filename, "wb") as f:
            pickle.dump(result_dict, f)
    else:
        pass

    # Reset the dictionary here.
    return {}


def set_start_date_port(accounts, start_date):
    for a in accounts:
        a["start_date"] = start_date

    return accounts


def port_change_dep_with(p2_inv, p1_inv, p2_rsp, p2_tfsa, p1_rsp, p1_tfsa, start_date):
    p1_inv["dep_with"][start_date] = 100000
    p1_rsp["dep_with"][start_date] = 100000 / (1 - 0.4641)
    p1_tfsa["dep_with"][start_date] = 100000
    p2_inv["dep_with"][start_date] = 100000
    p2_rsp["dep_with"][start_date] = 100000 / (1 - 0.2965)
    p2_tfsa["dep_with"][start_date] = 100000

    return (p2_inv, p1_inv, p2_rsp, p2_tfsa, p1_rsp, p1_tfsa)


def scenarios(d):
    mutual_funds = (True, False)
    account_type = ("inv", "rsp", "tfsa")
    drip = (True, False)
    rebalance_period = ["D", "M", "Q", "Y"]
    tax_rate = ["low", "medium", "high"]
    duration = ["3 year", "5 year", "10 year"]
    start_date = ["2002-01-01", "2004-01-01", "2005-01-01", "2007-01-01", "2009-01-01"]
    result_dict = None
    date_dict = {
        "2002-01-01": ["2004-12-31", "2006-12-31", "2011-12-31"],
        "2004-01-01": ["2006-12-31", "2008-12-31", "2013-12-31"],
        "2005-01-01": ["2007-12-31", "2009-12-31", "2014-12-31"],
        "2007-01-01": ["2009-12-31", "2011-12-31", "2016-12-31"],
        "2009-01-01": ["2011-12-31", "2013-12-31", "2018-12-31"],
    }
    allocation_target = ["75/25", "50/50", "25/75"]
    rebalancing_range = ["narrow", "broad"]

    n = 4321

    for du in duration:
        if du == "3 year":
            continue
        for sd in start_date:
            dur_dict = {"3 year": 0, "5 year": 1, "10 year": 2}
            d["start_date"] = sd
            d["end_date"] = date_dict[sd][dur_dict[du]]
            for ac in account_type:
                d = set_account_type(d, ac)
                result_dict = save_dict(result_dict, n)
                print('####### SAVED #######')
                for rb in rebalance_period:
                    d["rebalance_period"] = rb
                    for dr in drip:
                        d["drip"] = dr
                        for tx in tax_rate:
                            d = set_tax_rate(d, tx)
                            for mf in mutual_funds:
                                d["mutual_funds"] = mf
                                for at in allocation_target:
                                    for rr in rebalancing_range:
                                        d = specify_allocation(d, at, rr)
                                        n += 1
                                        cols = (du, sd, ac, rb, dr, tx, mf, at, rr)
                                        print(cols, n)
                                        result_dict[cols] = fin_funcs(
                                            ra.rebalance_account(d)
                                        )

    result_dict = save_dict(result_dict, n)

    return pd.DataFrame.from_dict(result_dict).T


def scenarios_portfolio(p1_inv, p1_rsp, p1_tfsa, p2_inv, p2_rsp, p2_tfsa):

    accounts_dict = {
        "[p2_inv, p1_inv, p2_rsp, p1_rsp, p2_tfsa, p1_tfsa]": [
            p2_inv,
            p1_inv,
            p2_rsp,
            p1_rsp,
            p2_tfsa,
            p1_tfsa,
        ],
        "[p2_rsp, p1_rsp, p2_tfsa, p1_tfsa, p2_inv, p1_inv]": [
            p2_rsp,
            p1_rsp,
            p2_tfsa,
            p1_tfsa,
            p2_inv,
            p1_inv,
        ],
        "[p2_inv, p2_rsp, p2_tfsa, p1_inv, p1_rsp, p1_tfsa]": [
            p2_inv,
            p2_rsp,
            p2_tfsa,
            p1_inv,
            p1_rsp,
            p1_tfsa,
        ],
        "[p1_inv, p1_rsp, p1_tfsa, p2_inv, p2_rsp, p2_tfsa]": [
            p1_inv,
            p1_rsp,
            p1_tfsa,
            p2_inv,
            p2_rsp,
            p2_tfsa,
        ],
        "[p2_tfsa, p2_rsp, p2_inv, p1_tfsa, p1_rsp, p1_inv]": [
            p2_tfsa,
            p2_rsp,
            p2_inv,
            p1_tfsa,
            p1_rsp,
            p1_inv,
        ],
        "[p1_tfsa, p1_rsp, p1_inv, p2_tfsa, p2_rsp, p2_inv]": [
            p1_tfsa,
            p1_rsp,
            p1_inv,
            p2_tfsa,
            p2_rsp,
            p2_inv,
        ],
    }

    rebalance_period = ["D", "M", "Q", "Y"]
    duration = ["3 year", "5 year", "10 year"]
    start_date_list = ["2002-01-01", "2004-01-01", "2005-01-01", "2007-01-01", "2009-01-01"]
    date_dict = {
        "2002-01-01": ["2004-12-31", "2006-12-31", "2011-12-31"],
        "2004-01-01": ["2006-12-31", "2008-12-31", "2013-12-31"],
        "2005-01-01": ["2007-12-31", "2009-12-31", "2014-12-31"],
        "2007-01-01": ["2009-12-31", "2011-12-31", "2016-12-31"],
        "2009-01-01": ["2011-12-31", "2013-12-31", "2018-12-31"],
    }
    allocation_target = ["75/25", "50/50", "25/75"]
    rebalancing_range = ["narrow", "broad"]

    result_dict = None

    n = 0

    # Allocation parameters for the portfolio.
    # Used to reallocation the portfolio of accounts and mask when rebalancing needed.
    port_allocation = {
        # Schedule for portfolio rebalancing,
        # Alias	Description
        # D	    Day
        # M	    Month end
        # Q	    Quarter end
        # A	    Year end
        # BA	Business year end
        "rebalance_period": "Q",
        # Target allocation
        "atar_cash": 0.1,
        "atar_fixed_income": 0.4,
        "atar_equity": 0.5,
        # Maximum allocation limits.
        "amax_cash": 0.15,
        "amax_fixed_income": 0.45,
        "amax_equity": 0.55,
        # Minimum allocation limits.
        "amin_cash": -0.05,
        "amin_fixed_income": 0.35,
        "amin_equity": 0.45,
        # Rebalance from maximum to rmax level.
        "rmax_cash": 0.1,
        "rmax_fixed_income": 0.40,
        "rmax_equity": 0.50,
        # Rebalance from minimum to rmin level.
        "rmin_cash": 0.1,
        "rmin_fixed_income": 0.4,
        "rmin_equity": 0.5,
    }

    for k, accounts in accounts_dict.items():
        print(k)
        for sd in start_date_list:
            accounts = set_start_date_port(accounts, sd)
            result_dict = save_dict(result_dict, n)
            print("***** SAVED *****")
            for du in range(3):
                ed = date_dict[sd][du]
                # rsps in pretax dollars, since we are measuring after tax effect after all withdrawals.
                p1_inv.update({"dep_with": {sd: 100000}})
                p1_rsp.update({"dep_with": {sd: 186601.9779809666}})
                p1_tfsa.update({"dep_with": {sd: 100000}})
                p2_inv.update({"dep_with": {sd: 100000}})
                p2_rsp.update({"dep_with": {sd: 142146.41080312722}})
                p2_tfsa.update({"dep_with": {sd: 100000}})
                for rb in rebalance_period:
                    port_allocation["rebalance_period"] = rb
                    for at in allocation_target:
                        for rr in rebalancing_range:
                            port_allocation = specify_allocation(
                                port_allocation, at, rr
                            )
                            n += 1
                            cols = (k, sd, duration[du], rb, at, rr)
                            print(cols, n)
                            result_dict[cols] = fin_funcs_port(
                                rebalance_portfolio(port_allocation, accounts, sd, ed)
                            )

    result_dict = save_dict(result_dict, n)
    print("final save")

    return pd.DataFrame.from_dict(result_dict).T

def scenarios_portfolio_check(p1_inv, p1_rsp, p1_tfsa, p2_inv, p2_rsp, p2_tfsa):

    accounts_dict = {
        "[p2_inv, p1_inv, p2_rsp, p1_rsp, p2_tfsa, p1_tfsa]": [
            p2_inv,
            p1_inv,
            p2_rsp,
            p1_rsp,
            p2_tfsa,
            p1_tfsa,
        ],
        "[p2_inv, p2_rsp, p2_tfsa, p1_inv, p1_rsp, p1_tfsa]": [
            p2_inv,
            p2_rsp,
            p2_tfsa,
            p1_inv,
            p1_rsp,
            p1_tfsa,
        ]
    }

    # Create list of dates, duration 5 years, quarterly.

    df_sd = pd.Series(pd.date_range("2002-01-01", "2009-01-01",
                                    freq='QS').strftime("%Y-%b-%d")).to_frame(name='start')
    df_ed = pd.Series(pd.date_range("2006-12-31", "2013-12-31",
                                    freq='Q').strftime("%Y-%b-%d")).to_frame(name='end')
    df_dates = pd.concat((df_sd, df_ed), axis=1)


    allocation_target = ["75/25", "50/50", "25/75"]

    result_dict = None

    n = 0

    # Allocation parameters for the portfolio.
    # Used to reallocation the portfolio of accounts and mask when rebalancing needed.
    port_allocation = {
        # Schedule for portfolio rebalancing,
        # Alias	Description
        # D	    Day
        # M	    Month end
        # Q	    Quarter end
        # A	    Year end
        # BA	Business year end
        "rebalance_period": "M",
        # Target allocation
        "atar_cash": 0.1,
        "atar_fixed_income": 0.4,
        "atar_equity": 0.5,
        # Maximum allocation limits.
        "amax_cash": 0.15,
        "amax_fixed_income": 0.45,
        "amax_equity": 0.55,
        # Minimum allocation limits.
        "amin_cash": -0.05,
        "amin_fixed_income": 0.35,
        "amin_equity": 0.45,
        # Rebalance from maximum to rmax level.
        "rmax_cash": 0.1,
        "rmax_fixed_income": 0.40,
        "rmax_equity": 0.50,
        # Rebalance from minimum to rmin level.
        "rmin_cash": 0.1,
        "rmin_fixed_income": 0.4,
        "rmin_equity": 0.5,
    }



    for k, accounts in accounts_dict.items():
        print(k)
        for ind in df_dates.index:
            sd = df_dates.iloc[ind, 0]
            ed = df_dates.iloc[ind, 1]

            accounts = set_start_date_port(accounts, sd)
            result_dict = save_dict(result_dict, n)
            print("***** SAVED *****")
            # rsps in pretax dollars, since we are measuring after tax effect after all withdrawals.
            p1_inv.update({"dep_with": {sd: 100000}})
            p1_rsp.update({"dep_with": {sd: 186601.9779809666}})
            p1_tfsa.update({"dep_with": {sd: 100000}})
            p2_inv.update({"dep_with": {sd: 100000}})
            p2_rsp.update({"dep_with": {sd: 142146.41080312722}})
            p2_tfsa.update({"dep_with": {sd: 100000}})
            for at in allocation_target:
                port_allocation = specify_allocation(
                    port_allocation, at, "narrow"
                )
                n += 1
                cols = (k, sd, at)
                print(cols, n)
                result_dict[cols] = fin_funcs_port(
                    rebalance_portfolio(port_allocation, accounts, sd, ed)
                )

    result_dict = save_dict(result_dict, n)
    print("final save")

    return pd.DataFrame.from_dict(result_dict).T

def scenarios_portfolio_check_three(p1_inv, p1_rsp, p1_tfsa, p2_inv, p2_rsp, p2_tfsa):

    accounts_dict = {
        "[p1_inv, p1_rsp, p1_tfsa]": [
            p1_inv,
            p1_rsp,
            p1_tfsa,
        ],
        "[p1_rsp, p1_tfsa, p1_inv]": [
            p1_rsp,
            p1_tfsa,
            p1_inv,
        ],
        "[p1_tfsa, p1_rsp, p1_inv,]": [
            p1_tfsa,
            p1_rsp,
            p1_inv,
        ],
        "[p2_inv, p2_rsp, p2_tfsa]": [
            p2_inv,
            p2_rsp,
            p2_tfsa
        ],
        "[p2_rsp, p2_tfsa, p2_inv]": [
            p2_rsp,
            p2_tfsa,
            p2_inv,
        ],
        "[p2_tfsa, p2_rsp, p2_inv,]": [
            p2_tfsa,
            p2_rsp,
            p2_inv,
        ],
    }

    # Create list of dates, duration 5 years, quarterly.

    df_sd = pd.Series(pd.date_range("2002-01-01", "2009-01-01",
                                    freq='QS').strftime("%Y-%b-%d")).to_frame(name='start')
    df_ed = pd.Series(pd.date_range("2006-12-31", "2013-12-31",
                                    freq='Q').strftime("%Y-%b-%d")).to_frame(name='end')
    df_dates = pd.concat((df_sd, df_ed), axis=1)


    allocation_target = ["75/25", "50/50", "25/75"]

    result_dict = None

    n = 0

    # Allocation parameters for the portfolio.
    # Used to reallocation the portfolio of accounts and mask when rebalancing needed.
    port_allocation = {
        # Schedule for portfolio rebalancing,
        # Alias	Description
        # D	    Day
        # M	    Month end
        # Q	    Quarter end
        # A	    Year end
        # BA	Business year end
        "rebalance_period": "M",
        # Target allocation
        "atar_cash": 0.1,
        "atar_fixed_income": 0.4,
        "atar_equity": 0.5,
        # Maximum allocation limits.
        "amax_cash": 0.25,
        "amax_fixed_income": 0.55,
        "amax_equity": 0.65,
        # Minimum allocation limits.
        "amin_cash": -0.05,
        "amin_fixed_income": 0.25,
        "amin_equity": 0.35,
        # Rebalance from maximum to rmax level.
        "rmax_cash": 0.1,
        "rmax_fixed_income": 0.40,
        "rmax_equity": 0.50,
        # Rebalance from minimum to rmin level.
        "rmin_cash": 0.1,
        "rmin_fixed_income": 0.4,
        "rmin_equity": 0.5,
    }



    for k, accounts in accounts_dict.items():
        print(k)
        for ind in df_dates.index:
            sd = df_dates.iloc[ind, 0]
            ed = df_dates.iloc[ind, 1]

            accounts = set_start_date_port(accounts, sd)
            result_dict = save_dict(result_dict, n)
            print("***** SAVED *****")
            # rsps in pretax dollars, since we are measuring after tax effect after all withdrawals.
            p1_inv.update({"dep_with": {sd: 100000}})
            p1_rsp.update({"dep_with": {sd: 186601.9779809666}})
            p1_tfsa.update({"dep_with": {sd: 100000}})
            p2_inv.update({"dep_with": {sd: 100000}})
            p2_rsp.update({"dep_with": {sd: 142146.41080312722}})
            p2_tfsa.update({"dep_with": {sd: 100000}})
            for at in allocation_target:
                port_allocation = specify_allocation(
                    port_allocation, at, "narrow"
                )
                n += 1
                cols = (k, sd, at)
                print(cols, n)
                result_dict[cols] = fin_funcs_port(
                    rebalance_portfolio(port_allocation, accounts, sd, ed)
                )

    result_dict = save_dict(result_dict, n)
    print("final save")

    return pd.DataFrame.from_dict(result_dict).T

def scenarios_asset_allocation(p1_inv, p1_rsp, p1_tfsa, p2_inv, p2_rsp, p2_tfsa):

    # Allocation parameters for the portfolio.
    # Used to reallocation the portfolio of accounts and mask when rebalancing needed.
    port_allocation = {
        # Schedule for portfolio rebalancing,
        # Alias	Description
        # D	    Day
        # M	    Month end
        # Q	    Quarter end
        # A	    Year end
        # BA	Business year end
        "rebalance_period": "M",
        # Target allocation
        "atar_cash": 0.1,
        "atar_fixed_income": 0.4,
        "atar_equity": 0.5,
        # Maximum allocation limits.
        "amax_cash": 0.25,
        "amax_fixed_income": 0.55,
        "amax_equity": 0.65,
        # Minimum allocation limits.
        "amin_cash": 0.075,
        "amin_fixed_income": 0.25,
        "amin_equity": 0.35,
        # Rebalance from maximum to rmax level.
        "rmax_cash": 0.1,
        "rmax_fixed_income": 0.40,
        "rmax_equity": 0.50,
        # Rebalance from minimum to rmin level.
        "rmin_cash": 0.1,
        "rmin_fixed_income": 0.4,
        "rmin_equity": 0.5,

        }

    # Set account level allocations

    sd = "2002-01-01"
    ed = "2018-12-31"
    accounts = set_start_date_port([
        p2_inv,
        p1_inv,
        p2_rsp,
        p1_rsp,
        p2_tfsa,
        p1_tfsa,
    ], sd)

    # set tax rate
    for acct in [p1_inv, p1_rsp, p1_tfsa]:
        set_tax_rate(acct, 'high')
    for acct in [p2_inv, p2_rsp, p2_tfsa]:
        set_tax_rate(acct, 'low')

    # reset other account parameters
    for acct in accounts:
        acct['rebalance_period'] = "D"
        acct['drip'] = False
        acct['mutual_funds'] = False
        acct['trade_fee'] = 7.50
        acct["minimum_trade_dollar"] = 0

    # rsps in pretax dollars, since we are measuring after tax effect after all withdrawals.
    p1_inv.update({"dep_with": {sd: 50000}})
    p1_rsp.update({"dep_with": {sd: 186601.9779809666}})
    p1_tfsa.update({"dep_with": {sd: 65000}})
    p2_inv.update({"dep_with": {sd: 175000}})
    p2_rsp.update({"dep_with": {sd: 142146.41080312722}})
    p2_tfsa.update({"dep_with": {sd: 10000}})

    _, df_aa = rebalance_portfolio(port_allocation, accounts, sd, ed)

    # pickle the dataframe for use in other analysis
    with open("scenario_data/port_aa.pickle", "wb") as f:
        pickle.dump(df_aa, f)

    return df_aa

if __name__ == "__main__":

    # account_scenarios = scenarios(params)

    rd = scenarios_asset_allocation(
        at.p1_inv, at.p1_rsp, at.p1_tfsa, at.p2_inv, at.p2_rsp, at.p2_tfsa
    )


    end = "end"
