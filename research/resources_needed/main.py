import pdb
import matplotlib.pyplot as plt
import numpy as np
import time
import inspect, os, sys

# Hacky logic for importing module from other dirs
file_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) # script directory
project_dir = os.path.join(file_dir.split('vqf')[0], 'vqf')
src_dir = os.path.join(project_dir, 'src')
sys.path.append(src_dir)
from preprocessing import create_clauses, assess_number_of_unknowns

def main():
    threshold = 1e3
    primes = get_primes_lower_than_n(int(threshold))
    primes = primes[1:]

    qubits_required_no_preprocessing = []
    qubits_required_with_preprocessing = []
    initial_time = time.time()
    for p in primes:
        for q in primes:
            if p < q:
                continue
            m = p * q
            if m > threshold:
                continue
            start_time = time.time()
            p_dict, q_dict, z_dict, _ = create_clauses(m, p, q, apply_preprocessing=False, verbose=False)
            x, z = assess_number_of_unknowns(p_dict, q_dict, z_dict)

            qubits_required_no_preprocessing.append([m, x])

            p_dict, q_dict, z_dict, _ = create_clauses(m, p, q, apply_preprocessing=True, verbose=False)
            x, z = assess_number_of_unknowns(p_dict, q_dict, z_dict)
            qubits_required_with_preprocessing.append([m, x])
            end_time = time.time()
            t = np.round(end_time - start_time, 3)
            print(p, q, m, t, "    ", end="\r")

    print("Total time:", np.round((end_time - initial_time) / 60, 3), '[min]')

    data_1 = np.array(qubits_required_no_preprocessing)
    data_2 = np.array(qubits_required_with_preprocessing)

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    ax.scatter(data_1[:, 0], data_1[:, 1], label="No classical preprocessing")
    ax.scatter(data_2[:, 0], data_2[:, 1], label="Classical preprocessing")
    ax.set_xlabel("Biprime to be factored")
    ax.set_ylabel("Number of qubit required")
    ax.set_xscale('log')
    plt.legend()

    plt.show()

def get_primes_lower_than_n(n):
    # Source: https://hackernoon.com/prime-numbers-using-python-824ff4b3ea19
    primes = []
    for possiblePrime in range(2, n):
        
        # Assume number is prime until shown it is not. 
        isPrime = True
        for num in range(2, int(possiblePrime ** 0.5) + 1):
            if possiblePrime % num == 0:
                isPrime = False
                break
          
        if isPrime:
            primes.append(possiblePrime)

    return primes

if __name__ == '__main__':
    main()