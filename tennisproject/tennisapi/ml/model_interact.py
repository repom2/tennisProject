import numpy as np
import joblib
import os
import pandas as pd
import gradio as gr


def feature_importance():
    local_path = os.getcwd() + '/tennisapi/ml/trained_models/'

    file_name = "roland_garros_wta_model"
    file_path = local_path + file_name

    model = joblib.load(file_path)
    features = model.feature_names
    round_mapping = model.round_mapping
    importances = model.feature_importances

    importances = pd.DataFrame(data={
        'Attribute': features,
        'Importance': importances
    })
    importances = importances.sort_values(by='Importance', ascending=False)

    print(importances)

    round_mapping = model.round_mapping

    def predict_flower(
            round_name,
            winner_games,
            loser_games,
            winner_elo,
            loser_elo,
            winner_hardelo,
            loser_hardelo,
            winner_year_games,
            loser_year_games,
            winner_win_percent,
            loser_win_percent
    ):
        round_name = round_mapping[round_name]

        df = pd.DataFrame.from_dict(
            {
                'round_name': [round_name],
                'winner_games': [winner_games],
                'loser_games': [loser_games],
                'winner_elo': [winner_elo],
                'loser_elo': [loser_elo],
                'winner_hardelo': [winner_hardelo],
                'loser_hardelo': [loser_hardelo],
                'winner_year_games': [winner_year_games],
                'loser_year_games': [loser_year_games],
                'winner_win_percent': [winner_win_percent],
                'loser_win_percent': [loser_win_percent],
            }
        )
        predict = model.predict_proba(df)[0]

        output_dict = {}

        for i in range(2):
            pred = predict[i]
            label = model.classes_[i]
            if label == 0:
                label = "Away"
            elif label == 1:
                label = "Home"
            output_dict[label] = pred

        return output_dict

    round_name = gr.Dropdown(choices=round_mapping, label='Round Name', value=list(round_mapping.values())[0])

    winner_games = gr.inputs.Slider(
        minimum=1, maximum=200, default=33, step=1, label="winner_games"
    )
    loser_games = gr.inputs.Slider(
        minimum=1, maximum=200, default=33, step=1, label="loser_games"
    )
    winner_elo = gr.inputs.Slider(
        minimum=0, maximum=2400, default=1700, step=60, label="winner_elo"
    )
    loser_elo = gr.inputs.Slider(
        minimum=0, maximum=2400, default=1700, step=60, label="loser_elo"
    )
    winner_hardelo = gr.inputs.Slider(
        minimum=0, maximum=2400, default=1600, step=60, label="winner_hardelo"
    )
    loser_hardelo = gr.inputs.Slider(
        minimum=0, maximum=2400, default=1600, step=60, label="loser_hardelo"
    )
    winner_year_games = gr.inputs.Slider(
        minimum=1, maximum=70, default=10, step=1, label="winner_year_games"
    )
    loser_year_games = gr.inputs.Slider(
        minimum=1, maximum=70, default=10, step=1, label="loser_year_games"
    )
    winner_win_percent = gr.inputs.Slider(
        minimum=0, maximum=100, default=0.5, step=60,
        label="winner_win_percent"
    )
    loser_win_percent = gr.inputs.Slider(
        minimum=0, maximum=100, default=0.5, step=300,
        label="loser_win_percent"
    )

    demo = gr.Interface(
        fn=predict_flower,
        inputs=[
            round_name,
            winner_games,
            loser_games,
            winner_elo,
            loser_elo,
            winner_hardelo,
            loser_hardelo,
            winner_year_games,
            loser_year_games,
            winner_win_percent,
            loser_win_percent
        ],
        outputs="label",
        live=True,
        interpretation="default",
        title="Trained Model"
    )

    demo.launch(debug=True, share=True)
