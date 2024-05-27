import gurobipy as gb
import numpy as np
from Pre_Process import Pre_Process

class Solver:

    def __init__(self, data_path):

        self.data = Pre_Process(data_path)

        model = gb.Model()
        model.modelSense = gb.GRB.MINIMIZE

        self.X_as = model.addVars(
            [a for a,_ in enumerate(self.data.arcs)], vtype=gb.GRB.BINARY, name="X_as"
        )

        # Define alpha
        self.alpha = model.addVar(vtype=gb.GRB.INTEGER, name="alpha")

        costs_list = []
        for arc in self.data.arcs:
            cost = 0
            if (arc[0] == "A1") or (arc[0] == "A2"):
                cost = arc[4] # arc = ("As", job_1, t1, job_2, t2)
            costs_list.append(cost)

        costs = np.array(costs_list)

        J = range(1, self.data.n_jobs + 1)
        J_0 = range(0, self.data.n_jobs + 1)

        # Constraint 1
        for j in J:
            model.addConstr(
                gb.quicksum(
                    self.X_as[index]
                    for index in range(len(self.data.arcs))
                    if ((self.data.arcs[index][0] == "A1" or self.data.arcs[index][0] == "A2")
                        and self.data.arcs[index][3] == j)
                ) == 1
            )

        # Constraint 2
        model.addConstr(
            gb.quicksum(
                self.X_as[index]
                for index in range(len(self.data.arcs))
                if (self.data.arcs[index][0] == "A2")
            ) == 1
        )

        # Constraint 3a
        for node in self.data.O:
            job = node[0] # It should be always 0
            if (job != 0):
                raise Exception("Error in the node list O")
            time = node[1]
            if ((time == 0) or (time == self.data.T)):
                continue
            else:
                model.addConstr(
                    gb.quicksum(
                        self.X_as[index]
                        for index in range(len(self.data.arcs))
                        if ((self.data.arcs[index][3] == 0) and (self.data.arcs[index][4] == time)) # job = 0
                    ) - gb.quicksum(
                        self.X_as[index]
                        for index in range(len(self.data.arcs))
                        if ((self.data.arcs[index][1] == 0) and (self.data.arcs[index][2] == time)) # job = 0
                    ) == 0
                )

        # Constraint 3b
        for node in self.data.R:
            job = node[0]
            time = node[1]
            model.addConstr(
                gb.quicksum(
                    self.X_as[index]
                    for index in range(len(self.data.arcs))
                    if ((self.data.arcs[index][3] == job) and (self.data.arcs[index][4] == time))
                ) - gb.quicksum(
                    self.X_as[index]
                    for index in range(len(self.data.arcs))
                    if ((self.data.arcs[index][1] == job) and (self.data.arcs[index][2] == time))
                ) == 0
            )

        # Constraint 4
        for j in J:
            cost_arcs_entering_j = gb.quicksum(
                costs[index] * self.X_as[index]
                for index in range(len(self.data.arcs))
                if ((self.data.arcs[index][0] == "A1") or (self.data.arcs[index][0] == "A2"))
                and self.data.arcs[index][3] == j
            )
            model.addConstr(self.alpha >= cost_arcs_entering_j)

        # Set objective function
        model.setObjective(self.alpha, gb.GRB.MINIMIZE)
        
        self.model = model



    def solve(self):
        self.model.optimize()



    def get_solution_alpha(self):
        if self.model.status == gb.GRB.OPTIMAL:
            solution = {
                'alpha': self.alpha.X
                #'X_as': {index: self.X_as[index].X for index in self.X_as}
            }
            return solution
        else:
            return None
    

    
    def get_solution_path(self):
        if self.model.status != gb.GRB.OPTIMAL:
            return None
        
        # Extract the arcs in the solution
        selected_arcs = [
            self.data.arcs[index] for index in range(len(self.data.arcs)) if self.X_as[index].X > 0.5
        ]
        
        ordered_arcs = sorted(selected_arcs, key=lambda x: x[2])

        return ordered_arcs
