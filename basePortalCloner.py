#!/usr/bin/env python

import json
import os
from pathlib import Path
from subprocess import STDOUT, call, Popen, PIPE
from sys import exit, argv, stdout

class colors:
    NORMAL = '\u001b[0m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\u001b[33m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'



logo = colors.BOLD + colors.YELLOW + """

888888b.        8888888b.        .d8888b.
888  "88b       888   Y88b      d88P  Y88b
888  .88P       888    888      888    888
8888888K.       888   d88P      888
888  "Y88b      8888888P"       888
888    888      888             888    888
888   d88P      888             Y88b  d88P
8888888P"       888              "Y8888P"

""" + colors.NORMAL

pathToRepos = argv[1]
thisFolderUrl = pathToRepos + '/templatesTools/basePortalCloner/'
jsonFile = open(thisFolderUrl + 'portals.json', 'r', encoding="utf-8")
portalObject = json.load(jsonFile)

#
# Output menu
#
def menu():
    count = 0
    namesArray = []
    print(colors.YELLOW + '\nSelect portal to copy:\n' + colors.NORMAL)
    for portal in portalObject:
        count = count + 1
        print(colors.BLUE + "(" + str(count) + ") " + colors.YELLOW + portalObject[portal]['name'] + colors.NORMAL)
        namesArray.append(portal)
    ### validate input between parameters allowed
    portalsLength = len(portalObject)
    indexChosen = 0
    indexInRange = False
    indexIsNumeric = False
    counter = 0
    while not indexInRange or not indexIsNumeric:
        indexChosen = input(colors.YELLOW + '\nEnter number [1-' + str(portalsLength) + '] -> ' + colors.NORMAL)
        indexIsNumeric = indexChosen.isnumeric()
        if indexIsNumeric:
            indexInRange = (1 <= int(indexChosen) <= portalsLength)
        counter = counter + 1
        if not indexInRange or not indexIsNumeric:
            print(colors.RED + 'Wrong index' + colors.NORMAL)
        if counter >= 3:
            print(colors.BOLD + colors.RED + "3rd warning, exiting now..." + colors.NORMAL)
            exit()
    portalChosen = namesArray[int(indexChosen) - 1]
    return portalChosen

#
# Validate branch and create new one
#
def createBranch():
    proceed = input(colors.YELLOW + 'Would you like to create a new branch? [y/n]' + colors.NORMAL)
    if proceed in ["y", "Y"]:

        branchName = input(colors.YELLOW + 'Enter the branch name: ' + colors.NORMAL)

        p = Popen(['git', 'rev-parse', '--verify', '--quiet', str(branchName)], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        branchCount, err = p.communicate(b"input data that is passed to subprocess' stdin")
        branchCountStr = str(branchCount).replace("b'","").replace("\\n'","").replace("'","")

        if branchCountStr:
            updateBranch = "git pull"
            print(colors.RED + "Branch " + colors.BOLD + str(branchName) + colors.NORMAL + colors.RED + " already exists. Checking out to it!" + colors.NORMAL)
            checkout = "git checkout " + str(branchName)
            call(checkout, shell=True)
            call(updateBranch, shell=True)
            print(colors.GREEN + "Correctly updated branch " + colors.BOLD + str(branchName) + colors.NORMAL)
        else:
            try:
                checkoutNew = "git checkout -b " + str(branchName)
                push = "git push --set-upstream origin " + str(branchName)
                call(checkoutNew, shell=True)
                call(push, shell=True)
            except:
                print(colors.RED + "Error creating " + colors.BOLD + branchName + colors.NORMAL + colors.RED + ", exiting!" + colors.NORMAL)
                exit()
    elif proceed in ["n", "N"]:
        print(colors.RED + "Not allowed to work from stable, exiting!" + colors.NORMAL)
        exit()
    else:
        print(colors.RED + "Option not recognized, exiting!" + colors.NORMAL)
        exit()

#
# Check if stable
#
def checkIfStable():
    try:
        p = Popen(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        branchName, err = p.communicate(b"input data that is passed to subprocess' stdin")
        branchNameStr = str(branchName).replace("b'","").replace("\\n'","")
    except:
        print(colors.RED + "Folder is not a valid git repository, exiting!" + colors.NORMAL)
        exit()
    else:
        if "stable" in str(branchName):
            print(colors.RED + 'You are in stable branch!' + colors.NORMAL)
            createBranch()
        else:
            print(colors.YELLOW + "You are in " + colors.BOLD + branchNameStr + "!" + colors.NORMAL)
            isGood = input(colors.YELLOW + 'Would you like to keep working here? [y/n]' + colors.NORMAL)
            if isGood in ["n", "N"]:
                try:
                    checkoutStable = "git checkout stable"
                    call(checkoutStable, shell=True)
                except:
                    print(colors.RED + 'Issue checking out to stable, exiting!' + colors.NORMAL)
                    exit()
                createBranch()

#
# Update main repository before copying
#
def updateRepo(repoPath, base):
    checkoutStableCmd = "git -C " + repoPath + "/ checkout stable"
    pullStableCmd = "git -C " + repoPath + "/ pull"
    print(colors.YELLOW + "Initiating update of " + colors.BOLD + base + "..." + colors.NORMAL)
    try:
        call(checkoutStableCmd, shell=True)
    except:
        print(colors.RED + "Problem checking out to stable in main repo, exiting" + colors.NORMAL)
        exit()
    else:
        try:
            call(pullStableCmd, shell=True)
        except:
            print(colors.RED + "Problem updating main repo, exiting!" + colors.NORMAL)
            exit()
        else:
            print(colors.GREEN + "Main repository updated correctly!" + colors.NORMAL)
            # Print out what repo has been updated?

#
# Prompt for new folder name and check it is new folder
#
def newFolder(count = 0):
    newPortalName = input(colors.YELLOW + "\nName of new portal: " + colors.NORMAL)
    p = Path(newPortalName + "/")
    try:
        p.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        count += 1
        print(count)
        if count < 3:
            print(colors.RED + "Folder name being used! Choose a different name" + colors.NORMAL)
            newFolder(count)
        else:
            print(colors.RED + colors.BOLD + "3rd warning, exiting now..." + colors.NORMAL)
            exit()
    else:
        print(colors.YELLOW + "Folder " + colors.BOLD + newPortalName + colors.NORMAL + colors.YELLOW + " has been created!" + colors.NORMAL)
    return newPortalName

def copyPortal(pathToRepoToCopy, newPortalName):
    newPortalUrl = "./" + newPortalName
    print(newPortalUrl)
    copyString = "cp -r " + pathToRepoToCopy + "/* " + newPortalUrl
    print(copyString)
    try:
        call(copyString, shell=True)
        print(colors.GREEN + "Portal copied successfully!\n" + colors.NORMAL)
    except:
        print(colors.RED + "Problem copying portal, exiting!" + colors.NORMAL)
        exit()

print(logo)
checkIfStable()

# Creating repository to copy path
portalChosen = menu()
portalChosenUrl = "/" + portalObject[portalChosen]['base'] + portalObject[portalChosen]['url']
pathToRepoToCopy = pathToRepos + portalChosenUrl
base = portalObject[portalChosen]['base']

updateRepo(pathToRepoToCopy, base)

# Creating path to new portal and copying
newPortalName = newFolder()
copyPortal(pathToRepoToCopy, newPortalName)
enterNewFolderString = "cd " + newPortalName
call(enterNewFolderString, shell=True) #not working, why?
print(colors.GREEN + colors.BOLD + "Process completed successfully. Exiting!\n" + colors.NORMAL)

# TODO: reduce colors.#### to shorter strings
# TODO: encapsulate in namespace
# TODO: create branch name maker (prompt for case ID, get folder name, add timestamp)
# TODO: initiate voutique or hybrid if nonexistent
# TODO: Working on GUI