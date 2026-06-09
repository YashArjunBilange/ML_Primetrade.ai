# ML Engineering Internship Task

## Local Run

Install dependencies:

pip install -r requirements.txt

Run:

python run.py --input data.csv --config config.yaml --output metrics.json --log-file run.log

## Docker Build

docker build -t mlops-task .

## Docker Run

docker run --rm mlops-task

## Example Output

{
  "version": "v1",
  "rows_processed": 10000,
  "metric": "signal_rate",
  "value": 0.4989,
  "latency_ms": 33,
  "seed": 42,
  "status": "success"
}