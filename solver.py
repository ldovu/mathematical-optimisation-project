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
                #'X_as': {a: self.X_as[a].X for a in self.X_as}
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
