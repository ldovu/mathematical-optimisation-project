import gurobipy as gb
import numpy as np
from Pre_Process import Pre_Process

class Solver:

    def __init__(self, data_path):

        print("Starting pre-processing...")

        self.data = Pre_Process(data_path)

        model = gb.Model()
        model.modelSense = gb.GRB.MINIMIZE

        print("Defining variables...")
        self.X_as = model.addVars(
            [a for a,_ in enumerate(self.data.arcs)], vtype=gb.GRB.BINARY, name="X_as"
        )
        self.alpha = model.addVar(vtype=gb.GRB.INTEGER, name="alpha")

        print("Defining costs...")
        costs_list = []
        for a,arc in enumerate(self.data.arcs):
            cost = 0
            if ((a in self.data.range_A1) or (a in self.data.range_A2)):
                cost = arc[4] # arc = ("As", job_1, t1, job_2, t2)
            costs_list.append(cost)

        costs = np.array(costs_list)

        J = range(1, self.data.n_jobs + 1)
        J_0 = range(0, self.data.n_jobs + 1)

        print("Defining costraint 1...")
        # Constraint 1
        for j in J:
            model.addConstr(
                gb.quicksum(
                    self.X_as[a]
                    for a,arc in enumerate(self.data.arcs)
                    if (((a in self.data.range_A1) or (a in self.data.range_A2))
                        and arc[3] == j)
                ) == 1
            )

        print("Defining costraint 2...")
        # Constraint 2
        model.addConstr(
            gb.quicksum(
                self.X_as[a]
                for a in self.data.range_arcs
                if (a in self.data.range_A2)
            ) == 1
        )

        print("Defining costraint 3...")
        # Constraint 3
        i = 0
        for node in self.data.O[1:-1] + self.data.R: # self.data.O[1:-1] skips first element (0, 0) and last element (0, T)
            job = node[0]
            time = node[1]
            model.addConstr(
                gb.quicksum(
                    self.X_as[a]
                    for a,arc in enumerate(self.data.arcs)
                    if ((arc[3] == job) and (arc[4] == time))
                ) - gb.quicksum(
                    self.X_as[a]
                    for a,arc in enumerate(self.data.arcs)
                    if ((arc[1] == job) and (arc[2] == time))
                ) == 0
            )
            i = i + 1
            print(i)
            # model.addConstr(
            #     gb.quicksum( 
            #         self.X_as[a] * 
            #         (-1 if (arc[1] == job and arc[2] == time) else 1 if (arc[3] == job and arc[4] == time) else 0) 
            #         for a, arc in enumerate(self.data.arcs) 
            #     ) == 0 
            # )


        print("Defining costraint 4...")
        # Constraint 4
        for j in J:
            cost_arcs_entering_j = gb.quicksum(
                costs[a] * self.X_as[a]
                for a,arc in enumerate(self.data.arcs)
                if (((a in self.data.range_A1) or (a in self.data.range_A2))
                and arc[3] == j)
            )
            model.addConstr(self.alpha >= cost_arcs_entering_j)

        print("Setting objective...")
        # Set objective function
        model.setObjective(self.alpha, gb.GRB.MINIMIZE)
        
        self.model = model
        print("Model ready.")



    def solve(self):
        self.model.optimize()



    def get_solution_alpha(self):
        if self.model.status == gb.GRB.OPTIMAL:
            solution = {
                'alpha': self.alpha.X
            }
            return solution
        else:
            return None
    

    
    def get_solution_path(self):
        if self.model.status != gb.GRB.OPTIMAL:
            return None
        
        # Extract the arcs in the solution
        selected_arcs = [
            self.data.arcs[a] for a in range(len(self.data.arcs)) if self.X_as[a].X > 0.5
        ]
        
        ordered_arcs = sorted(selected_arcs, key=lambda x: x[2])

        return ordered_arcs
    





# import gurobipy as gb
# import numpy as np
# from Pre_Process import Pre_Process
# import threading

# class Solver:

#     def __init__(self, data_path, num_threads=10):
#         print("Starting pre-processing...")
#         self.data = Pre_Process(data_path)
        
#         self.model = gb.Model()
#         self.model.modelSense = gb.GRB.MINIMIZE

#         self.num_threads = num_threads

#         print("Defining variables...")
#         self.X_as = self.model.addVars(len(self.data.arcs), vtype=gb.GRB.BINARY, name="X_as")
#         self.alpha = self.model.addVar(vtype=gb.GRB.INTEGER, name="alpha")

#         print("Defining costs...")
#         self.costs = np.array([arc[4] if a in self.data.range_A1 or a in self.data.range_A2 else 0 
#                                for a, arc in enumerate(self.data.arcs)])

#         print("Defining constraints...")
#         self.define_constraints()

#         print("Setting objective...")
#         self.model.setObjective(self.alpha, gb.GRB.MINIMIZE)

#         print("Model ready.")

#     def define_constraints(self):
#         # Constraint 1
#         J = range(1, self.data.n_jobs + 1)
#         for j in J:
#             arcs_entering_j = [a for a, arc in enumerate(self.data.arcs) 
#                                if (a in self.data.range_A1 or a in self.data.range_A2) and arc[3] == j]
#             self.model.addConstr(gb.quicksum(self.X_as[a] for a in arcs_entering_j) == 1)

#         # Constraint 2
#         arcs_in_A2 = [a for a in self.data.range_arcs if a in self.data.range_A2]
#         self.model.addConstr(gb.quicksum(self.X_as[a] for a in arcs_in_A2) == 1)

#         # Constraint 3
#         self.add_constraints_3_parallel()

#         # Constraint 4
#         for j in J:
#             arcs_entering_j = [a for a, arc in enumerate(self.data.arcs) 
#                                if (a in self.data.range_A1 or a in self.data.range_A2) and arc[3] == j]
#             self.model.addConstr(self.alpha >= gb.quicksum(self.costs[a] * self.X_as[a] for a in arcs_entering_j))

#     def add_constraints_3_parallel(self):
#         # Define a worker function to handle a subset of constraints
#         def worker(nodes, model, X_as, thread_id):
#             for node in nodes:
#                 job, time = node
#                 arcs_in = [a for a, arc in enumerate(self.data.arcs) if arc[3] == job and arc[4] == time]
#                 arcs_out = [a for a, arc in enumerate(self.data.arcs) if arc[1] == job and arc[2] == time]
#                 model.addConstr(gb.quicksum(X_as[a] for a in arcs_in) == gb.quicksum(X_as[a] for a in arcs_out))

#         # Split the nodes into chunks for parallel processing
#         nodes = self.data.O[1:-1] + self.data.R
#         chunk_size = len(nodes) // self.num_threads
#         threads = []

#         for i in range(self.num_threads):
#             start_index = i * chunk_size
#             if i == self.num_threads - 1:
#                 end_index = len(nodes)
#             else:
#                 end_index = (i + 1) * chunk_size
#             thread_nodes = nodes[start_index:end_index]
#             thread = threading.Thread(target=worker, args=(thread_nodes, self.model, self.X_as, i))
#             threads.append(thread)
#             thread.start()

#         for thread in threads:
#             thread.join()

#     def solve(self):
#         self.model.setParam('Threads', self.num_threads)
#         self.model.optimize()

#     def get_solution_alpha(self):
#         if self.model.status == gb.GRB.OPTIMAL:
#             return {'alpha': self.alpha.X}
#         else:
#             return None

#     def get_solution_path(self):
#         if self.model.status != gb.GRB.OPTIMAL:
#             return None
        
#         selected_arcs = [self.data.arcs[a] for a in range(len(self.data.arcs)) if self.X_as[a].X > 0.5]
#         ordered_arcs = sorted(selected_arcs, key=lambda x: x[2])
        
#         return ordered_arcs




