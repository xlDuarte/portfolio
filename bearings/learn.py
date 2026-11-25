"""Small, dependency-free learners used for the baselines (NumPy + SciPy only).

* Gaussian novelty detector with Ledoit–Wolf shrinkage of the covariance (Ledoit and Wolf, 2004),
  score = squared Mahalanobis distance to the healthy mean.
* Multinomial logistic regression with L2 penalty, fitted by L-BFGS on the exact gradient.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import minimize
from scipy.special import logsumexp


def ledoit_wolf(X: np.ndarray):
    """Shrunk covariance (1−δ)S + δ·μI with the Ledoit–Wolf optimal δ; returns (cov, δ)."""
    n, p = X.shape
    Xc = X - X.mean(0)
    S = Xc.T @ Xc / n
    mu = np.trace(S) / p
    d2 = np.sum((S - mu * np.eye(p)) ** 2)
    b2 = sum(np.sum((np.outer(x, x) - S) ** 2) for x in Xc) / n ** 2
    delta = float(min(b2, d2) / d2) if d2 > 0 else 1.0
    return (1 - delta) * S + delta * mu * np.eye(p), delta


class Novelty:
    def fit(self, X):
        self.mu = X.mean(0)
        self.sd = X.std(0) + 1e-12
        Z = (X - self.mu) / self.sd
        C, self.delta = ledoit_wolf(Z)
        self.P = np.linalg.inv(C)
        return self

    def score(self, X):
        Z = (X - self.mu) / self.sd
        return np.einsum("ij,jk,ik->i", Z, self.P, Z)


class Softmax:
    def __init__(self, l2: float = 1e-2):
        self.l2 = l2

    def fit(self, X, y):
        self.classes = np.unique(y)
        self.mu, self.sd = X.mean(0), X.std(0) + 1e-12
        Z = np.column_stack([np.ones(len(X)), (X - self.mu) / self.sd])
        Y = (y[:, None] == self.classes[None]).astype(float)
        k, p = len(self.classes), Z.shape[1]

        def f(w):
            W = w.reshape(p, k)
            A = Z @ W
            lse = logsumexp(A, axis=1)
            P = np.exp(A - lse[:, None])
            reg = self.l2 * np.sum(W[1:] ** 2)
            return float(np.sum(lse - np.sum(Y * A, 1)) / len(Z) + reg), ((Z.T @ (P - Y)) / len(Z) + 2 * self.l2 * np.vstack([np.zeros(k), W[1:]])).ravel()

        self.W = minimize(f, np.zeros(p * k), jac=True, method="L-BFGS-B").x.reshape(p, k)
        return self

    def predict(self, X):
        Z = np.column_stack([np.ones(len(X)), (X - self.mu) / self.sd])
        return self.classes[np.argmax(Z @ self.W, axis=1)]


def auc(neg: np.ndarray, pos: np.ndarray) -> float:
    """Area under the ROC curve by the Mann–Whitney statistic (ties count one half)."""
    s = np.concatenate([neg, pos])
    r = np.argsort(np.argsort(s, kind="mergesort"), kind="mergesort").astype(float) + 1
    # average ranks for ties
    _, inv, cnt = np.unique(s, return_inverse=True, return_counts=True)
    sums = np.bincount(inv, weights=r)
    r = (sums / cnt)[inv]
    return float((r[len(neg):].sum() - len(pos) * (len(pos) + 1) / 2) / (len(neg) * len(pos)))


def roc(neg, pos, n: int = 101):
    thr = np.quantile(np.concatenate([neg, pos]), np.linspace(1, 0, n))
    return [(float(np.mean(neg >= t)), float(np.mean(pos >= t))) for t in thr]


def balanced_accuracy(y, p) -> float:
    return float(np.mean([np.mean(p[y == c] == c) for c in np.unique(y)]))
