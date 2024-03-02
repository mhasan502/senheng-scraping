import os
import pandas as pd


class DataSaver:
    def __init__(self):
        self.collected_data = []

    def __reset__(self):
        self.collected_data.clear()

    def add_data(self, data: dict) -> None:
        self.collected_data.append(data)

    def save_data(self, file_name: str) -> None:
        if not os.path.exists("csvs"):
            os.makedirs("csvs")
        pd.DataFrame(self.collected_data).to_csv(f"csvs/{file_name}.csv", index=False)
        print(f"The data of {file_name} has been saved.")
        self.__reset__()
