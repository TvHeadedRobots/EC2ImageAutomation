# To do: Create EC2 instance image form instance ID with current date/time ec2-create-image [instanceId] -n [image name] [--no-reboot],
# add "no-reboot" command switch control
# check instance status (ec2-describe-instance-status)
# if status passed quit else reboot instance
# email status
# use ec2-describe-tags to get instance ids to backup using "backup" tag 

__author__="skiptabor"
__date__ ="$Jun 22, 2015 3:17:48 PM$"

import os
import sys
import time
import subprocess

ec2DescTagsCmd = 'c:/ec2/ec2-api-tools-1.7.4.0/bin/ec2-describe-tags.cmd'
# c:/ec2/ec2-api-tools-1.7.4.0/bin/ec2-create-image.cmd [instanceId] -n "[image name]" --no-reboot
ec2ImgCmd = 'c:/ec2/ec2-api-tools-1.7.4.0/bin/ec2-create-image.cmd'

if sys.argv[1] > 0:
    backupValArg = sys.argv[1]
else:
    backupValArg = 1
    
ec2Tags1d = []

def get_backup_instance(backupVal):
    ec2ImgInstanceId = []
    # run describe tags command and capture output
    exeEc2DescTagsCmd = subprocess.Popen(ec2DescTagsCmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

    ### build list of instance IDs for backup ###
    # get instance ID for backup from describe tag command output
    for line in exeEc2DescTagsCmd.stdout:
        ec2Tags1d.append(line)

    # split each tag line at [TAB] and populate list
    for line in ec2Tags1d:
        tag = line.split('\t')
        #print(tag)
        #print("tag 2: " + tag[2])
        #print("tag 3: " + tag[3])
        #print("tag 4: " + tag[4])

        # check each tag list for "backup" tag name / value and populate ec2ImgInstanceId list
        # backupVal is passed in as CLI argument 1
        if (tag[3] == 'backup' and tag[4].replace('\r\n','') == backupVal):
            ec2ImgInstanceId.append(tag[2])
            #print("tag 2: " + tag[2])
            #print("tag 3: " + tag[3])
            #print("tag 4: " + tag[4])
    return ec2ImgInstanceId

### get "Name" tag name / value for each instance ID to create backup image name
# iterate through ec2ImgInstanceId
def get_backup_img_name(ec2ImgInstanceId):
    ec2ImgName = []
    curdate = time.strftime("%Y%m%d")
    
    for instanceId in ec2ImgInstanceId:
        nameSet = 0
        for line in ec2Tags1d:
            tag = line.split('\t')
            #print("Entered create img name loop")

            # iterate through tag[] to get "Name" name / value for instances in ec2ImgInstanceId
            if (tag[3] == 'Name' and tag[2] == instanceId):
                ec2ImgName.append(tag[4].replace('\r\n','_') + curdate)
                nameSet = 1
            if (tag[3] != 'Name' and tag[2] == instanceId and nameSet == 0):
                ec2ImgName.append(instanceId + '_' + curdate)
                #print('Get instance name conditional: ' + tag[4].replace('\r\n','_') + curdate)
    return ec2ImgName

backupInstances = get_backup_instance(backupValArg)
backupImgName = get_backup_img_name(backupInstances)

if len(backupInstances) != len(backupImgName):
    print("ERROR: List of instances to backup is not the same size as backup image name list.\r\nSomething is wrong and I'm not going any further.")
    print('len(backupImgName) = ')
    print(len(backupImgName))
    print('len(backupInstances) = ')
    print(len(backupInstances))
else:
    for n in range(len(backupInstances)):
        if (len(sys.argv) > '1' and sys.argv[2] == 'reboot'):
            ec2ImgCmd = ec2ImgCmd + ' ' + backupInstances[n] + ' -n "' + backupImgName[n] + '"'
            print('Preforming backup of ' + backupInstances[n] + ' with reboot')
        else:
            ec2ImgCmd = ec2ImgCmd + ' ' + backupInstances[n] + ' -n "' + backupImgName[n] + '"' + ' --no-reboot'
            print('Preforming backup of ' + backupInstances[n] + ' with reboot')
        
        print('Creating image: ' + backupImgName[n] + '...')
        exeEc2ImgCmd = subprocess.Popen(ec2ImgCmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)