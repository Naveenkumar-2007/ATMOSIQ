import os
import sys
import time

import numpy as np
import torch
from torch.utils.data import DataLoader, Dataset

from atmosiq.components.deep.models import build_model
from atmosiq.components.model_trainer import feature_columns_for
from atmosiq.entity.artifact_entity import DatasetCreationArtifact, ModelTrainerArtifact
from atmosiq.entity.config_entity import DeepTrainerConfig
from atmosiq.exception.exception import AtmosIQException
from atmosiq.logging.logger import logging
from atmosiq.utils.main_utils.utils import read_parquet, seed_everything
from atmosiq.utils.ml_utils.metric import metrics as metric

logger = logging.getLogger("atmosiq.components.deep_trainer")


class WeatherSequenceDataset(Dataset):
    def __init__(self, features, targets, seq_len):
        self.features = torch.tensor(features, dtype=torch.float32)
        self.targets = torch.tensor(targets, dtype=torch.float32)
        self.seq_len = seq_len

    def __len__(self):
        return max(0, len(self.features) - self.seq_len)

    def __getitem__(self, idx):
        return self.features[idx : idx + self.seq_len], self.targets[idx + self.seq_len - 1]


class DeepTrainer:
    def __init__(self, dataset_artifact, config, model_names=None):
        try:
            self.dataset_artifact = dataset_artifact
            self.config = config
            self.model_names = model_names or ["lstm", "gru", "tcn", "transformer"]
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        except Exception as e:
            raise AtmosIQException(e, sys)

    def _loop(self, model, loader, optimizer=None, scheduler=None):
        training = optimizer is not None
        model.train(training)
        loss_fn = torch.nn.HuberLoss()
        total, count = 0.0, 0
        for X, y in loader:
            X, y = X.to(self.device), y.to(self.device)
            if training:
                optimizer.zero_grad()
            pred = model(X).squeeze(-1)
            loss = loss_fn(pred, y)
            if training:
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                if scheduler is not None:
                    scheduler.step()
            total += loss.item() * len(y)
            count += len(y)
        return total / max(count, 1)

    def initiate_deep_training(self, horizon=24):
        try:
            seed_everything(42)
            train = read_parquet(os.path.join(self.dataset_artifact.dataset_dir, "train.parquet"))
            validation = read_parquet(os.path.join(self.dataset_artifact.dataset_dir, "validation.parquet"))
            target_col = f"target_temperature_{horizon}h"
            features = feature_columns_for(train)
            tr = train.dropna(subset=[target_col] + [f for f in features if f in train.columns])
            va = validation.dropna(subset=[target_col] + [f for f in features if f in validation.columns])
            if tr.empty or va.empty:
                return []
            X_tr, y_tr = tr[features].to_numpy(dtype=np.float32), tr[target_col].to_numpy()
            X_va, y_va = va[features].to_numpy(dtype=np.float32), va[target_col].to_numpy()
            mu, sd = X_tr.mean(0), X_tr.std(0) + 1e-8
            X_tr, X_va = (X_tr - mu) / sd, (X_va - mu) / sd
            train_loader = DataLoader(WeatherSequenceDataset(X_tr, y_tr, self.config.sequence_length), batch_size=self.config.batch_size, shuffle=False)
            val_loader = DataLoader(WeatherSequenceDataset(X_va, y_va, self.config.sequence_length), batch_size=self.config.batch_size)
            artifacts = []
            for name in self.model_names:
                model = build_model(name, X_tr.shape[1], {"context_length": self.config.sequence_length}).to(self.device)
                optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
                scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=max(1, self.config.epochs * max(len(train_loader), 1)))
                best_val, patience_left, best_state = float("inf"), self.config.patience, None
                for epoch in range(self.config.epochs):
                    self._loop(model, train_loader, optimizer, scheduler)
                    val_loss = self._loop(model, val_loader)
                    if val_loss < best_val - 1e-4:
                        best_val, best_state = val_loss, {k: v.cpu().clone() for k, v in model.state_dict().items()}
                        patience_left = self.config.patience
                    else:
                        patience_left -= 1
                        if patience_left <= 0:
                            logger.info("early stopping", extra={"ctx_model": name, "ctx_epoch": epoch})
                            break
                if best_state is not None:
                    model.load_state_dict(best_state)
                model.eval()
                preds = []
                with torch.no_grad():
                    for X, _ in val_loader:
                        preds.append(model(X.to(self.device)).squeeze(-1).cpu().numpy())
                preds = np.concatenate(preds) if preds else np.array([])
                y_eval = y_va[self.config.sequence_length :]
                val_metrics = {"mae": metric.mae(y_eval, preds), "rmse": metric.rmse(y_eval, preds)} if len(preds) else {"mae": float("nan"), "rmse": float("nan")}
                path = os.path.join(self.config.deep_dir, f"{name}_{horizon}h.pt")
                os.makedirs(os.path.dirname(path), exist_ok=True)
                torch.save({"state": model.state_dict(), "config": {"name": name, "in_dim": int(X_tr.shape[1])}, "scaler": (mu.tolist(), sd.tolist()), "features": features}, path)
                artifacts.append(ModelTrainerArtifact(
                    trained_model_file_path=path, model_name=name, task="temperature", horizon_hours=horizon,
                    train_metrics={"epochs": self.config.epochs}, validation_metrics=val_metrics, training_run_id=f"deep_{name}_{horizon}h",
                ))
            logger.info("deep training complete", extra={"ctx_models": len(artifacts)})
            return artifacts
        except Exception as e:
            raise AtmosIQException(e, sys)
