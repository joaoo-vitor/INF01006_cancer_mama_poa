import argparse
import glob
import os
import pandas as pd


def aggregate_csvs(directory, file_filter, output_path):
    # Ensure the directory path is absolute/normalized
    directory = os.path.abspath(directory)

    # Construct the full search pattern
    search_pattern = os.path.join(directory, file_filter)

    # Find and sort all matching files
    files = sorted(glob.glob(search_pattern))

    if not files:
        print(f"No files found matching pattern: {search_pattern}")
        return

    print(f"📂 Found {len(files)} files to aggregate...")

    # Read and combine all CSV files
    df_list = []
    for file in files:
        print(f"   -> Reading {os.path.basename(file)}")
        df_list.append(pd.read_csv(file, dtype={"AP_CIDCAS": str}))

    combined_df = pd.concat(df_list, ignore_index=True)

    # Save the aggregated file
    combined_df.to_csv(output_path, index=False)
    print(f"✅ Success! Aggregated file saved to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Aggregate multiple CSV files into one."
    )

    # Define the required arguments
    parser.add_argument(
        "-d",
        "--dir",
        required=True,
        help="Path to the directory containing the files",
    )
    parser.add_argument(
        "-f",
        "--filter",
        required=True,
        help="Name filter pattern (e.g., 'RDRS24*colo.csv' or 'RDRS24*')",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Name of the final aggregated CSV file",
    )

    args = parser.parse_args()

    aggregate_csvs(args.dir, args.filter, args.output)