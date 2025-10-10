import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import re

class EmissionsQualityAssessor:
    """Simple assessor for emissions inventory quality"""
    
    def __init__(self):
        pass
        
    def assess_scope2_validity(self, scope2_data: pd.DataFrame) -> Dict:
        """
        Simple validation: Are Scope 2 emissions calculations valid according to GHG Protocol?
        
        Things to check:
        1. Basic data structure
        2. Required columns(co2e emission)/data for GHG Protocol
            2.1. Must include electricity, steam, heating, and cooling
            2.2. Should contain two reporting methods: location-based, market-based
                In order to compute location-based emissions, it must include Emission factor and Consumption amount
                and market-based emissions, it must include Renewable percentage
        3. Accounting method (GHG Protocol requirement)
        4. Data quality - no negative emissions
        """
        issues = []
        summary = []
        validity_threshold = 100
        # Check 1: Basic data structure
        if scope2_data.empty:
            return {
                "is_valid": False,
                "score": 0,
                "issues": ["No Scope 2 data provided"],
                "summary": "Invalid: No data to validate"
            }
        
        # Check 2: Required columns/data for GHG Protocol
        required_cols = ['CO2e_Tonnes']
        scope2_cols = scope2_data.columns   
        missing_cols = [col for col in required_cols if col not in scope2_cols]
        if missing_cols:
            issues.append(f"Missing required columns: {required_cols}', '.join(missing_cols)")
        else:
            summary.append(f"From required column list {required_cols}, all are present")
        
        location_based_possible = False
        market_based_possible = False
        # 2.2. Check if we can compute location-based emissions
        if 'Emission_Factor' in scope2_cols and 'Consumption_Amount' in scope2_cols:
            location_based_possible = True
            # Check if at least one record is negative (this also checks Null.)
            invalid_emission_factor = (scope2_data['Emission_Factor'] < 0).sum()
            invalid_consumption_amount =  (scope2_data['Consumption_Amount'] < 0).sum()
            if invalid_emission_factor > 0 and invalid_consumption_amount > 0:
                issues.append(f"Negative values in Emission_Factor or Consumption_Amount columns")
            else:
                summary.append("No negative values in Emission_Factor or Consumption_Amount columns")
        else:
            issues.append("Cannot compute location-based emissions: missing Emission_Factor or Consumption_Amount")
        
        # Check if we can compute market-based emissions
        if 'Renewable_Percentage' in scope2_data.columns:
            market_based_possible = True
            # Market-based emissions would be lower due to renewable energy
            renewable_avg = scope2_data['Renewable_Percentage'].mean()
            if renewable_avg <= 0:
                issues.append("No renewable energy data available for market-based calculation")
            else:
                summary.append(f"There are Renewable percentage available with value: {renewable_avg:.2f}% so that we can compute market-based emissions")
        else:
            issues.append("Cannot compute market-based emissions: missing Renewable_Percentage data")
        
        # Check 4: Data quality - no negative emissions
        if 'CO2e_Tonnes' in scope2_data.columns:
            negative_emissions = (scope2_data['CO2e_Tonnes'] < 0).sum()
            if negative_emissions > 0:
                issues.append(f"{negative_emissions} records have negative emissions")
            else:
                summary.append(f"No negative emissions found in CO2e_Tonnes column")
        
        # Calculate simple score
        score = max(0, 100 - len(issues) * 25)  # -25 points per issue
        is_valid = score >= validity_threshold
        
        return {
            # "is_valid": is_valid,
            # "score": score,
            "issues": issues,
            "location_based_possible": location_based_possible,
            "market_based_possible": market_based_possible,
            "summary": ", ".join(summary)
        }