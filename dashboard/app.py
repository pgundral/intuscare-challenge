from faicons import icon_svg
from shinyswatch import theme

import pandas as pd
from base_solution import solution, patient_data

from shiny import App, reactive, render, ui
from shiny.types import FileInfo

app_ui = ui.page_fluid( 
    ui.page_sidebar(
    ui.sidebar(
        ui.input_select("model", "Select the transformation method:",
                        {"base": "Base", "opt": "Vectorized", "async": "Batch API"}),
        ui.input_file("data", "Choose JSON File", accept=[".json"], multiple=False),
        ui.input_text_area("manual_data", "Manually Input Data"),
        ui.input_action_button("button", "TRANSFORM"),
        title="OPTIONS",
        width = 400
    ),
    ui.layout_columns(
        ui.card(
            ui.card_header("INPUT DATA"),
            ui.output_data_frame("display_input_data"),
            full_screen=True,
        ),
        ui.card(
            ui.card_header("OUTPUT DATA"),
            ui.output_data_frame("display_output_data"),
            full_screen=True,
        ),
    ),
    ui.card(
        ui.card_header("METRICS"),
        height = 300,
        full_screen=True
    ),
    fillable=True,
    title = "DASHBOARD"
    ), 
title="Dashboard",
theme = theme.lux)


def server(input, output, session):
    @reactive.calc
    def patient_data():
        file: list[FileInfo] | None = input.data()
        if file is None:
            return pd.DataFrame()
        return pd.read_json(file[0]["datapath"]
        )
    
    @reactive.event(input.button)
    def output():
        return solution(patient_data())

    # @reactive.file_reader("data.json")
    # def read_patient_data():
    #     return pd.read_json(input.data.datapath)
        
    # @reactive.calc
    # def transform():
    #     filt_df = df[df["species"].isin(input.species())]
    #     filt_df = filt_df.loc[filt_df["body_mass_g"] < input.mass()]
    #     return filt_df

    # @render.data_frame
    # def display_input_data():
    #     df = pd.DataFrame(read_patient_data())
    #     df['diagnoses'] = df['diagnoses'].apply(lambda x: ', '.join(map(str, x)) if x else 'None')
    #     return render.DataGrid(df)

    @render.data_frame
    def display_input_data():
        return pd.DataFrame(patient_data())
    
    @render.data_frame
    def display_output_data():
        return pd.DataFrame(output())


app = App(app_ui, server)
