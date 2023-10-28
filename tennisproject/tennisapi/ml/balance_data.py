from tennisapi.ml.features import features, loser_features, winner_features
import pandas as pd
from sklearn.preprocessing import LabelEncoder


def label_round_name(data):
    le = LabelEncoder()
    label = le.fit_transform(data['round_name'])
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
    print('df', len(data), len(df1), len(df2))

    # Dont change because have to match with sql
    columns = [
        'date',
        'winner_name',
        'loser_name',
        'round_name'
        ] + winner_features() + loser_features() + ['result']

    revert_columns = [
        'date',
        'loser_name',
        'winner_name',
        'round_name'
        ] + loser_features() + winner_features() + ['result']

    df2 = df2[revert_columns]
    df2["result"] = 0
    df2.columns = columns

    merge_df = pd.concat([df1, df2])

    train_data, round_mapping = label_round_name(merge_df)

    print(train_data.head())

    return train_data, round_mapping
