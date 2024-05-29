import numpy as np

class Beam_Search:

    def __init__(self, file_path):
        self.arcs = None
        self.tree_length = None
        self.n_jobs = None
        self.list_active_nodes = None
        self.all_nodes = None
        self.set_not_scheduled_jobs_U = None
           
        
    def get_tree_length(self):
        return self.tree_length
    
    def get_node_to_branch(self):
        return self.node_to_branch
    
    def get_gamma(self):
        return self.gamma
    
    def set_idle_time_I(self, job, previous_job):
        pass 
    
    def set_beta(self, job, previous_job):
        pass
    
    def set_lower_bound(self, job):
        pass

    def set_completion_time_C():
        pass
        
    # TODO: - introduce randomic aspect with variable gamma
    #       - understand U(i)  
    def Beam_Search(self, N, w, gamma):
        tree_level = 0
        
        list_all_nodes = []
        list_all_nodes.append(['*']*self.n_jobs)
        
        auxiliary_list = []
        tree_length = self.n_jobs
        
        while (tree_level < (tree_length - 1)):
            list_all_nodes[tree_level+1] = auxiliary_list
            
            list_remaining_jobs = []
            
            # list_all_nodes = [𝜋1, 𝜋2, ..., 𝜋k]
            for node in list_all_nodes[tree_level]:
                copy_list_remaining_jobs = list_remaining_jobs[node]
                
                # While there are more than 2 branches in a node
                while len(copy_list_remaining_jobs)>w :
                    # First selection on the I value 
                    job_to_discard = max(self.set_idle_time_I(
                        node[job_to_discard], node[job_to_discard-1]))
                    copy_list_remaining_jobs.remove(job_to_discard)
                for job in copy_list_remaining_jobs:
                    list_all_nodes[tree_level+1]+= self.set_beta(job, job-1)
                    
            while len(list_all_nodes[tree_level+1])>N:
                # Second selection on the LB value
                node_to_remove = max(self.set_lower_bound(i for i in list_all_nodes[tree_level+1]))
                list_all_nodes[tree_level+1].remove(node_to_remove)
            tree_level += 1
            
        list_all_nodes[tree_level] = auxiliary_list
        for node in list_all_nodes[tree_level]:
            for job in list_remaining_jobs[node]:
                list_all_nodes[tree_level]+= self.set_beta(job, job-1)
                
        return min(self.set_completion_time_C(i for i in list_all_nodes[tree_level]))
    