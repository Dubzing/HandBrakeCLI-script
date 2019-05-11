import os
import shutil
import time
import psutil

# You can edit this #

Done = "Done" #the last folder where the files will be placed (puts them in the right dir and subdir)
TODO = "TODO" #the last folder where the videos will be pulled from (goes through subfolders and takes all files)
Folder = "C:/Videos/" #This is the dir were you have the "TODO" Folder


# Example #
# if you want the videos in C:/Videos/UnEncoded to be encoded and placed in C:/Videos/Encoded:
# Done = "Encoded"
# TODO = "UnEncoded"
# Folder = "C:/Videos/"


HandBrake = "D:/Program/HandBrake/HandBrakeCLI.exe" #path to your HandBrakeCLI
extension = ".mkv" #what video format it should output. .mkv or .mp4 only


DelSmallVideo = False # If you cancel the encoding in the beginning this can help you del unfinished encodings. Default = False
FileSize = 50 #Under this size(MB) the video will be deleted. Only if "DelSmallVideo" is True. Default = 50

TimerOn = False # spams the terminal Defualt = False

#Here you can change handbrake arguments. This uses by defualt "H.265 MKV 1080p30" with all subs and dubs and no chapters
#Do use input and output (-i and -o). It is configured by defualt and can make the script give errors
code = "start " + HandBrake + ' -m --no-markers -Z "H.265 MKV 1080p30" --all-audio --all-subtitles'
#If you want the encoding to happen in the python window remove < "start " + >
#But I recommend to have python open a new window so you can see the log.

# Don't edit anything below this #

# Defining Functions #

def findProcessIdByName(processName):

    #Get a list of all the PIDs of a all the running process whose name contains
    #the given string processName

    listOfProcessObjects = []

    # Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=['pid', 'name', 'create_time'])
            # Check if process name contains the given name string.
            if processName.lower() in pinfo['name'].lower():
                listOfProcessObjects.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return listOfProcessObjects;

def timer (TIME):
    while TIME >= 0:
        if TimerOn:
            print ("Encoding in Progress. Next check in " + str(TIME) + "sec")
        time.sleep(1)
        TIME -= 1

def copyDirNoFiles (dir, des):
    def ig_f(dir, files):
        return [f for f in files if os.path.isfile(os.path.join(dir, f))]
    shutil.copytree(dir, des, ignore=ig_f)

# Main Code #

Encoding_start = Folder + TODO #dir with all the dir and subdir of videos
Encoding_end = Folder + Done #dir where the files will be copyed to (within all the right dir and subdir)
files = []
RealFileSize = FileSize * 1000000 #makes the size from MB to B
Formats = [".mkv", ".mp4"]

# r=root, d=directories, f = files
for r, d, f in os.walk(Encoding_start):
    for file in f:
        if ".mkv" in file:
            files.append(os.path.join(r, file))
        elif ".mp4" in file:
            files.append(os.path.join(r, file))


try:
    copyDirNoFiles(Encoding_start,Encoding_end)
    print("copying dir and subdir")
    time.sleep(2)
except:
    print("!!!OBS!!! dir and subdir is already created")
    print('If the dir and subdir is not completed del the ' + Encoding_end + ' folder and restart script')
    time.sleep(4)

firstTime = True
for f in files:
    Start = True
    NewVideoDir = f.replace(TODO, Done)
    if ".mp4" in NewVideoDir:
        if ".mkv" in extension:
            NewVideoDir = NewVideoDir.replace(".mp4", ".mkv")
    if os.path.isfile(NewVideoDir):
        if DelSmallVideo:
            if firstTime:
                if RealFileSize >= os.path.getsize(NewVideoDir):
                    print(NewVideoDir + " exists but is to small, removing and starting new encoding.")
                    time.sleep(1)
                    print('In 30 sec it will delete all other small video files as the program goes.')
                    print('If this was a mistake cancel the script and turn off "DelSmallVideo"')
                    time.sleep(30)
                    firstTime = False
                    print("removed " + NewVideoDir)
                    os.remove(NewVideoDir)
                else:
                    print( "Already exists " + NewVideoDir)
                    Start = False
            else:
                print("removed " + NewVideoDir)
                os.remove(NewVideoDir)
        else:
            print( "Already exists " + NewVideoDir)
            Start = False
    if Start:
        batchCode = code + ' -i "' + f.replace("\\", "/") + '" -o "' + NewVideoDir.replace("\\", "/") + '"'
        os.system(batchCode)
        print("Encoding has started on " + NewVideoDir)
        checkIfEncoding = True
        while checkIfEncoding:
            listOfProcessIds = findProcessIdByName('HandBrakeCLI')
            if len(listOfProcessIds) > 0:
                timer(5)
            else:
                checkIfEncoding = False
                print(NewVideoDir + "Is done Encoding starting next one.")
