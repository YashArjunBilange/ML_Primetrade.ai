import argparse
import json
import logging
import time
import os
import sys

import pandas as pd
import numpy as np
import yaml


# Read command line arguments
def get_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--log-file", required=True)

    return parser.parse_args()


# Setup logging
def setup_logging(log_file):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )


# Load configuration file
def load_config(config_path):

    if not os.path.exists(config_path):
        raise FileNotFoundError("Config file not found")

    with open(config_path, "r") as file:
        config = yaml.safe_load(file)

    if config is None:
        raise ValueError("Config file is empty")

    required_keys = ["seed", "window", "version"]

    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing config field: {key}")

    return config


# Load CSV data
def load_data(input_path):

    if not os.path.exists(input_path):
        raise FileNotFoundError("Input CSV file not found")

    try:
        # Read raw file
        with open(input_path, "r", encoding="utf-8") as f:
            lines = [line.strip().strip('"') for line in f]

        # Convert cleaned lines into dataframe
        from io import StringIO
        csv_text = "\n".join(lines)

        df = pd.read_csv(StringIO(csv_text))

    except Exception:
        raise ValueError("Invalid CSV format")

    if df.empty:
        raise ValueError("CSV file is empty")

    df.columns = df.columns.str.strip().str.lower()

    logging.info(f"Columns found: {list(df.columns)}")

    if "close" not in df.columns:
        raise ValueError("Column 'close' not found")

    return df

# Calculate rolling mean and signals
def generate_signals(df, window):

    logging.info("Calculating rolling mean")

    df["rolling_mean"] = (
        df["close"]
        .rolling(window=window)
        .mean()
    )

    logging.info("Generating signals")

    df["signal"] = (
        df["close"] > df["rolling_mean"]
    ).astype(int)

    return df


# Save metrics JSON
def save_metrics(metrics, output_path):

    with open(output_path, "w") as file:
        json.dump(metrics, file, indent=2)


def main():

    args = get_arguments()

    setup_logging(args.log_file)

    start_time = time.time()

    version = "v1"

    try:

        logging.info("Job started")

        # Load config
        config = load_config(args.config)

        version = config["version"]

        logging.info(
            f"Config loaded: seed={config['seed']}, "
            f"window={config['window']}, "
            f"version={config['version']}"
        )

        # Set seed
        np.random.seed(config["seed"])

        # Load dataset
        df = load_data(args.input)

        logging.info(f"Rows loaded: {len(df)}")

        # Processing
        df = generate_signals(
            df,
            config["window"]
        )

        rows_processed = len(df)

        signal_rate = float(
            df["signal"].mean()
        )

        latency_ms = int(
            (time.time() - start_time) * 1000
        )

        metrics = {
            "version": config["version"],
            "rows_processed": rows_processed,
            "metric": "signal_rate",
            "value": round(signal_rate, 4),
            "latency_ms": latency_ms,
            "seed": config["seed"],
            "status": "success"
        }

        save_metrics(metrics, args.output)

        logging.info(f"Signal rate: {signal_rate}")
        logging.info(f"Metrics: {metrics}")
        logging.info("Job completed successfully")

        print(json.dumps(metrics, indent=2))

        sys.exit(0)

    except Exception as e:

        logging.exception("Job failed")

        metrics = {
            "version": version,
            "status": "error",
            "error_message": str(e)
        }

        save_metrics(metrics, args.output)

        print(json.dumps(metrics, indent=2))

        sys.exit(1)


if __name__ == "__main__":
    main()