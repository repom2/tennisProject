import pandas as pd
from sklearn.preprocessing import LabelEncoder
from tennisapi.ml.features import features, loser_features, winner_features


def label_round_name(data):
    le = LabelEncoder()
    label = le.fit_transform(data["round_name"])
    name_mapping = dict(zip(le.classes_, le.transform(le.classes_)))
    data["round_name"] = label

    return data, name_mapping


def balance_train_data(data):
    # shuffle the DataFrame rows
    data = data.sample(frac=1)
    data_length = int(round(len(data.index) / 2, 0))
    print("split", data_length)
    df1 = data.iloc[:data_length, :]
    df2 = data.iloc[data_length:, :]
    print("df", len(data), len(df1), len(df2))

    # Dont change because have to match with sql
    columns = (
        ["start_at", "home_name", "away_name", "round_name"]
        + winner_features()
        + loser_features()
        + ["winner_code"]
    )

    revert_columns = (
        ["start_at", "home_name", "away_name", "round_name"]
        + loser_features()
        + winner_features()
        + ["winner_code"]
    )

    df2 = df2[revert_columns]
    df2["winner_code"] = 0
    df2.columns = columns

    merge_df = pd.concat([df1, df2])

    train_data, round_mapping = label_round_name(merge_df)

    print(train_data.head())

    return train_data, round_mapping
