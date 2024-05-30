import random
import numpy as np
import os

class GenerateIstances:
    """
    Generation procedure described by Ovacikt et al. in: 
        "Rolling horizon algorithms for a single-machine dybamic scheduling problem with sequence-dependent
         setup times" 
        (1994) International Journal of Production Research
    """
    def __init__(self, n_jobs, dispersion, processing_times_interval = [1, 100],
                 setup_times_interval = [1, 100]):

        self.n_jobs = n_jobs
        self.dispersion = dispersion
        self.processing_times_interval = processing_times_interval
        self.setup_times_interval = setup_times_interval
        avg_processing_time = (processing_times_interval[1] - processing_times_interval[0]) / 2
        self.release_dates_interval = [1, int(n_jobs * dispersion * avg_processing_time)]
        
        self.release_dates = np.full(self.n_jobs+1, -1)
        self.processing_times = np.full(self.n_jobs+1, -1)
        self.setup_times = np.full([self.n_jobs+1, self.n_jobs+1], -1, dtype=int)

        self.generate()


    def randint_from_interval(self, interval):
        return random.randint(interval[0], interval[1])


    def generate(self):

        for i in range(0, self.n_jobs+1):

            if i != 0:
                self.processing_times[i] = self.randint_from_interval(self.processing_times_interval)
                self.release_dates[i] = self.randint_from_interval(self.release_dates_interval)

            for j in range(0, self.n_jobs+1):
                # setup time i -> j
                if j!=0 and i!=j:
                    self.setup_times[i, j] = self.randint_from_interval(self.setup_times_interval)

    
    # Specify the path where the folder have to be stored
    # The folder will contain 3 files csv, one for each datastructure
    def export_csv(self):
        parent_folder = os.getcwd().replace("\\","/")+ "/GeneratedIstances"
        folder_name = "{:02d}".format(int(self.n_jobs)) + "n_" + "{:02d}".format(int(10*self.dispersion)) + "R"
        if folder_name in os.listdir(parent_folder):
            i = 1
            while folder_name+str(f"_{i}") in os.listdir(parent_folder):
                i = i + 1
            folder_name = folder_name + str(f"_{i}")
        path = parent_folder + "/" + folder_name 
        os.mkdir(path)
        np.savetxt(path + "/release_dates.csv", self.release_dates, delimiter=",", fmt='%i')
        np.savetxt(path + "/processing_times.csv", self.processing_times, delimiter=",", fmt='%i')
        np.savetxt(path + "/setup_times.csv", self.setup_times, delimiter=",", fmt='%i')
        print("Files exported in: ", path)
        



            

            
            

