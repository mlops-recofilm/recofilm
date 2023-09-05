import os


def get_last_final_csv(data_folder):
    csv_files = [file for file in os.listdir(data_folder) if file.startswith("final") and file.endswith(".csv")]
    if not csv_files:
        print("No CSV files starting with 'final' found in the data folder.")
        return None

    csv_files.sort(key=lambda x: os.path.getctime(os.path.join(data_folder, x)), reverse=True)
    last_final_csv = csv_files[0]
    return os.path.join(data_folder, last_final_csv)