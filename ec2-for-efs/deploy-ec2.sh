#!/usr/bin/env bash
AWSAccount=295744685835
AWSAccountProfile=blog-tools
region=us-east-2

aws cloudformation deploy --stack-name ec2-cmd-client --template-file ec2-for-efs/ec2-for-efs.yaml \
--capabilities CAPABILITY_NAMED_IAM \
--parameter-overrides VPCId=vpc-21fb5749 CidrBlock=172.20.0.0/24 RouteTableID=rtb-f7ec759f \
SubnetA=subnet-0f862d67 SubnetB=subnet-5e31d324 SubnetC=subnet-2e86a363 \
KeyName=dlt-blockchain-key VolumeName=dltefs MountPoint=efsmount \
--profile $AWSAccountProfile --region $region


#aws cloudformation deploy --stack-name ec2-cmd-client-full --template-file ec2-for-efs/full-ec2-for-efs.yaml \
#--capabilities CAPABILITY_NAMED_IAM \
#--parameter-overrides KeyName=dlt-blockchain-key \
#--profile $AWSAccountProfile --region $region
