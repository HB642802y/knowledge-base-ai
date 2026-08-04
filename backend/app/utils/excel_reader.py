from pathlib import Path
import pandas as pd


class ExcelReader:

    def __init__(self, file_path: Path):
        self.file_path = file_path

    def read(self) -> str:

        excel = pd.ExcelFile(self.file_path)

        text = ""

        for sheet in excel.sheet_names:

            df = excel.parse(sheet)

            text += f"\n--- {sheet} ---\n"

            text += df.to_string(index=False)

        return text 