import numpy as np

def cfar_ca(signal, training_cells, guard_cells, p_fa):
    """
    Performs Cell Averaging Constant False Alarm Rate (CA-CFAR) detection on a 1D signal.

    Args:
        signal (np.array): The 1D input signal (e.g., a range profile).
        training_cells (int): Number of training cells on each side of the cell under test.
        guard_cells (int): Number of guard cells on each side of the cell under test.
        p_fa (float): Desired probability of false alarm.

    Returns:
        np.array: A boolean array indicating detected targets (True) or noise (False).
    """
    num_cells = len(signal)
    detected_targets = np.zeros(num_cells, dtype=bool)

    # Calculate the threshold factor (alpha) based on the desired probability of false alarm
    # For CA-CFAR, alpha = N * (p_fa^(-1/N) - 1), where N is the number of training cells
    # Here, N = 2 * training_cells
    N = 2 * training_cells
    alpha = N * (p_fa**(-1/N) - 1)

    for i in range(num_cells):
        # Skip cells that don't have enough training cells on both sides
        if i < training_cells + guard_cells or i >= num_cells - (training_cells + guard_cells):
            continue

        # Define the regions for training cells
        # Exclude the cell under test and guard cells
        
        # Left training cells
        sum_training_cells = np.sum(signal[i - training_cells - guard_cells : i - guard_cells])
        
        # Right training cells
        sum_training_cells += np.sum(signal[i + guard_cells + 1 : i + guard_cells + training_cells + 1])

        # Calculate the noise estimate (average of training cells)
        noise_estimate = sum_training_cells / N

        # Calculate the threshold
        threshold = alpha * noise_estimate

        # Compare the cell under test with the threshold
        if signal[i] > threshold:
            detected_targets[i] = True

    return detected_targets

if __name__ == '__main__':
    # Example usage of CFAR
    # Create a sample signal with some peaks (targets) and noise
    sample_signal = np.array([0.5, 0.6, 0.7, 0.8, 5.0, 0.9, 1.0, 1.1, 1.2, 6.0, 1.3, 1.4, 1.5, 1.6, 1.7, 7.0, 1.8, 1.9, 2.0])
    
    # CFAR parameters
    training_cells = 2
    guard_cells = 1
    p_fa = 1e-4  # Probability of false alarm

    # Perform CFAR detection
    detections = cfar_ca(sample_signal, training_cells, guard_cells, p_fa)

    print("Sample Signal:", sample_signal)
    print("Detected Targets (boolean):", detections)
    print("Detected Target Values:", sample_signal[detections])

    # Another example with more noise and a clearer target
    np.random.seed(42)
    noise = np.random.rand(50) * 2
    target1 = np.array([10.0])
    target2 = np.array([12.0])
    signal_with_noise_and_targets = np.concatenate((noise[:15], target1, noise[15:30], target2, noise[30:]))

    detections_2 = cfar_ca(signal_with_noise_and_targets, training_cells, guard_cells, p_fa)
    print("\nSignal with noise and targets:", signal_with_noise_and_targets)
    print("Detected Targets (boolean):", detections_2)
    print("Detected Target Values:", signal_with_noise_and_targets[detections_2])
