from Solver import Solver

file_path_1 = "Instances/in02_001.dat"

solver_1 = Solver(file_path_1)

print(f"n_jobs = {solver_1.data.n_jobs}")

# solver_1.solve()

# solution_path_1 = solver_1.get_solution_path()
# print("\n\n\nSolution arcs:")
# print(solution_path_1)

# solution_alpha_1 = solver_1.get_solution_alpha()
# print("\n\n\nSolution alpha:")
# print(solution_alpha_1)