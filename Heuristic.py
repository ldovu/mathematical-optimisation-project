class Heuristic:

    def __init__(self):
        raise Exception("__init__ not ready yet")
    
    def ILS_BD(self, I_R, I_ILS, w, N, gamma):
        opt_value = 100*100
        opt_solution = 0
        for i in range(I_R):
            solution = self.beam_search(w, N, gamma)
            local_opt_solution = solution
            Iter_ILS = 0
            while Iter_ILS < I_ILS:
                solution = self.local_search(solution)
                if self.get_fitness(solution) < self.get_fitness(opt_value):
                    local_opt_solution = solution
                    Iter_ILS = 0
                solution = self.perturbation(local_opt_solution)
                Iter_ILS = Iter_ILS + 1
            if self.get_fitness(local_opt_solution) < self.get_fitness(opt_solution):
                opt_solution = local_opt_solution
                opt_value = self.get_fitness(local_opt_solution)
        return opt_value, opt_solution

    def beam_search(self, w, N, gamma):
        # return solution
        pass

    def local_search(self, solution):
        # return solution
        pass

    def get_fitness(self, solution):
        # return fitness value
        pass

    def perturbation(self, solution):
        # retunr soltuion
        pass