def create_features(df):
    df = df.copy()

    df["snapshot_date"] = pd.to_datetime(df["snapshot_date"])
    df = df.sort_values("snapshot_date").reset_index(drop=True)

    df["daily_change"] = df["active_offers"].diff()
    df["daily_change_pct"] = df["active_offers"].pct_change() * 100

    for lag in [1, 2, 3, 7]:
        df[f"lag_{lag}"] = df["active_offers"].shift(lag)

    for window in [3, 7]:
        df[f"rolling_mean_{window}"] = (
            df["active_offers"]
            .shift(1)
            .rolling(window=window)
            .mean()
        )

    return df