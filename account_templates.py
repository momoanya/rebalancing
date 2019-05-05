"""
DATE RANGE: must be between 2002-01-01 and 2018-12-31.
"""

# Testing variables dict used when calling rebalance_account() 
# from rebalance_account.py
# Following are two sample dictionaries, one with notes, one without, 
# followed by dictionaries used in production.

# Dict with comments
dict_with_notes = {
    # Account name, format should reflect nature of account.
    "name": "Investment No Drip",
    # One line description of the account
    "description": "Investment without a DRIP program",
    # The date range for analysis,
    # must be between 2002-01-01 and 2018-12-31.
    "start_date": "2001-01-01",
    "end_date": "2011-12-31",
    # All deposits including initial deposit should be stated here.
    # List of dates and deposits/withdrawals in dictionary format.
    # Negative number for withdrawals. The dates in the template are
    # the defaults.
    "dep_with": {"2002-01-01": 100000},
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
    "rebalance_period": "M",
    # Trading Fees
    # Trade_fee or slippage defaults to $7.50, 0 if no fee.
    "trade_fee": 7.50,
    # Minimum trade size.
    "minimum_trade_dollar": 0.00,
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

# Dict without comments
dnc = {
    "name": "Investment No Drip",
    "description": "Investment without a DRIP program",
    "start_date": "2002-01-01",
    "end_date": "2005-01-01",
    "dep_with": {"2002-01-01": 100000},
    "taxable_transactions": True,
    "taxable_withdrawal": False,
    "tax_rate": 0.3148,
    "tax_div": 0.0892,
    "tax_gains": 0.1574,
    "rebalance_period": "M",
    "trade_fee": 7.50,
    "minimum_trade_dollar": 100.0,
    "drip": False,
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


# Three dictionaries used during account level testing: 
# inv: Taxable investment acccount.
# rsp: RRSP account.
# tfsa: Tax free savings account.

inv = {
    "name": "Investment Account",
    "description": "Sample taxable investment account.",
    "start_date": "2002-01-01",
    "end_date": "2011-12-31",
    "dep_with": {"2002-01-01": 100000},
    "taxable_transactions": True,
    "taxable_withdrawal": False,
    "tax_rate": 0.4341,
    "tax_div": 0.2952,
    "tax_gains": 0.2170,
    "rebalance_period": "M",
    "trade_fee": 7.50,
    "minimum_trade_dollar": 0.0,
    "drip": False,
    "mutual_funds": False,
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

rsp = {
    "name": "Registerer Retirement Savings Plan",
    "description": "Sample RRSP account.",
    "start_date": "2002-01-01",
    "end_date": "2011-12-31",
    "dep_with": {"2002-01-01": 176709.6660187312},
    "taxable_transactions": False,
    "taxable_withdrawal": True,
    "tax_rate": 0.4341,
    "tax_div": 0.2952,
    "tax_gains": 0.2170,
    "rebalance_period": "M",
    "trade_fee": 7.50,
    "minimum_trade_dollar": 0.0,
    "drip": False,
    "mutual_funds": False,
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


tfsa = {
    "name": "Tax Free Savings Account",
    "description": "Sample tfsa investment account.",
    "start_date": "2002-01-01",
    "end_date": "2011-12-31",
    "dep_with": {"2002-01-01": 100000},
    "taxable_transactions": False,
    "taxable_withdrawal": False,
    "tax_rate": 0.4341,
    "tax_div": 0.2952,
    "tax_gains": 0.2170,
    "rebalance_period": "M",
    "trade_fee": 7.50,
    "minimum_trade_dollar": 0.0,
    "drip": False,
    "mutual_funds": False,
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

# params: Used for testing during build.
params = {
    "name": "Scenario Dictionary",
    "description": "Values will be set manually by the loops",
    "start_date": "2002-01-01",
    "end_date": "2018-12-31",
    "dep_amount": 100000,
    "dep_with": {"2002-01-01": 100000},
    "taxable_transactions": True,
    "taxable_withdrawal": False,
    "tax_rate": 0.3148,
    "tax_div": 0.0892,
    "tax_gains": 0.1574,
    "rebalance_period": "M",
    "trade_fee": 7.50,
    "minimum_trade_dollar": 0.0,
    "drip": False,
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


# Six dictionaries with values used for rebalance_portfolio()
# and also scenario testing. There are two persons, p1 and p2.
# Each person has an inv, rsp, tfsa account. 

# Person one.
p1_inv = {
    # Account name, format should reflect nature of account.
    "name": "p1_inv",
    # One line description of the account
    "description": "Person 1 investment account",
    # owner
    "owner": "p1",
    # account type
    "account_type": "inv",
    # The date range for analysis,
    # must be between 2002-01-01 and 2018-12-31.
    "start_date": "2001-01-01",
    "end_date": "2009-12-31",
    # All deposits including initial deposit should be stated here.
    # List of dates and deposits/withdrawals in dictionary format.
    # Negative number for withdrawals. The dates in the template are
    # the defaults.
    "dep_with": {},
    # Transactions subject to tax
    # TFSA:          transactions = False,      withdrawals = False
    # RRSP:          transaeections = False,      withdrawals = True
    # Taxable:       transactions = True,      withdrawals = False
    "taxable_transactions": True,
    # RRSPs have tax on withdrawal, this shown accrued in taxes
    "taxable_withdrawal": False,
    # Marginal tax rates for Ontario at $75,000 income
    # for general tax like rsp withdrawal or interest income.
    "tax_rate": 0.41,
    # Tax rate on Canadian dividends as a percent of tax_rate.
    "tax_div": 0.1162,
    # Inclusion rate tax rate on capital gains realized.
    "tax_gains": 0.205,
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
    "minimum_trade_dollar": 0.0,
    # Dividends reinvested with no cost, drip=True
    # otherwise to cash for later rebalancing.
    "drip": False,
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


p1_rsp = {
    # Account name, format should reflect nature of account.
    "name": "p1_rsp",
    # One line description of the account
    "description": "Person 1 RRSP account",
    # owner
    "owner": "p1",
    # account type
    "account_type": "rsp",
    # The date range for analysis,
    # must be between 2002-01-01 and 2018-12-31.
    "start_date": "2003-01-03",
    "end_date": "2009-12-31",
    # All deposits including initial deposit should be stated here.
    # List of dates and deposits/withdrawals in dictionary format.
    # Negative number for withdrawals. The dates in the template are
    # the defaults.
    "dep_with": {},
    # Transactions subject to tax
    # TFSA:          transactions = False,      withdrawals = False
    # RRSP:          transaeections = False,      withdrawals = True
    # Taxable:       transactions = True,      withdrawals = False
    "taxable_transactions": False,
    # RRSPs have tax on withdrawal, this shown accrued in taxes
    "taxable_withdrawal": True,
    # Marginal tax rates for Ontario at $75,000 income
    # for general tax like rsp withdrawal or interest income.
    "tax_rate": 0.41,
    # Tax rate on Canadian dividends as a percent of tax_rate.
    "tax_div": 0.1162,
    # Inclusion rate tax rate on capital gains realized.
    "tax_gains": 0.205,
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
    "minimum_trade_dollar": 0.0,
    # Dividends reinvested with no cost, drip=True
    # otherwise to cash for later rebalancing.
    "drip": False,
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


p1_tfsa = {
    # Account name, format should reflect nature of account.
    "name": "p1_tfsa",
    # One line description of the account
    "description": "Person 1 tfsa",
    # owner
    "owner": "p1",
    # account type
    "account_type": "tfsa",
    # The date range for analysis,
    # must be between 2002-01-01 and 2018-12-31.
    "start_date": "2003-01-03",
    "end_date": "2009-12-31",
    # All deposits including initial deposit should be stated here.
    # List of dates and deposits/withdrawals in dictionary format.
    # Negative number for withdrawals. The dates in the template are
    # the defaults.
    "dep_with": {},
    # Transactions subject to tax
    # TFSA:          transactions = False,      withdrawals = False
    # RRSP:          transaeections = False,      withdrawals = True
    # Taxable:       transactions = True,      withdrawals = False
    "taxable_transactions": False,
    # RRSPs have tax on withdrawal, this shown accrued in taxes
    "taxable_withdrawal": False,
    # Marginal tax rates for Ontario at $75,000 income
    # for general tax like rsp withdrawal or interest income.
    "tax_rate": 0.41,
    # Tax rate on Canadian dividends as a percent of tax_rate.
    "tax_div": 0.1162,
    # Inclusion rate tax rate on capital gains realized.
    "tax_gains": 0.205,
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
    "minimum_trade_dollar": 0.0,
    # Dividends reinvested with no cost, drip=True
    # otherwise to cash for later rebalancing.
    "drip": False,
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


# Person two.
p2_inv = {
    # Account name, format should reflect nature of account.
    "name": "p2_inv",
    # One line description of the account
    "description": "Person 2 investment account",
    # owner
    "owner": "p2",
    # account type
    "account_type": "inv",
    # The date range for analysis,
    # must be between 2002-01-01 and 2018-12-31.
    "start_date": "2003-01-03",
    "end_date": "2009-12-31",
    # All deposits including initial deposit should be stated here.
    # List of dates and deposits/withdrawals in dictionary format.
    # Negative number for withdrawals. The dates in the template are
    # the defaults.
    "dep_with": {},
    # Transactions subject to tax
    # TFSA:          transactions = False,      withdrawals = False
    # RRSP:          transaeections = False,      withdrawals = True
    # Taxable:       transactions = True,      withdrawals = False
    "taxable_transactions": True,
    # RRSPs have tax on withdrawal, this shown accrued in taxes
    "taxable_withdrawal": False,
    # Marginal tax rates for Ontario at $75,000 income
    # for general tax like rsp withdrawal or interest income.
    "tax_rate": 0.2,
    # Tax rate on Canadian dividends as a percent of tax_rate.
    "tax_div": 0.05,
    # Inclusion rate tax rate on capital gains realized.
    "tax_gains": 0.1,
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
    "minimum_trade_dollar": 0.0,
    # Dividends reinvested with no cost, drip=True
    # otherwise to cash for later rebalancing.
    "drip": False,
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


p2_rsp = {
    # Account name, format should reflect nature of account.
    "name": "p2_rsp",
    # One line description of the account
    "description": "Person 2 RRSP account",
    # owner
    "owner": "p2",
    # account type
    "account_type": "rsp",
    # The date range for analysis,
    # must be between 2002-01-01 and 2018-12-31.
    "start_date": "2003-01-03",
    "end_date": "2012-12-31",
    # All deposits including initial deposit should be stated here.
    # List of dates and deposits/withdrawals in dictionary format.
    # Negative number for withdrawals. The dates in the template are
    # the defaults.
    "dep_with": {},
    # Transactions subject to tax
    # TFSA:          transactions = False,      withdrawals = False
    # RRSP:          transaeections = False,      withdrawals = True
    # Taxable:       transactions = True,      withdrawals = False
    "taxable_transactions": False,
    # RRSPs have tax on withdrawal, this shown accrued in taxes
    "taxable_withdrawal": True,
    # Marginal tax rates for Ontario at $75,000 income
    # for general tax like rsp withdrawal or interest income.
    "tax_rate": 0.2,
    # Tax rate on Canadian dividends as a percent of tax_rate.
    "tax_div": 0.05,
    # Inclusion rate tax rate on capital gains realized.
    "tax_gains": 0.1,  # Schedule for portfolio rebalancing,
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
    "minimum_trade_dollar": 0.0,
    # Dividends reinvested with no cost, drip=True
    # otherwise to cash for later rebalancing.
    "drip": False,
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


p2_tfsa = {
    # Account name, format should reflect nature of account.
    "name": "p2_tfsa",
    # One line description of the account
    "description": "Person 2 tfsa",
    # owner
    "owner": "p2",
    # account type
    "account_type": "tfsa",
    # The date range for analysis,
    # must be between 2002-01-01 and 2018-12-31.
    "start_date": "2003-01-03",
    "end_date": "2012-12-31",
    # All deposits including initial deposit should be stated here.
    # List of dates and deposits/withdrawals in dictionary format.
    # Negative number for withdrawals. The dates in the template are
    # the defaults.
    "dep_with": {},
    # Transactions subject to tax
    # TFSA:          transactions = False,      withdrawals = False
    # RRSP:          transaeections = False,      withdrawals = True
    # Taxable:       transactions = True,      withdrawals = False
    "taxable_transactions": False,
    # RRSPs have tax on withdrawal, this shown accrued in taxes
    "taxable_withdrawal": False,
    # Marginal tax rates for Ontario at $75,000 income
    # for general tax like rsp withdrawal or interest income.
    "tax_rate": 0.2,
    # Tax rate on Canadian dividends as a percent of tax_rate.
    "tax_div": 0.05,
    # Inclusion rate tax rate on capital gains realized.
    "tax_gains": 0.1,
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
    "minimum_trade_dollar": 0.0,
    # Dividends reinvested with no cost, drip=True
    # otherwise to cash for later rebalancing.
    "drip": False,
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
