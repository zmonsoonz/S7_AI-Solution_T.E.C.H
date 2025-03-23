import pandas as pd

import ml_funcs


def main():
    data = pd.read_csv("flights_dataset.csv").drop(["TAXI_OUT", "Unnamed: 0"], axis=1)
    ml_funcs.training_and_predict(data)


if __name__ == "__main__":
    main()
