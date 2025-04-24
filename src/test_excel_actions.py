import os
import pandas as pd
from action_performer import ActionPerformer

def create_test_excel():
    """Create a test Excel file for testing the new Excel features."""
    project_dir = os.path.dirname(os.path.dirname(__file__))
    excel_dir = os.path.join(project_dir, "excel_files")
    
    if not os.path.exists(excel_dir):
        os.makedirs(excel_dir)
    
    file_path = os.path.join(excel_dir, "test_data.xlsx")
    
    # Create a simple dataframe
    data = {
        "Keywords": ["Python programming", "Machine learning", "Data science", 
                    "Artificial intelligence", "Web development"],
        "Results": ["", "", "", "", ""]
    }
    
    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False)
    
    print(f"Created test Excel file at: {file_path}")
    return file_path

def test_excel_actions():
    """Test the Excel actions functionality."""
    # Create test file
    file_path = create_test_excel()
    relative_path = os.path.join("excel_files", "test_data.xlsx")
    
    performer = ActionPerformer()
    
    # Test extracting data
    extract_action = {
        "type": "excel",
        "file": relative_path,
        "sheet": "Sheet1",
        "column": "Keywords",
        "start_row": 1,
        "end_row": 3,
        "use_last_filled": False,
        "mode": "extract_data"
    }
    
    print("\nTesting data extraction...")
    performer.perform_action(extract_action)
    
    # Test search action
    search_action = {
        "type": "excel",
        "file": relative_path,
        "sheet": "Sheet1",
        "column": "Keywords",
        "start_row": 1,
        "end_row": 3,
        "use_last_filled": False,
        "mode": "search_data",
        "target_column": "Results"
    }
    
    print("\nTesting Google search and results storage...")
    performer.perform_action(search_action)
    
    print("\nDone! Check the Excel file for results.")

if __name__ == "__main__":
    test_excel_actions()
