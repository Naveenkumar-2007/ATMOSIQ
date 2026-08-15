import hashlib
import json
import os
import pickle
import random
import sys

import numpy as np
import pandas as pd
import yaml

from atmosiq.exception.exception import AtmosIQException


def ensure_dir(path):
    target = os.path.dirname(path) if os.path.splitext(path)[1] else path
    if target:
        os.makedirs(target, exist_ok=True)
    return path


def read_yaml_file(file_path):
    try:
        with open(file_path) as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise AtmosIQException(e, sys)


def write_yaml_file(file_path, content):
    ensure_dir(file_path)
    with open(file_path, "w") as f:
        yaml.safe_dump(content, f, sort_keys=False)


def read_json_file(file_path):
    with open(file_path) as f:
        return json.load(f)


def write_json_file(file_path, content):
    ensure_dir(file_path)
    with open(file_path, "w") as f:
        json.dump(content, f, indent=2, default=str)


def save_parquet(df, file_path):
    ensure_dir(file_path)
    df.to_parquet(file_path, index=False)


def read_parquet(file_path):
    return pd.read_parquet(file_path)


def hash_config(content):
    return hashlib.sha256(json.dumps(content, sort_keys=True, default=str).encode()).hexdigest()


def save_object(file_path, obj):
    try:
        ensure_dir(file_path)
        blob = pickle.dumps(obj)
        with open(file_path, "wb") as f:
            f.write(blob)
        with open(file_path + ".sha256", "w") as f:
            f.write(hashlib.sha256(blob).hexdigest())
    except Exception as e:
        raise AtmosIQException(e, sys)


def load_object(file_path, trusted_hashes=None):
    try:
        with open(file_path, "rb") as f:
            blob = f.read()
        digest = hashlib.sha256(blob).hexdigest()
        sidecar = file_path + ".sha256"
        if os.path.exists(sidecar):
            with open(sidecar) as f:
                expected = f.read().strip()
            if expected != digest:
                raise ValueError(f"Artifact integrity check failed for {file_path}")
        if trusted_hashes is not None and digest not in trusted_hashes:
            raise ValueError(f"Artifact {file_path} is not in the trusted registry")
        return pickle.loads(blob)
    except Exception as e:
        raise AtmosIQException(e, sys)


def seed_everything(seed):
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass
