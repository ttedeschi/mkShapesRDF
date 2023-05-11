import fnmatch
import subprocess
import glob


class SearchFiles:
    def __init__(self):
        # cache result of `glob.glob(folder)` and `xrdfs redirector ls folder`
        self.cached_list_of_files = {}

    def searchFiles(self, folder, searchString, xrootd=False):
        _files = []
        listOfFiles = []
        if len(self.cached_list_of_files.get(folder, [])) == 0:
            print("Need to query for files for folder", folder)
            if xrootd:
                redirector = "root://eoscms.cern.ch"
                proc = subprocess.Popen(
                    f"xrdfs {redirector} ls {folder}",
                    shell=True,
                    stdout=subprocess.PIPE,
                )
                listOfFiles = proc.communicate()[0].decode("utf-8").split("\n")
                self.cached_list_of_files[folder] = listOfFiles
            else:
                listOfFiles = glob.glob(folder + "/*")
        else:
            listOfFiles = self.cached_list_of_files[folder]

        _files = list(
            filter(lambda k: fnmatch.fnmatch(k, folder + searchString), listOfFiles)
        )
        if xrootd:
            _files = list(map(lambda k: "root://eoscms.cern.ch/" + k, _files))

        return _files