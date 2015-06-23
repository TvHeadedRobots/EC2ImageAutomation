EC2 Instance Image Automation Script
Allows for a process for scheduling and automating EC2 instance image creation

Requirements
-------------

1. Python 2.7.3 or greater
2. EC2 API Tools 1.7.4.0 (ec2-api-tools-1.7.4.0)
   http://aws.amazon.com/developertools/351

CLI usage
---------
ec2imageautomation.py [backup tag value] [reboot]

[backup tag value] (required)
This is the value assigned to a tag with the name of "backup" attached to the 
instance to be imaged. This can be any arbitrary value and be used for selecting
which instance to create images for.

[reboot] (optional)
This argument will cause the instance to reboot for imaging. Not passing this 
argument will cause imaging to proceed without instance reboot. 

Note: Arguments must be passed in in order.

Example:
python ec2imageautomation.py 1
