import os
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmissionsDataLoader:
    def __init__(self, data_path):
        self.data_path = Path(data_path)

    def load_data(self, files: List[str]):
        """
        Load emissions inventory data from files

        params:
            files: List[str], List of files to load
        returns:
            Dict, Dictionary of dataframes
        """
        data = {}
        for i, file in enumerate(files):
            data[f'scope{i+1}_df'] = pd.read_csv(os.path.join(self.data_path, file))
        return data