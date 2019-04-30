import rebalance_account as ra
import account_templates as at

test_var_d = at.inv
df = ra.rebalance_account(test_var_d)

securities = ["XBB", "XIC", "TD_Bond", "TD_CDN_Equity"]


def test_total_value_norm_start_value():
    # print(t.total_value_norm[0])
    assert df.total_value_norm[0] == 1.0


def test_cash_start_value():
    assert df.total_value_norm[0] == 1.0


def test_total_dividends_and_real_gains():
    # < 2 accounts for rounding errors
    assert (
        df[["tax_gain", "tax_dividend"]].sum().sum()
        - df.loc[df.index[-1], "tax_realized"]
        < 2
    )


def test_dividends_negative():
    assert any(df["dividends"] > 0), "Negative dividend usually means negative units"


def test_units_negative():
    # This is returning true, should be false.
    df_unit_negative = df.loc[
        (df["XBB-unit"] < 0)
        | (df["XIC-unit"] < 0)
        | (df["TD_Bond-unit"] < 0)
        | (df["TD_CDN_Equity-unit"] < 0),
        ["XBB-unit", "XIC-unit", "TD_Bond-unit", "TD_CDN_Equity-unit"],
    ]

    assert df_unit_negative.empty, df_unit_negative


def test_sum_dividends():
    # Test all individual dividends add up to dividends column.
    securities = ["XBB", "XIC", "TD_Bond", "TD_CDN_Equity"]
    df["temp"] = 0
    for sec in securities:
        df["temp"] += df[sec + "-unit"] * df[sec + "-dividends"]
    filt = (df["dividends"] - df["temp"]) > 0
    assert df[filt].empty, df.loc[filt, "dividends"]
