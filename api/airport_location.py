import pandas as pd
import os

PATH = os.path.abspath(os.getcwd())
file_path = "\\api\\airports-code@public.csv"
df = pd.read_csv(PATH + file_path, sep=';')


def get_airport_coordinates(airport_code):
    """
    Получает широту и долготу аэропорта по его IATA-коду.
    """
    result = df[df["Airport Code"] == airport_code][["Latitude", "Longitude"]]
    if not result.empty:
        return result.iloc[0]["Latitude"], result.iloc[0]["Longitude"]
    return None, None
