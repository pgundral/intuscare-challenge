from faicons import icon_svg
from shinyswatch import theme

import pandas as pd
from base_solution import patient_data
from base_solution import solution as base_s
from optimized_solution import solution as opt_s
# from async_solution import solution as async_s

from shiny import App, reactive, render, ui
from shiny.types import FileInfo
import json
import cProfile, pstats
import io

def solution_profiler(fx, data):
    # Create a profiler using cProfile
    profiler = cProfile.Profile()

    # Run the profiler around the fx
    profiler.enable()
    fx(data)
    profiler.disable()

    # Capture the pstats analysis using io
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats(pstats.SortKey.TIME)
    ps.print_stats(10)

    # Format the data
    lines = s.getvalue().split("\n")
    data = [line.split(None, 5) for line in lines[5:-2] if line]
    columns = ["ncalls", "tottime", "percall", "cumtime", "percall2", "filename"]
    
    # Clean the data and convert to DataFrame
    df = pd.DataFrame(data, columns=columns).dropna()

    # Return the function result along with the analysis
    return df[["filename", "tottime", "cumtime"]]


app_ui = ui.page_fluid( 
    ui.page_sidebar(
    ui.sidebar(
        ui.input_select("model", "Select the transformation method:",
                        {"base": "Base", "opt": "Optimized"}),
        ui.input_file("data", "Choose JSON File", accept=[".json"], multiple=False),
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
        ui.output_data_frame("metrics"),
        height = 300,
        full_screen=True
    ),
    fillable=True,
    title = "DASHBOARD"
    ), 
title="Dashboard",
theme = theme.lux)


def server(input, output, session):

    modelsdict = {"base": base_s, "opt": opt_s}

    @reactive.calc
    def patient_data():
        file: list[FileInfo] | None = input.data()
        if file is None:
            return pd.DataFrame()
        with open(file[0]["datapath"], "r") as f:
            loaded_data = json.load(f)
        return loaded_data

    selected_solution = reactive.Value(base_s)

    @reactive.effect
    def switch_model():
        choice = input.model()
        selected_solution.set(modelsdict[choice])

    @reactive.event(input.button)
    def transform():
        return selected_solution.get()(patient_data())
    
    @reactive.event(input.button)
    def get_metrics():
        models = {"base": base_s, "opt": opt_s}
        return solution_profiler(selected_solution.get(), patient_data())

    @render.data_frame
    def display_input_data():
        return pd.DataFrame(patient_data())
    
    @render.data_frame
    def display_output_data():
        return pd.DataFrame(transform())
    
    @render.data_frame
    def metrics():
        return pd.DataFrame(get_metrics())


app = App(app_ui, server)
