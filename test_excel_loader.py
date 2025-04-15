# test_excel_loader.py
from agents.excel_loader import ExcelLoaderAgent, AgentState
import os
import pandas as pd

# Test function
def test_excel_loader(file_path, sheet_name=None):
    print(f"Loading data from file '{file_path}'...")
    
    # Create agent
    agent = ExcelLoaderAgent("test_loader")
    
    # Initialize state
    state = AgentState(
        agent_id="test",
        data={
            "file_path": file_path,
            "sheet_name": sheet_name
        }
    )
    
    # Run
    result_state = agent.load_excel(state)
    
    # Print results
    print("\n===== Result =====")
    print(f"Status: {result_state['status']}")
    
    for msg in result_state.get("messages", []):
        print(f"{msg.get('role', 'system')}: {msg.get('content', '')}")
    
    if result_state["status"] == "failed":
        print("\nErrors:")
        for error in result_state.get("errors", []):
            print(f"- {error}")
    elif "dataframe" in result_state.get("data", {}):
        data = result_state["data"]["dataframe"]
        df = pd.DataFrame(data)
        
        print(f"\nSuccessfully loaded {len(data)} items.")
        
        # Data overview
        print("\n===== Data Overview =====")
        print("\nColumns:", list(df.columns))
        print("\nFirst 5 rows:")
        print(df.head(5))
        
        # Option to view all data
        view_all = input("\nDo you want to view all data? (y/n): ").strip().lower() == 'y'
        if view_all:
            print("\n===== All Data =====")
            pd.set_option('display.max_rows', None)
            pd.set_option('display.max_columns', None)
            pd.set_option('display.width', None)
            print(df)
            # Reset display options
            pd.reset_option('display.max_rows')
            pd.reset_option('display.max_columns')
            pd.reset_option('display.width')
        
        # Save data to CSV for easier viewing
        save_csv = input("\nDo you want to save data to CSV? (y/n): ").strip().lower() == 'y'
        if save_csv:
            csv_path = f"{os.path.splitext(file_path)[0]}_extracted.csv"
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            print(f"Data saved to {csv_path}")
    
    return result_state

# Run test
if __name__ == "__main__":
    # Check if agents directory exists
    if not os.path.exists("agents"):
        os.makedirs("agents")
        print("Created 'agents' directory")
        
    file_path = input("Excel file path: ")
    sheet_name = input("Sheet name (press Enter if none): ").strip() or None
    
    test_excel_loader(file_path, sheet_name)