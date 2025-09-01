import os
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmissionsDataLoader:
    """Load and preprocess emissions inventory data from CSV files"""
    
    def __init__(self, data_path):
        self.data_path = Path(data_path)

    def load_data(self, files: List[str]):
        data = {}
        for i, file in enumerate(files):
            data[f'scope{i+1}_df'] = pd.read_csv(os.path.join(self.data_path, file))
        return data
        
    def get_combined_data(self) -> pd.DataFrame:
        """Combine all scope data into single dataframe"""
        if not all([self.scope1_data is not None, 
                   self.scope2_data is not None, 
                   self.scope3_data is not None]):
            self.load_all_scopes()
        
        combined = pd.concat([
            self.scope1_data,
            self.scope2_data,
            self.scope3_data
        ], ignore_index=True)
        
        return combined