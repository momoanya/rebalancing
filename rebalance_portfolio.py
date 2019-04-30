import account_templates as at
import pandas as pd
import rebalance_account as ra
import refunc as rf


def rebalance_portfolio(port_allocation, accounts, start_date, end_date):
    """
    Creates and manages multiple investment accounts with combined results.

    :param accounts: Accounts dictionary and deposits to be set.

    :returns: two dataframes:
              dataframe1, Two columns, portfolio returns, account returns, pct_change.
              dataframe2, long format with asset allocations for each account for plotting.
    """
    # Create slicer.
    idx = pd.IndexSlice

    # Create empty dataframes in each account, to be used to determine if this is initialization or rebalance.
    # e.g. a['df'].empty is True
    for a in accounts:
        a["df"] = pd.DataFrame()
        a["dfa"] = pd.DataFrame()

    # Set default parameters in the account dictionaries.
    for act in accounts:
        # act["trade_fee"] = 7.50
        # act["minimum_trade_dollar"] = 100
        # act["drip"] = True
        # act["mutual_funds"] = False

        # Set the start and end date.
        # Make initial deposit equal to zero.
        # Mutual funds must be false.
        act["start_date"] = start_date
        act["end_date"] = end_date

    # Initialize rebalancing date to the start date.
    re_date = start_date

    # Create account tuple for building the multi index for rows.
    accounts_list = []
    for a in accounts:
        accounts_list.append(tuple((a["owner"], a["account_type"])))

    # Create portfolio dataframe for tracking assets. This will show the current investments,
    # new investments, and asset allocations in percent.
    idex = pd.MultiIndex.from_tuples(accounts_list, names=["person", "act_type"])
    col = pd.MultiIndex.from_product(
        [["invested", "new"], ["csh", "fi", "eq"]], names=["status", "asset"]
    )
    df = pd.DataFrame(data=0, index=idex, columns=col)

    # Put initial cash in the portfolio dataframe accounts.
    for a in accounts:
        df.loc[idx[a["owner"], a["account_type"]], idx["invested", "csh"]] = a[
            "dep_with"
        ][start_date]

    # Total size of the initial portfolio.
    total_invested = df.loc[idx[:, :], idx["invested", :]].sum().sum()

    rebalancing = True
    while rebalancing:
        # Determine target allocation in dollars.
        target_csh = total_invested * port_allocation["atar_cash"]
        target_fi = total_invested * port_allocation["atar_fixed_income"]
        target_eq = total_invested * port_allocation["atar_equity"]

        # Allocate dollars to the accounts.
        for a in accounts:
            df, target_csh, target_fi, target_eq = rf.allocate_account(
                a, df, target_csh, target_fi, target_eq
            )

        # Determine allocation percentages.
        df1 = df.loc[:, idx["new", ("csh", "fi", "eq")]].div(
            df.loc[:, idx["new", :]].sum(axis=1), axis=0
        )
        df = df.join(df1.rename(columns={"new": "allocation"}, level=0))

        # Initialize the dataframes for each account.
        for a in accounts:
            cash_all = df.loc[
                idx[a["owner"], a["account_type"]], idx["allocation", "csh"]
            ]
            fi_all = df.loc[idx[a["owner"], a["account_type"]], idx["allocation", "fi"]]
            eq_all = df.loc[idx[a["owner"], a["account_type"]], idx["allocation", "eq"]]
            adj_asset_allocation = rf.retarget(cash_all, fi_all, eq_all, a)
            if a["df"].empty:
                a["df"] = rf.start_accounts(adj_asset_allocation)
            else:
                r = a["df"].loc[re_date, :].to_dict()
                # Reset the df row to the adjusted rebalanced pd.Series.
                a["df"].loc[re_date, :] = pd.Series(rf.rebalance_row(r, a))

                # Propagate all values down from last rebalance date.
                a["df"].loc[re_date:, :] = rf.propagate(re_date, a["df"], a)

        # Create a dataframe with the index rebalancing periods, this is used
        # so that the re-sampling is only done once. Columns are not used, just the index.
        dfp = rf.trade_period_index(
            port_allocation, accounts[0]["df"][["cash", "total_value"]], start_date
        )

        # Create a dataframe and add all the account dataframe assets into totals columns.
        cols = ["cash_total", "fixed_income_total", "equity_total"]
        df_port = pd.DataFrame(data=0, index=accounts[0]["df"].index, columns=cols)

        for a in accounts:
            df_port = df_port.add(a["df"][cols])

        # Create dataframe that shows the allocation for the entire portfolio in percentages over timeindex.
        df_port_all = df_port.div(df_port.sum(axis=1), axis=0)

        # Filter the dataframe with percentages to show only dates for the trading periods,
        # e.g. A annual, Q quarterly
        dft = df_port_all.filter(items=dfp.index, axis=0)

        # The columns in the accounts have different names than the short-forms used in these dataframes.
        dft.columns = [
            "cash_allocation",
            "fixed_income_allocation",
            "equity_allocation",
        ]

        # Use masks to filter the dataframe with percentages to see if asset allocation is outside
        # accepted limits. If so, set the rebalance date (re_date) and repeat above.
        # If not, then finalize the account dataframes and finish.
        # Test for maximum levels.
        mask1 = dft["cash_allocation"] > port_allocation["amax_cash"]
        mask2 = dft["fixed_income_allocation"] > port_allocation["amax_fixed_income"]
        mask3 = dft["equity_allocation"] > port_allocation["amax_equity"]
        # Test for minimum levels.
        mask4 = dft["cash_allocation"] < port_allocation["amin_cash"]
        mask5 = dft["fixed_income_allocation"] < port_allocation["amin_fixed_income"]
        mask6 = dft["equity_allocation"] < port_allocation["amin_equity"]

        # Get the date for the next rebalancing.
        if dft[mask1 | mask2 | mask3 | mask4 | mask5 | mask6].empty:
            # Finalize accounts.
            df_result_portfolio = pd.DataFrame(
                data=0, index=accounts[0]["df"].index, columns=["value_after_tax"]
            )

            df_account_ass_all = pd.DataFrame(
                data=None,
                columns=[
                    "account",
                    "cash_all_compare",
                    "fixed_income_all_compare",
                    "equity_all_compare",
                ],
            )

            for a in accounts:
                a["df"] = rf.finalize(a, a["df"])
                df_result_portfolio = df_result_portfolio.add(
                    a["df"][["value_after_tax"]]
                )

                # Add markers to dataframe.
                a["df"]["account"] = a["name"]
                a["df"]["owner"] = a["owner"]
                a["df"]["account_type"] = a["account_type"]

                # Calculate after-tax asset allocation in dollars.
                a["df"]["cash_all_compare"] = a["df"]["value_after_tax"].mul(
                    a["df"]["cash_allocation"]
                )
                a["df"]["fixed_income_all_compare"] = a["df"]["value_after_tax"].mul(
                    a["df"]["fixed_income_allocation"]
                )
                a["df"]["equity_all_compare"] = a["df"]["value_after_tax"].mul(
                    a["df"]["equity_allocation"]
                )
                # Build asset allocation dataframe for graphing in final report.
                if not df_account_ass_all.empty:
                    df_account_ass_all = pd.concat(
                        [
                            df_account_ass_all,
                            a["df"].loc[
                            :,
                            [
                                "account",
                                "owner",
                                "account_type",
                                "cash_all_compare",
                                "fixed_income_all_compare",
                                "equity_all_compare",
                            ],
                            ],
                        ],
                        axis=0,
                    )
                else:
                    df_account_ass_all = a["df"].loc[
                                         :,
                                         [
                                             "account",
                                             "owner",
                                             "account_type",
                                             "cash_all_compare",
                                             "fixed_income_all_compare",
                                             "equity_all_compare",
                                         ],
                                         ]

            # Make df_account_ass_all wide to long format.
            df_account_ass_all = df_account_ass_all.reset_index()

            df_account_ass_all.columns = ["trade_date", "account", "owner", "account_type", "cash", "fixed_income",
                                          "equity"]

            df_account_ass_all = pd.melt(
                df_account_ass_all,
                id_vars=["trade_date", "account", "owner", "account_type"],
                value_vars=["cash", "fixed_income", "equity"],
            )

            df_account_ass_all.rename(columns={"variable": "asset"}, inplace=True)

            df_result_portfolio["returns"] = df_result_portfolio[
                "value_after_tax"
            ].pct_change()
            df_result_portfolio = df_result_portfolio["returns"]
            df_result_accounts = pd.DataFrame(
                data=0, index=accounts[0]["df"].index, columns=["value_after_tax"]
            )
            for a in accounts:
                # Set the account rebalancing parameters equal to the portfolio rebalancing parameters.
                a["rebalance_period"] = port_allocation["rebalance_period"]
                a["atar_cash"] = port_allocation["atar_cash"]
                a["atar_fixed_income"] = port_allocation["atar_fixed_income"]
                a["atar_equity"] = port_allocation["atar_equity"]
                a["amax_cash"] = port_allocation["amax_cash"]
                a["amax_fixed_income"] = port_allocation["amax_fixed_income"]
                a["amax_equity"] = port_allocation["amax_equity"]
                a["amin_cash"] = port_allocation["amin_cash"]
                a["amin_fixed_income"] = port_allocation["amin_fixed_income"]
                a["amin_equity"] = port_allocation["amin_equity"]
                a["rmax_cash"] = port_allocation["rmax_cash"]
                a["rmax_fixed_income"] = port_allocation["rmax_fixed_income"]
                a["rmax_equity"] = port_allocation["rmax_equity"]
                a["rmin_cash"] = port_allocation["rmin_cash"]
                a["rmin_fixed_income"] = port_allocation["rmin_fixed_income"]
                a["rmin_equity"] = port_allocation["rmin_equity"]

                a["dfa"] = ra.rebalance_account(a)
                df_result_accounts = df_result_accounts.add(
                    a["dfa"][["value_after_tax"]]
                )



            df_result_accounts["returns"] = df_result_accounts[
                "value_after_tax"
            ].pct_change()
            df_result_accounts = df_result_accounts["returns"]

            df_result = pd.concat(
                [df_result_portfolio, df_result_accounts],
                axis=1,
                keys=["portfolio", "account"],
            )
            return df_result, df_account_ass_all
        else:
            # Get the date for the next rebalancing
            re_date = dft[mask1 | mask2 | mask3 | mask4 | mask5 | mask6].iloc[0].name

            total_invested = df_port.loc[re_date].sum()

            # Determine the current asset mix of the portfolio.
            cols_acct = ["cash_total", "fixed_income_total", "equity_total"]
            convert = {
                "cash_total": "csh",
                "fixed_income_total": "fi",
                "equity_total": "eq",
            }
            df_all = pd.DataFrame()
            # Re-create the portfolio dataframe from the account dataframes.
            for a in accounts:
                df_all_s = a["df"].loc[re_date, cols_acct]
                df_all_s.name = (a["owner"], a["account_type"])
                df_all_s.index = df_all_s.index.map(convert)

                # If the dataframe is empty, create it, else concat
                if df_all.empty:
                    df_all = pd.DataFrame(df_all_s)
                else:
                    df_all = pd.concat([df_all, pd.DataFrame(df_all_s)], axis=1)
            # Reshape the dataframe to put the multi index on the correct axis.
            df_all = df_all.T
            # Copy and create the 'new' dataframe and populate with zeros.
            df_all_new = df_all.copy()
            df_all_new[:] = 0
            # Join the two together.
            df_all = pd.concat([df_all, df_all_new], axis=1, keys=["invested", "new"])
            df = df_all


if __name__ == "__main__":

    # Project parameters.

    # Project time envelope.
    start_date = "2002-01-01"
    end_date = "2018-12-31"

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

    # Accounts by order of importance for equity investing and least important for cash.
    # accounts = [at.p1_inv, at.p1_rsp, at.p1_tfsa]
    accounts = [at.p2_inv, at.p1_inv, at.p2_rsp, at.p1_rsp, at.p2_tfsa, at.p1_tfsa]

    # Clear deposits in the dictionaries.
    for act in accounts:
        act["dep_with"] = {}
        act["end_date"] = end_date

    # Place initial deposits to the accounts.
    at.p1_inv["dep_with"][start_date] = 100000
    at.p1_rsp["dep_with"][start_date] = 100000
    at.p1_tfsa["dep_with"][start_date] = 100000
    at.p2_inv["dep_with"][start_date] = 100000
    at.p2_rsp["dep_with"][start_date] = 100000
    at.p2_tfsa["dep_with"][start_date] = 100000

    # Dataframe with two columns, returns for portfolio and for accounts
    returns, asset_allocation = rebalance_portfolio(
        port_allocation, accounts, start_date, end_date
    )

    end = "end"
