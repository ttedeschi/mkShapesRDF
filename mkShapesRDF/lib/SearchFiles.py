import fnmatch
import subprocess
import glob
import sys


class SearchFiles:
    def __init__(self):
        # cache result of `glob.glob(folder)` and `xrdfs redirector ls folder`
        self.cached_list_of_files = {}

    def searchFiles(
        self, folder, process, redirector="root://eoscms.cern.ch/", isLatino=True
    ):
        if not folder.endswith("/"):
            folder += "/"

        listOfFiles = []
        if len(self.cached_list_of_files.get(folder, [])) == 0:
            print("Need to query for files for folder", folder)
            if redirector != "":
                print("with redirector", redirector)
                proc = subprocess.Popen(
                    f"xrdfs {redirector} ls {folder}",
                    shell=True,
                    stdout=subprocess.PIPE,
                )
                listOfFiles = proc.communicate()[0].decode("utf-8").split("\n")
            else:
                listOfFiles = glob.glob(folder + "*")
            self.cached_list_of_files[folder] = listOfFiles
        else:
            listOfFiles = self.cached_list_of_files[folder]
        if isLatino:
            process = "nanoLatino_" + process + "__part*.root"
        files = list(
            filter(lambda k: fnmatch.fnmatch(k, folder + process), listOfFiles)
        )
        if redirector != "":
            files = list(map(lambda k: redirector + k, files))

        return files

    def searchFilesDAS(
        self, process, redirector="root://cms-xrd-global.cern.ch/", instance=""
    ):
        files = []
        if (len(self.cached_list_of_files.get(process, []))) == 0:
            procString = f'dasgoclient --query="file dataset={process}'
            if instance != "":
                procString += " instance=" + instance
            procString += '"'

            proc = subprocess.Popen(
                procString, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            out, err = proc.communicate()
            out = out.decode("utf-8")
            out = out.split("\n")
            files = list(filter(lambda k: k.strip() != "", out))
            print(files, len(files))
            err = err.decode("utf-8")
            if len(err) != 0:
                print("There were some errors in retrieving file:")
                print(err)
                sys.exit()
        else:
            files = self.cached_list_of_files[process]

        files = list(map(lambda k: redirector + k, files))
        return files[1:]
