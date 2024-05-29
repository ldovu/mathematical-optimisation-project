from Pre_Process import Pre_Process
import heapq
import random

class Heuristic:

    def __init__(self, file_path):
        self.data = Pre_Process(file_path)
        
        

    # Idle and completion time
    def compute_I_and_C(self, jobs_sequence):
        
        # Set the idle time and completion time for the first job
        first_job = jobs_sequence[0]
        idle_time = self.data.release_dates[first_job] + self.data.setup_times[0][first_job]
        completion_time = idle_time + self.data.processing_times[first_job]
        
        # Iterate over the remaining jobs in the sequence
        for i in range(1, len(jobs_sequence)):
            job = jobs_sequence[i]
            previous_job = jobs_sequence[i - 1]
            
            # Define the release time, setup time, and processing time for the current job
            release_time_job =  self.data.release_dates[job]
            setup_time_job = self.data.setup_times[previous_job][job]
            processing_time_job = self.data.processing_times[job]
             
            idle_time = max(0, release_time_job - completion_time) + setup_time_job
            
            completion_time += idle_time + processing_time_job
        
        return idle_time, completion_time

    # Lower bound
    def compute_lower_bound(self, jobs_sequence, all_jobs):
        _, completion_pi = self.compute_I_and_C(jobs_sequence)
        
        # Define the set of remaining jobs U(π)
        remaining_jobs_U = [job for job in all_jobs if job not in jobs_sequence]
        
        Q = remaining_jobs_U + [jobs_sequence[-1]]
        
        min_release_time = min(self.data.release_dates[j] for j in remaining_jobs_U)
        
        min_setup_sum = 0
        for k in remaining_jobs_U:
            min_setup_time = min(self.data.setup_times[t][k] for t in Q if self.data.setup_times[t][k] != -1) 
            min_setup_sum += min_setup_time
        
        # Compute sum of processing times 
        processing_time_sum = sum(self.data.processing_times[k] for k in remaining_jobs_U)
        
        lower_bound = max(completion_pi, min_release_time) + min_setup_sum + processing_time_sum
        
        return lower_bound

    # Function β that branches a node π by scheduling job j
    def branch_node(self, j, pi):
        new_pi = pi.copy()
        new_pi.append(j)
        return new_pi

    # Algorithm Beam Search
    def beam_search(self, w, N, gamma, all_jobs):
        # Initialize the root node
        current_level = 0
        pi_0 = []
        prod_k = [pi_0]
        
        while current_level < len(all_jobs) - 1:
            prod_k1 = []
            
            for node in prod_k:
                remaining_jobs_U = [job for job in all_jobs if job not in node]
                theta = remaining_jobs_U.copy()
                
                # If the number of jobs exceeds the maximum number of possible branches, remove the job with the maximum idle time 
                while len(theta) > w:
                    max_idle_job = max(theta, key=lambda j: self.compute_I_and_C(node + [j])[0])
                    theta.remove(max_idle_job)
                
                # Branch the node by scheduling each job in theta
                for j in theta:
                    new_node = self.branch_node(j, node)
                    prod_k1.append(new_node)
            
            candidate_list = []
            
            # Compute the lower bound for each node in prod_k1 and add them to the candidate list based on the lower bound
            # Heap queue is used for keeping the candidate list sorted
            for node in prod_k1:
                lower_bound = self.compute_lower_bound(node, all_jobs)
                heapq.heappush(candidate_list, (lower_bound, node))
            
            # Randomly select N nodes from the candidate list
            prod_k1 = [heapq.heappop(candidate_list)[1] for _ in range(min(len(candidate_list), int((1 + gamma) * N)))]
            random.shuffle(prod_k1)
            prod_k1 = prod_k1[:N]
            
            # Update the list of the sequence of nodes
            prod_k = prod_k1
            current_level += 1
        
        final_nodes = []
        # Finale level of the tree
        for node in prod_k:
            remaining_jobs_U = [job for job in all_jobs if job not in node]
            for j in remaining_jobs_U:
                final_nodes.append(self.branch_node(j, node))
        
        best_node = min(final_nodes, key=lambda node: self.compute_I_and_C(node)[1])
        _, best_completion_time = self.compute_I_and_C(best_node)
        
        return best_node, best_completion_time



    def local_search(self, solution):
        # return solution
        pass

    def get_fitness(self, solution):
        # return fitness value
        pass

    def perturbation(self, solution):
        # retunr soltuion
        pass