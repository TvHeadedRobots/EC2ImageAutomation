# To do: 
# check instance status (ec2-describe-instance-status)
# if status passed quit else reboot instance
# email status
# add config file to set EC2 API Tools path

__author__="skiptabor"
__date__ ="$Jun 22, 2015 3:17:48 PM$"

import sys
import time
import subprocess

# setup EC2 API Tools commands
ec2DescTagsCmd = 'c:/ec2/ec2-api-tools-1.7.4.0/bin/ec2-describe-tags.cmd'
# c:/ec2/ec2-api-tools-1.7.4.0/bin/ec2-create-image.cmd [instanceId] -n "[image name]" --no-reboot
ec2StatusCmd = 'ec2-describe-instance-status'
curdate = time.strftime('%Y%m%d-%H%M')

# setup log file
amiLog = open('amiLog.txt', 'a')

# check for backup value arg. If no argument assume "1"
# should add input prompt
if sys.argv[1] > 0:
    backupValArg = sys.argv[1]
else:
    backupValArg = 1
    
ec2Tags1d = []

### build list of instance IDs for backup ###
def get_backup_instance(backupVal):
    ec2ImgInstanceId = []
    # run describe tags command and capture output
    exeEc2DescTagsCmd = subprocess.Popen(ec2DescTagsCmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

    # get instance ID for backup from describe tag command output
    for line in exeEc2DescTagsCmd.stdout:
        ec2Tags1d.append(line)

    # split each tag line at [TAB] and populate list
    for line in ec2Tags1d:
        tag = line.split('\t')

        # check each tag list for "backup" tag name / value and populate ec2ImgInstanceId list
        # backupVal is passed in as CLI argument 1
        if (tag[3] == 'backup' and tag[4].replace('\r\n','') == backupVal):
            ec2ImgInstanceId.append(tag[2])

    # return list of instance IDs for backup
    return ec2ImgInstanceId

### get "Name" tag name / value for each instance ID to create backup image name ###
# iterate through ec2ImgInstanceId
def get_backup_img_name(ec2ImgInstanceId):
    ec2ImgName = []

    # iterate through tag[] to get "Name" name / value for instances in ec2ImgInstanceId
    for instanceId in ec2ImgInstanceId:
        nameSet = 0
        for line in ec2Tags1d:
            tag = line.split('\t')
            
            # check to make sure there is a "Name" tag, if not use instance ID
            if (tag[3] == 'Name' and tag[2] == instanceId):
                ec2ImgName.append(tag[4].replace('\r\n','_') + curdate)
                nameSet = 1
            if (tag[3] != 'Name' and tag[2] == instanceId and nameSet == 0):
                ec2ImgName.append(instanceId + '_' + curdate)
    
    # return list of constructed images names for backup            
    return ec2ImgName

def create_ec2_img(backupInstanceList, backupImgNameList):
    # check to make sure that backupInstanceList list is same size as backupImgName list
    
    ec2ImgCmd = 'c:/ec2/ec2-api-tools-1.7.4.0/bin/ec2-create-image.cmd'
    dupeAmiNames = []
    
    if len(backupInstanceList) != len(backupImgNameList):
        print(len(backupImgNameList)) 
        print("ERROR: List of instances to backup is not the same size as backup image name list.\r\nSomething is wrong and I'm not going any further.")
        print('len(backupImgNameList) = ')
        print(len(backupImgNameList))
        print('len(backupInstanceList) = ')
        print(len(backupInstanceList))
        return 
    else:
        for n in range(len(backupInstanceList)):
            if (len(sys.argv) > '1' and sys.argv[2] == 'reboot'):
                ec2ImgCmd = ec2ImgCmd + ' ' + backupInstanceList[n] + ' -n "' + backupImgNameList[n] + '"'
                print('Preforming backup of ' + backupInstanceList[n] + ' with reboot')
            else:
                ec2ImgCmd = ec2ImgCmd + ' ' + backupInstanceList[n] + ' -n "' + backupImgNameList[n] + '"' + ' --no-reboot'
                print('Preforming backup of ' + backupInstanceList[n] + ' with no reboot')
                
            exeEc2ImgCmd = subprocess.Popen(ec2ImgCmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

        print('Creating AMI image named: ' + backupImgNameList[n] + '...')
        
        retVal = []
        # get results from command 
        ec2ImgStdOut = exeEc2ImgCmd.stdout.readline()
        ec2ImgErrOut = exeEc2ImgCmd.stderr.readline()
        
        # parse stdout command result
        retVal = ec2ImgStdOut.split('\t')
                
        #check stdout result to see if an image was created
        if len(retVal) > 0 and retVal[0] == 'IMAGE':
            amiId = retVal[1].replace('\r\n','')
            amiLog.write('AMI created:' + amiId + '\t' + backupImgNameList[n] + '\t' + curdate + '\r\n')
            amiLog.close()
            print('Image ' + amiId + ' created')
            
        # check to see if there was an error returned
        if ec2ImgErrOut != '':
            #print('error: ' + ec2ImgErrOut)
            errRetVal = []
            errRetVal = ec2ImgErrOut.split(' ')

            # check to see if image name already exists
            if errRetVal[0] == 'Client.InvalidAMIName.Duplicate:':
                amiLog.write(backupImgNameList[n] + ' already exists\t' + curdate + '\t' + errRetVal[0] + '\r\n')
                amiLog.close()
                # add duplicate AMI names to list to rerun
                dupeAmiNames.append(backupImgNameList[n])
                print('No AMI created')
                print(ec2ImgErrOut)
            else:
                print('Something happened...')
                print('stdout: ' + ec2ImgStdOut)
                print('errout: ' + ec2ImgErrOut)


        return


# call functions to get backup instances and image names
backupInstances = get_backup_instance(backupValArg)
backupImgNames = get_backup_img_name(backupInstances)
# call function to create images
ec2ImgRun = create_ec2_img(backupInstances, backupImgNames)




    #time.sleep(10)
    #ec2StatusCmd = ec2StatusCmd + ' ' + backupInstances[n]
    #exeEc2StatusCmd = subprocess.Popen(ec2StatusCmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)


