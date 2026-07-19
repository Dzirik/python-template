"""
Canonical method-identifier vocabulary for the transformer suite.

F and INV are reserved for a larger transformer suite not yet migrated into this repo, which uses
all four ids heavily and needs one canonical import path. Do not prune them as unused.
"""

F = "f"  # fit method in transformers
FP = "fp"  # fit_predict method in transformers
P = "p"  # predict method in transformers
INV = "i"  # inverse method
