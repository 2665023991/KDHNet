"""Information transfer rate used by the paper evaluation."""
import numpy as np

def compute_itr(num_classes, accuracy, decision_window_sec):
    if accuracy <= 0 or decision_window_sec <= 0 or num_classes <= 1:
        return 0.0
    if accuracy >= 1.0:
        accuracy = 0.9999
    if accuracy <= 1.0 / num_classes:
        return 0.0

    bits = (
        np.log2(num_classes)
        + accuracy * np.log2(accuracy)
        + (1 - accuracy) * np.log2((1 - accuracy) / (num_classes - 1))
    )
    return bits * (60.0 / decision_window_sec)
