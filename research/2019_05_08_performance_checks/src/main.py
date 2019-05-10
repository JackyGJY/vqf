from vqf.preprocessing import create_clauses, calculate_number_of_unknowns
from vqf.preprocessing import factor_56153, factor_291311
from vqf.optimization import OptimizationEngine
from sympy import Add, Mul, Symbol
import numpy as np
import pdb


def run_single_case(p_q_info, optimization_engine):
    sampling_results, mapping = optimization_engine.perform_qaoa()
    most_frequent_bit_string = max(sampling_results, key=lambda x: sampling_results[x])
    
    squared_overlap = calculate_squared_overlap(mapping, sampling_results, p_q_info)

    return squared_overlap, optimization_engine.step_by_step_results


def calculate_squared_overlap(mapping, sampling_results, p_q_info):
    true_p = p_q_info[0]
    true_q = p_q_info[1]
    p_dict = p_q_info[2]
    q_dict = p_q_info[3]

    p_binary_string = bin(true_p)[2:][::-1]
    q_binary_string = bin(true_q)[2:][::-1]

    p_binary = [int(char) for char in p_binary_string]
    q_binary = [int(char) for char in q_binary_string]
    if len(p_binary) < len(p_dict):
        trailing_zeros = len(p_dict) - len(p_binary)
        for zero in range(trailing_zeros):
            p_binary.append(0)

    if len(q_binary) < len(q_dict):
        trailing_zeros = len(q_dict) - len(q_binary)
        for zero in range(trailing_zeros):
            q_binary.append(0)

    correct_assignment = {}
    for q_id, q_val in q_dict.items():
        if type(q_val) is Symbol:
            bit_id = mapping[str(q_val)]
            correct_value = q_binary[q_id]
            if bit_id not in correct_assignment.keys():
                correct_assignment[bit_id] = correct_value

    for p_id, p_val in p_dict.items():
        if type(p_val) is Symbol:
            bit_id = mapping[str(p_val)]
            correct_value = p_binary[p_id]
            if bit_id not in correct_assignment.keys():
                correct_assignment[bit_id] = correct_value

    total_overlap = 0
    total_count = 0
    print(correct_assignment)
    print(mapping)
    for bit_string, count in sampling_results.most_common():
        correct_count = 0
        for bit_id, bit_value in enumerate(bit_string):
            # This accounts for the fact some of the bits of the sampling results
            # are irrelevant to the result - namely, carry bits.
            if bit_id not in correct_assignment.keys():
                continue
            if bit_value == correct_assignment[bit_id]:
                correct_count += 1
        overlap = correct_count / len(correct_assignment) * count
        total_count += count
        print(bit_string, correct_count, count)
        total_overlap += overlap
    total_overlap = total_overlap / total_count
    return total_overlap * total_overlap


def main():
    p_q_m_list = [[283, 7, 1981], [29, 11, 319], [263, 263, 69169], [263, 11, 2893], [241, 233, 56153], [557, 523, 291311]]
    results = []
    grid_sizes = [6, 24, 36, 9, 12, 24]
    unknowns_list = [[2, 0], [6, 3], [8, 5], [3, 1], [4, 0], [6, 0]]
    for p_q_m, grid_size, unknowns in zip(p_q_m_list, grid_sizes, unknowns_list):
        true_p = p_q_m[0]
        true_q = p_q_m[1]
        m = p_q_m[2]

        apply_preprocessing = True
        preprocessing_verbose = False
        optimization_verbose = False

        number_of_unknowns = 0
        carry_bits = 0
        counter = 0
        if m == 56153:
            p_dict, q_dict, z_dict, clauses = factor_56153()
        elif m == 291311:
            p_dict, q_dict, z_dict, clauses = factor_291311()
        else:
            p_dict, q_dict, z_dict, clauses = create_clauses(m, true_p, true_q, apply_preprocessing, preprocessing_verbose)
        number_of_unknowns, carry_bits = calculate_number_of_unknowns(p_dict, q_dict, z_dict)
        print(number_of_unknowns, carry_bits)
        if number_of_unknowns != unknowns[0] or carry_bits != unknowns[1]:
            print("Got wrong number of unknowns!")
            continue

        p_q_info = [true_p, true_q, p_dict, q_dict]
        step_by_step_results = None
        for steps in range(1, 9):
            for i in range(3):
                print(m, steps, i)                
                optimization_engine = OptimizationEngine(clauses, steps=steps, grid_size=grid_size, tol=1e-10, verbose=optimization_verbose, visualize=False)
                optimization_engine.step_by_step_results = step_by_step_results
                squared_overlap, step_by_step_results = run_single_case(p_q_info, optimization_engine)
                
                print(squared_overlap)
                results.append([m, steps, squared_overlap])

                optimization_history = optimization_engine.optimization_history
                history_file_name = "_".join([str(m), str(steps), str(i), "history"]) + ".csv"
                np.savetxt(history_file_name, optimization_history, delimiter=",")
            np.savetxt("results.csv", results, delimiter=",", header="m,steps,squared_overlap", fmt='%.4f', comments='')

if __name__ == '__main__':
    main()