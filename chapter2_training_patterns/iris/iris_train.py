from typing import Tuple
import numpy as np
import os
from argparse import ArgumentParser
from sklearn import metrics
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_iris
from skl2onnx.common.data_types import FloatTensorType
from skl2onnx import convert_sklearn

import mlflow
import mlflow.sklearn


def get_data(test_size: float = 0.3) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    iris = load_iris()
    data = iris.data
    target = iris.target
    x_train, x_test, y_train, y_test = train_test_split(data, target, shuffle=True, test_size=test_size)
    x_train = np.array(x_train).astype("float32")
    y_train = np.array(y_train).astype("float32")
    x_test = np.array(x_test).astype("float32")
    y_test = np.array(y_test).astype("float32")
    return x_train, x_test, y_train, y_test


def define_svc_pipeline() -> Pipeline:
    steps = [("normalize", StandardScaler()), ("svc", SVC(probability=True))]
    pipeline = Pipeline(steps=steps)
    return pipeline


def train(model, x_train, y_train):
    model.fit(x_train, y_train)


def evaluate(model, x_test, y_test) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    predict = model.predict(x_test)
    accuracy = metrics.accuracy_score(y_test, predict)
    precision = metrics.precision_score(y_test, predict, average="micro")
    recall = metrics.recall_score(y_test, predict, average="micro")
    return accuracy, precision, recall


def save_onnx(model, filepath: str):
    initial_type = [("float_input", FloatTensorType([None, 4]))]
    onx = convert_sklearn(model, initial_types=initial_type)
    with open(filepath, "wb") as f:
        f.write(onx.SerializeToString())


def main():
    parser = ArgumentParser(description="Scikit-learn iris Example")
    parser.add_argument(
        "--test_size",
        type=float,
        default=0.3,
        help="test data rate",
    )
    args = parser.parse_args()
    mlflow.sklearn.autolog()

    mlflow_experiment_id = int(os.getenv("MLFLOW_EXPERIMENT_ID", 0))

    x_train, x_test, y_train, y_test = get_data(test_size=args.test_size)

    model = define_svc_pipeline()

    train(model, x_train, y_train)

    accuracy, precision, recall = evaluate(model, x_test, y_test)

    mlflow.log_param("normalize", "StandardScaler")
    mlflow.log_param("model", "svc")
    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("precision", precision)
    mlflow.log_metric("recall", recall)
    mlflow.sklearn.log_model(model, "model")

    onnx_name = f"iris_svc_{mlflow_experiment_id}.onnx"
    onnx_path = os.path.join("/tmp/", onnx_name)
    save_onnx(model, onnx_path)
    mlflow.log_artifact(onnx_path)


if __name__ == "__main__":
    main()