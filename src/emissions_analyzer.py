import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class EmissionsInsight:
    """Container for emissions insights"""
    category: str
    value: float
    percentage: float
    trend: str
    recommendation: str

class EmissionsAnalyzer:
    """Analyze emissions data and generate insights"""
    
    def __init__(self, data: Dict[str, pd.DataFrame]):
        self.scope1_data = data.get("scope1_df")
        self.scope2_data = data.get("scope2_df")
        self.scope3_data = data.get("scope3_df")
        
    def calculate_total_emissions(self) -> Dict[str, float]:
        """Calculate total emissions by scope"""
        totals = {}
        
        if self.scope1_data is not None and 'CO2e_Tonnes' in self.scope1_data.columns:
            totals['scope1'] = self.scope1_data['CO2e_Tonnes'].sum()
        
        if self.scope2_data is not None and 'CO2e_Tonnes' in self.scope2_data.columns:
            totals['scope2'] = self.scope2_data['CO2e_Tonnes'].sum()
            
        if self.scope3_data is not None and 'CO2e_Tonnes' in self.scope3_data.columns:
            totals['scope3'] = self.scope3_data['CO2e_Tonnes'].sum()
        
        totals['total'] = sum(totals.values())
        
        return totals
    
    def identify_top_emitters(self, scope: int, top_n: int = 5) -> pd.DataFrame:
        """Identify top emission sources within a scope"""
        scope_map = {
            1: self.scope1_data,
            2: self.scope2_data,
            3: self.scope3_data
        }
        
        df = scope_map.get(scope)
        if df is None or df.empty:
            return pd.DataFrame()
        
        # Group by category/activity
        if 'Category' in df.columns:
            grouped = df.groupby('Category')['CO2e_Tonnes'].sum()
        elif 'Activity_Description' in df.columns:
            grouped = df.groupby('Activity_Description')['CO2e_Tonnes'].sum()
        
        return grouped.nlargest(top_n).reset_index()