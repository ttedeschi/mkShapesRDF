import subprocess
import numpy as np
import time
import sys


class CheckJobCondor:
    def __init__(
        self,
        cycles_before_exit_on_completed,
        cycles_before_exit_on_held,
        transfer_output,
        remove_job,
    ):
        self.arr = []
        self.job_ids = []
        self.number_of_jobs = 0
        self.JobStatus = [
            "Unexpanded",
            "Idle",
            "Running",
            "Removed",
            "Completed",
            "Held",
            "Submission_err",
            "Unknown",
        ]
        self.job_id = ""
        self.job_status = []
        self.stats = np.zeros(8, dtype=int)
        self.counter_to_exit_completed = 0

        self.counter_to_exit_held = 0

        self.counter_failed_connection = 0

        self.exit_condor = 0

        self.cycles_before_exit_on_completed = cycles_before_exit_on_completed

        self.cycles_before_exit_on_held = cycles_before_exit_on_held
        self.transfer_output = eval(transfer_output)
        self.remove_job = eval(remove_job)

    def execute_condor_q(self):

        try:
            # Run the "condor_q" command to list the Job IDs (Cluster IDs)
            result = subprocess.check_output(
                ["condor_q", "-af", "ClusterId"], universal_newlines=True
            )

            # Split the output into lines and print the Job IDs
            self.job_ids = result.strip().split("\n")

            if len(self.job_ids) > 0:

                self.job_id = self.job_ids[len(self.job_ids) - 1]

            self.counter_failed_connection = 0

        except subprocess.CalledProcessError:
            print("Error running condor_q. Check your HTCondor installation.")

            self.counter_failed_connection = self.counter_failed_connection + 1

    def check_single_job_status(self):

        # if str(self.job_id)!="":

        try:

            command = str(self.job_id)

            print(command)
            # Run the "condor_q" command to list the Job IDs (Cluster IDs)
            result = subprocess.check_output(
                ["condor_q", command, "-af", "JobStatus"], universal_newlines=True
            )

            # print(result)

            self.job_status = result.strip().split("\n")

            # print(self.job_status)

            self.number_of_jobs = len(self.job_status)

            self.counter_failed_connection = 0

        except subprocess.CalledProcessError:
            print("Error running condor_q. Check your HTCondor installation.")

            self.counter_failed_connection = self.counter_failed_connection + 1

    def get_stats(self):

        if self.job_status != [""]:

            for i in range(0, len(self.job_status)):

                if int(self.job_status[i]) <= 6:

                    self.stats[int(self.job_status[i])] = (
                        self.stats[int(self.job_status[i])] + 1
                    )

                else:

                    self.stats[7] = self.stats[7] + 1

        else:

            self.exit_condor = 1

    def print_stats(self):

        for i in range(0, len(self.JobStatus)):

            print(str(self.stats[i]) + " jobs are in state: " + self.JobStatus[i])

    def clean_stats(self):

        for i in range(0, len(self.stats)):

            self.stats[i] = 0

    def check_exit_condition(self):

        if self.stats[4] == len(self.job_status):

            self.counter_to_exit_completed = self.counter_to_exit_completed + 1

        else:

            self.counter_to_exit_completed = 0

        if self.stats[5] == len(self.job_status):

            self.counter_to_exit_held = self.counter_to_exit_held + 1

        else:

            self.counter_to_exit_held = 0

        if self.counter_failed_connection == 10:

            self.exit_condor = 1

        if (
            self.counter_to_exit_completed == self.cycles_before_exit_on_completed
            or self.counter_to_exit_held == self.cycles_before_exit_on_held
        ):

            self.exit_condor = 1

    def on_exit_action(self):

        if self.counter_to_exit_completed == self.cycles_before_exit_on_completed:

            print("Exit on completed jobs")

            self.transfer_output_files()

            self.RemoveJob()

        elif self.counter_to_exit_held == self.cycles_before_exit_on_held:

            print("Exit on held jobs condition")

            self.CheckHoldCondition()

            self.transfer_output_files()

            self.RemoveJob()

        elif self.counter_failed_connection == 10:

            print("Exit on not established connection")

    def transfer_output_files(self):

        if str(self.job_id) != "":

            if self.transfer_output:

                bash_command = "condor_transfer_data " + str(self.job_id)

                result = subprocess.run(
                    bash_command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

                if result.returncode == 0:

                    print("Command output:")
                    print(result.stdout)

                else:

                    print("Command failed with error:")
                    print(result.stderr)

    def check_running_jobs(self, sleep):

        self.execute_condor_q()

        while self.exit_condor != 1:

            self.check_single_job_status()

            self.get_stats()

            self.check_exit_condition()

            self.print_stats()

            self.clean_stats()

            time.sleep(sleep)

        self.on_exit_action()

    def CheckHoldCondition(self):

        bash_command = "condor_q -hold " + str(self.job_id)

        result = subprocess.run(
            bash_command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if result.returncode == 0:

            print("Command output:")
            print(result.stdout)

        else:

            print("Command failed with error:")
            print(result.stderr)

    def RemoveJob(self):

        if str(self.job_id) != "":

            if self.remove_job:

                print("Now removing jobs")

                bash_command = "condor_rm " + str(self.job_id)

                result = subprocess.run(
                    bash_command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

                if result.returncode == 0:

                    print("Command output:")
                    print(result.stdout)

                else:

                    print("Command failed with error:")
                    print(result.stderr)


def main():

    p1 = CheckJobCondor(
        cycles_before_exit_on_completed=3,
        cycles_before_exit_on_held=3,
        transfer_output=sys.argv[1],
        remove_job=sys.argv[2],
    )

    p1.check_running_jobs(5)


if __name__ == "__main__":
    main()
