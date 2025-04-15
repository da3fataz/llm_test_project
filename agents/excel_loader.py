
"""
Excel Loader Agent with exact text matching
- Supports NC_llm_judge_testcase.xlsx format
- Looks for exact matches for '질문', '정답', '결과', etc.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
import os

class AgentState(dict):
    """Base agent state class"""
    def __init__(self, 
                 agent_id: str = "", 
                 status: str = "initialized",
                 messages: List[Dict] = None, 
                 data: Dict = None,
                 errors: List[str] = None,
                 results: Dict = None):
        super().__init__()
        self["agent_id"] = agent_id
        self["status"] = status  # initialized, running, completed, failed
        self["messages"] = messages or []
        self["data"] = data or {}
        self["errors"] = errors or []
        self["results"] = results or {}

class ExcelLoaderAgent:
    """Agent that loads Excel files"""
    
    def __init__(self, agent_id: str = "excel_loader"):
        self.agent_id = agent_id
    
    def load_excel(self, state: AgentState) -> AgentState:
        """Function to load Excel files"""
        file_path = state["data"].get("file_path")
        sheet_name = state["data"].get("sheet_name")
        
        try:
            if not file_path:
                raise ValueError("File path not specified.")
            
            if not os.path.exists(file_path):
                raise ValueError(f"File not found: {file_path}")
            
            # Save original file info
            state["data"]["original_file_path"] = file_path
            state["data"]["original_sheet_name"] = sheet_name
            
            # Load Excel file (without header)
            if sheet_name:
                xl = pd.ExcelFile(file_path)
                if sheet_name not in xl.sheet_names:
                    raise ValueError(f"Sheet not found: {sheet_name}")
                raw_df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
            else:
                raw_df = pd.read_excel(file_path, header=None)
            
            # Find header cells with exact text match
            header_texts = ["질문", "정답", "결과", "소요시간", "점수"]
            header_positions = {}
            
            for text in header_texts:
                for i in range(raw_df.shape[0]):
                    for j in range(raw_df.shape[1]):
                        # Check for exact match
                        cell_value = str(raw_df.iloc[i, j]).strip()
                        if cell_value == text:
                            header_positions[text] = (i, j)
                            # Debug output
                            print(f"Found '{text}' cell: position ({i}, {j})")
                            break
                    if text in header_positions:
                        break
            
            # Check required headers
            required_headers = ["질문", "정답", "결과"]
            missing_headers = [h for h in required_headers if h not in header_positions]
            
            if missing_headers:
                # Debug output
                found_headers = list(header_positions.keys())
                print(f"Found headers: {found_headers}")
                print(f"Missing headers: {missing_headers}")
                # Excel content sample output
                print("Excel file content sample:")
                print(raw_df.head(10))
                
                raise ValueError(f"Required headers not found: {', '.join(missing_headers)}")
            
            # Extract data
            data = {}
            for header, (row, col) in header_positions.items():
                data[header] = []
                # Extract data from below header cell
                for i in range(row + 1, raw_df.shape[0]):
                    value = raw_df.iloc[i, col]
                    if pd.isna(value) or str(value).strip() == "":
                        if len(data[header]) > 0:  # Stop if we already extracted data and encountered empty cell
                            break
                        continue  # Skip empty values
                    data[header].append(value)
            
            # Ensure all required headers have data
            for header in required_headers:
                if not data[header]:
                    raise ValueError(f"No data found for '{header}' column")
            
            # Find the maximum length for required columns
            max_required_len = max(len(data[h]) for h in required_headers)
            
            # Adjust data length (ensure all required columns have the same length)
            for header in required_headers:
                # Extend shorter arrays if needed
                while len(data[header]) < max_required_len:
                    data[header].append(None)  # Add None for missing values
            
            # Handle optional columns
            for header in header_positions:
                if header not in required_headers:
                    # If column exists but doesn't have enough data, add empty values
                    if header in data:
                        while len(data[header]) < max_required_len:
                            data[header].append(None)
                    # If column doesn't exist, add it with empty values
                    else:
                        data[header] = [None] * max_required_len
            
            # Debug output
            for header, values in data.items():
                print(f"{header}: {len(values)} items")
                if values:
                    print(f"  First item: {values[0]}")
            
            # Create DataFrame
            df = pd.DataFrame(data)
            
            # Add default response_time if missing
            if "소요시간" not in df.columns:
                df["소요시간"] = 0
            else:
                # Convert to numeric, replacing errors with 0
                df["소요시간"] = pd.to_numeric(df["소요시간"], errors='coerce').fillna(0)
            
            # Add empty score column if missing
            has_score_column = "점수" in df.columns
            score_column_name = "점수" if has_score_column else ""
            if not has_score_column:
                df["점수"] = np.nan
                score_column_name = "점수"
                has_score_column = True
            
            # Fill NaN values with empty string for text columns
            for col in ["질문", "정답", "결과"]:
                df[col] = df[col].fillna("")
            
            # Update state
            state["data"]["dataframe"] = df.to_dict(orient="records")
            state["data"]["raw_df"] = df  # Save original DataFrame
            state["data"]["has_score_column"] = has_score_column
            state["data"]["score_column_name"] = score_column_name
            
            state["status"] = "completed"
            state["messages"].append({
                "role": "system", 
                "content": f"Successfully loaded {len(df)} rows of data."
            })
            
        except Exception as e:
            state["status"] = "failed"
            state["errors"].append(str(e))
            state["messages"].append({
                "role": "system", 
                "content": f"Error during Excel loading: {str(e)}"
            })
        
        return state
