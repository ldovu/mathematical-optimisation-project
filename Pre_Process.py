import numpy as np

# NOTE: The matrices containing the data have an extra columns of "-1" in
#       position 0 in order to have job=job_index

class Pre_Process:

    def __init__(self, file_path):
        self.T = None
        self.time_steps = None
        self.processed_jobs = None
        self.setup_bar_times = None
        self.R = None
        self.O = None
        self.A1 = None
        self.A2 = None
        self.A3 = None
        self.A4 = None
        self.n_jobs = None
        self.release_dates = None
        self.processing_times = None
        self.setup_times = None

        self.read_dat(file_path)
        self.compute_greedy_solution()
        self.set_setup_bar_times()
        self.set_R()
        self.set_O()
        self.set_A1()
        self.set_A2()
        self.set_A3()
        self.set_A4()

    def get_n_jobs(self):
        return self.n_jobs
    
    def get_T(self):
        return self.T

    def get_R(self):
        return self.R
    

    def get_O(self):
        return self.O
    

    def get_A1(self):
        return self.A1
    

    def get_A2(self):
        return self.A2
    

    def get_A3(self):
        return self.A3
    

    def get_A4(self):
        return self.A4


    def read_dat(self, file_path):

        with open(file_path, 'r') as file:

            first_line = file.readline().replace("\n", "")
            first_elements = [int(x) for x in first_line.split(" ") if x]
            self.n_jobs = first_elements[0]

            # NOTE: The matrices containing the data have an extra columns of "-1" in
            #       position 0 in order to have job=job_index
            self.release_dates = np.full(self.n_jobs+1, -1)
            self.processing_times = np.full(self.n_jobs+1, -1)
            self.setup_times = np.full([self.n_jobs+1, self.n_jobs+1], -1, dtype=int)

            setup_matrix_rows = 0

            for i, line in enumerate(file):

                line = line.replace("\n", "")
                elements = [int(x) for x in line.split(" ") if x]

                line_length = len(elements)

                if i >= 2 and i < 2+self.n_jobs:
                    if line_length != 4:
                        raise Exception(f"Something is wrong with the {
                                        file_path} file format: Error {1}")
                    job = elements[0]

                    self.release_dates[job] = elements[1]
                    self.processing_times[job] = elements[2]
                    continue

                if i >= 2+self.n_jobs:

                    if line_length != self.n_jobs:
                        raise Exception(f"Something is wrong with the {
                                        file_path} file format: Error {2}")

                    setup_matrix_rows = setup_matrix_rows + 1

                    row_index = setup_matrix_rows - 1

                    for column_index, element in enumerate(elements):

                        job = column_index + 1
                        # Ignore setup times between a job and its self
                        if job == row_index:
                            continue

                        else:
                            self.setup_times[row_index, job] = element

            if setup_matrix_rows != self.n_jobs+1:
                raise Exception(f"Something is wrong with the {
                                file_path} file format: Error {3}")
    

    def compute_greedy_solution(self):

        self.GS_processed_jobs = [0]
        self.GS_time_steps = [0]

        current_time = 0

        for position in range(self.n_jobs):

            best_cost = 100**100
            best_job = 0
            time_increment = 0

            for job_index in range(self.n_jobs):

                job = job_index + 1

                # If the job under evaluation is alredy in the list, continue
                if job in self.GS_processed_jobs:
                    continue

                last_job = self.GS_processed_jobs[-1]
                current_release = self.release_dates[job]
                current_setup = self.setup_times[last_job, job]

                waiting_time = max(current_release - current_time, 0)
                current_cost = waiting_time + current_setup

                # Update the best choice if it's better
                if current_cost < best_cost:
                    best_cost = current_cost
                    best_job = job
                    current_processing = self.processing_times[job]
                    time_increment = current_cost + current_processing

            # Update the processed jobs with the best one found above
            current_time = current_time + time_increment
            self.GS_time_steps.append(current_time)
            self.GS_processed_jobs.append(best_job)

        self.T = int(current_time)

    # Takes the minimum setup time for each column without repeating the row index (excluding -1 values)

    def set_setup_bar_times(self):

        self.setup_bar_times = [-1]

        for job in range(1, self.n_jobs+1):
            column = [row[job] for row in self.setup_times if row[job] != -1]
            self.setup_bar_times.append(min(column))

    # NOTE: R[i] is a list of times t that represent the nodes (i, t)

    def set_R(self):
        self.R = [[] for _ in range(self.n_jobs+1)]
        self.R[0].append(-1)

        for job in range(1, self.n_jobs+1):
            for t in range((self.setup_bar_times[job] + self.release_dates[job] + self.processing_times[job]), self.T+1):
                self.R[job].append(t)

    # NOTE: O is a list of times t that represent the nodes (0, t)

    def set_O(self):
        self.O = [t for t in range(self.T+1)]

    # NOTE: A1[i][j] is a list of tuples (t1, t2) that represent the arcs (i, t1)->(j, t2)
    #       In this case: t2 = t1 + s_ij + p_j

    def set_A1(self):

        self.A1 = [[[] for _ in range(self.n_jobs+1)]
                   for _ in range(self.n_jobs+1)]

        # Fill the first row and first column with -1
        for j in range(self.n_jobs+1):
            self.A1[0][j].append(-1)
            if j != 0:
                self.A1[j][0].append(-1)

        # For each couple of jobs (i, j), without job 0, compute all arcs of type
        # (i, t) -> (j, t + s_ij + p_j)
        for job_i in range(1, self.n_jobs+1):
            for job_j in range(1, self.n_jobs+1):

                # Skip i==j
                if job_i == job_j:
                    self.A1[job_i][job_j].append(-1)
                    continue

                else:
                    # time_span = s_ij + p_j
                    time_span = self.setup_times[job_i][job_j] + \
                        self.processing_times[job_j]
                    # Get the smaller t from the node (job_i, t)
                    first_time_i = self.R[job_i][0]

                    # Get the smaller t from the arcs (job_i, t) -> (job_j, t+time_span)
                    release_date_j = self.release_dates[job_j]
                    initial_time = max(first_time_i, release_date_j)
                    # Get the largest t from the same arcs (job_i, t) -> (job_j, t+time_span)
                    final_time = self.T - time_span

                    # Define all the arcs in the computed range
                    for time in range(initial_time, final_time+1):
                        self.A1[job_i][job_j].append(
                            tuple([time, time+time_span]))

    # NOTE: A2[i] is a list of tuples (t1, t2) that represent the arcs (0, t1)->(i, t2)
    #       In this case: t2 = t1 + s_0j + p_j

    def set_A2(self):

        self.A2 = [[] for _ in range(self.n_jobs+1)]
        # Fill the first row and first column with [-1]
        self.A2[0].append(-1)

        # For each job j (no 0) compute all the arcs of type
        # (0, t) -> (j -> t + s_oj + pj) with the constraint t>=r_j
        for job in range(1, self.n_jobs+1):

            # time_span = s_oj + pj
            time_span = self.setup_times[0][job] + self.processing_times[job]

            # Get the smaller t from the arcs (0, t) -> (job, t+time_span)
            release_date_j = self.release_dates[job]
            # Actually not needed, we leave it like that for uniformity with the code of A1
            initial_time = max(0, release_date_j)

            # Get the largest t from the same arcs (0, t) -> (job, t+time_span)
            final_time = self.T - time_span

            # Define all the arcs in the computed range
            for time in range(initial_time, final_time+1):
                self.A2[job].append(tuple([time, time+time_span]))

    # NOTE: A3[i] is a list of times t that represent the arcs (i, t)->(0, T)

    def set_A3(self):

        self.A3 = [[] for _ in range(self.n_jobs+1)]
        # Fill the first row and first column with [-1]
        self.A3[0].append(-1)

        # For each job j, create an arc that goes from every node (j, t) to the node (0, T)
        # NOTE: (0, T) is omitted from the saved data because it would be redundant
        for job in range(1, self.n_jobs+1):
            for time in self.R[job]:
                self.A3[job].append(time)

    # NOTE: A4[i] is a list of tuples (t1, t2) that represent the arcs (i, t1)->(i, t2)
    #       In this case: t2 = t1 + 1
    # NOTE: In this case we consider also the dummy job (0)

    def set_A4(self):

        self.A4 = [[] for _ in range(self.n_jobs+1)]

        # First create all the arcs of type (0, t) -> (0, t+1)
        for time in self.O:
            if time >= self.T:
                break
            else:
                next_time = self.O[time+1]
                if time+1 != next_time:
                    print(time, next_time)
                    raise Exception("Error in the parsing of matrix O")
                else:
                    self.A4[0].append(tuple([time, next_time]))

        # Then for each job j create all the arcs of type (j, t) -> (j, t+1)
        for job in range(1, self.n_jobs+1):
            # Fixed the job, create all the arcs, starting from (j, s_bar_j + r_j + p_j)
            # Where, s_bar_j + r_j + p_j is the time stored in position 0 of the list R[job]
            for t_index, time in enumerate(self.R[job]):
                if time >= self.T:
                    break
                else:
                    next_time = self.R[job][t_index+1]
                    # Check if the list R[job] is correctly ordered
                    if time+1 != next_time:
                        print(time, next_time)
                        raise Exception("Error in the parsing of matrix R")
                    else:
                        self.A4[job].append(tuple([time, time+1]))
