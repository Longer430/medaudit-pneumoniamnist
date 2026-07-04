from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from medaudit.pipeline import export_predictions  # noqa: E402


def main() -> None:
    metrics = export_predictions(
        ROOT / "data" / "raw" / "pneumoniamnist.npz",
        ROOT / "data" / "processed" / "pneumoniamnist_test_predictions.csv",
    )
    for name, value in metrics.items():
        print(f"{name}={value}")


if __name__ == "__main__":
    main()
