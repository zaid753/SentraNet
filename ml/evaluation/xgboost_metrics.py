"""Evaluation metrics, safe PR-AUC calculation, and confusion matrix generator for XGBoost."""

from typing import Dict, Any, List, Optional, Tuple
import os
import json
import numpy as np
import pandas as pd
from sklearn.metrics import (
    f1_score,
    precision_score,
    recall_score,
    log_loss,
    accuracy_score,
    confusion_matrix,
    precision_recall_curve,
    auc,
)
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt

class XGBoostMetricsEvaluator:
    """
    Computes comprehensive evaluation metrics for multi-class network attack classification.
    Safely handles class absence in validation or test splits without fabricating numbers.
    """

    def __init__(self, class_names: List[str]):
        self.class_names = class_names
        self.num_classes = len(class_names)

    def evaluate(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_proba: np.ndarray,
        split_name: str = "test",
    ) -> Dict[str, Any]:
        """
        Calculates:
        - Macro & Weighted F1
        - Per-class Precision, Recall, F1
        - Multiclass Log Loss
        - Safe Macro PR-AUC (One-vs-Rest)
        - Confusion Matrix
        - Reference Accuracy
        """
        # Ensure 1D integer arrays
        y_true = np.asarray(y_true, dtype=int)
        y_pred = np.asarray(y_pred, dtype=int)
        y_proba = np.asarray(y_proba, dtype=float)

        # Accuracy (for reference only)
        acc = float(accuracy_score(y_true, y_pred))

        # F1 scores
        macro_f1 = float(f1_score(y_true, y_pred, average="macro", zero_division=0))
        weighted_f1 = float(f1_score(y_true, y_pred, average="weighted", zero_division=0))

        # Per-class metrics
        prec_per_class = precision_score(y_true, y_pred, average=None, labels=range(self.num_classes), zero_division=0)
        rec_per_class = recall_score(y_true, y_pred, average=None, labels=range(self.num_classes), zero_division=0)
        f1_per_class = f1_score(y_true, y_pred, average=None, labels=range(self.num_classes), zero_division=0)

        per_class_metrics = {}
        for idx, name in enumerate(self.class_names):
            class_present_in_ground_truth = int(np.sum(y_true == idx))
            class_predicted_count = int(np.sum(y_pred == idx))

            per_class_metrics[name] = {
                "class_index": idx,
                "ground_truth_count": class_present_in_ground_truth,
                "predicted_count": class_predicted_count,
                "precision": float(prec_per_class[idx]) if class_predicted_count > 0 else None,
                "recall": float(rec_per_class[idx]) if class_present_in_ground_truth > 0 else None,
                "f1_score": float(f1_per_class[idx]) if class_present_in_ground_truth > 0 else None,
                "status": "evaluated" if class_present_in_ground_truth > 0 else "class_absent_in_ground_truth",
            }

        # Multi-class Log Loss
        # Log loss requires valid probability distribution and labels present in y_true
        try:
            # clip probabilities for stability
            eps = 1e-15
            clipped_proba = np.clip(y_proba, eps, 1 - eps)
            clipped_proba /= clipped_proba.sum(axis=1, keepdims=True)
            loss = float(log_loss(y_true, clipped_proba, labels=list(range(self.num_classes))))
        except Exception as e:
            loss = None

        # Safe One-vs-Rest PR-AUC
        pr_aucs = {}
        valid_pr_auc_scores = []
        for idx, name in enumerate(self.class_names):
            y_binary = (y_true == idx).astype(int)
            unique_states = np.unique(y_binary)
            if len(unique_states) < 2:
                # Class absent or 100% of data - PR-AUC is mathematically undefined
                pr_aucs[name] = {
                    "pr_auc": None,
                    "reason": "Class has only one binary state in y_true (no positive or no negative samples)",
                }
            else:
                try:
                    p, r, _ = precision_recall_curve(y_binary, y_proba[:, idx])
                    score = float(auc(r, p))
                    pr_aucs[name] = {"pr_auc": round(score, 4)}
                    valid_pr_auc_scores.append(score)
                except Exception as e:
                    pr_aucs[name] = {"pr_auc": None, "reason": str(e)}

        macro_pr_auc = float(np.mean(valid_pr_auc_scores)) if valid_pr_auc_scores else None

        # Confusion Matrix across full canonical class list (5x5)
        cm = confusion_matrix(y_true, y_pred, labels=list(range(self.num_classes)))
        cm_dict = {
            "labels": self.class_names,
            "matrix": cm.tolist(),
        }

        report = {
            "split": split_name,
            "sample_count": len(y_true),
            "macro_f1": round(macro_f1, 4),
            "weighted_f1": round(weighted_f1, 4),
            "multiclass_log_loss": round(loss, 4) if loss is not None else None,
            "macro_pr_auc": round(macro_pr_auc, 4) if macro_pr_auc is not None else None,
            "pr_auc_valid_class_count": len(valid_pr_auc_scores),
            "total_class_count": self.num_classes,
            "accuracy_reference": round(acc, 4),
            "per_class": per_class_metrics,
            "pr_auc_per_class": pr_aucs,
            "confusion_matrix": cm_dict,
        }

        return report

    def plot_confusion_matrix(self, cm: np.ndarray, output_path: str, title: str = "Confusion Matrix") -> None:
        """Renders and saves a high-contrast confusion matrix plot."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig, ax = plt.subplots(figsize=(8, 6), facecolor="#030712")
        ax.set_facecolor("#0b0f19")

        im = ax.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
        cbar = ax.figure.colorbar(im, ax=ax)
        cbar.ax.yaxis.set_tick_params(color="#94a3b8")
        plt.setp(plt.getp(cbar.ax.axes, "yticklabels"), color="#94a3b8")

        ax.set(
            xticks=np.arange(self.num_classes),
            yticks=np.arange(self.num_classes),
            xticklabels=self.class_names,
            yticklabels=self.class_names,
            title=title,
            ylabel="Actual Ground Truth",
            xlabel="Predicted Class",
        )

        ax.title.set_color("#f8fafc")
        ax.yaxis.label.set_color("#cbd5e1")
        ax.xaxis.label.set_color("#cbd5e1")
        ax.tick_params(colors="#94a3b8")

        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

        # Loop over data dimensions and create text annotations.
        thresh = cm.max() / 2.0 if cm.max() > 0 else 1.0
        for i in range(self.num_classes):
            for j in range(self.num_classes):
                ax.text(
                    j,
                    i,
                    format(cm[i, j], "d"),
                    ha="center",
                    va="center",
                    color="white" if cm[i, j] > thresh else "#94a3b8",
                    fontweight="bold" if cm[i, j] > 0 else "normal",
                )

        fig.tight_layout()
        plt.savefig(output_path, dpi=180, facecolor=fig.get_facecolor(), edgecolor="none")
        plt.close()
