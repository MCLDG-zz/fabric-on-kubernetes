#!/usr/bin/env bash
AWSAccount=295744685835
AWSAccountProfile=blog-tools
region=us-east-2
k8sclusterprefix=mcdg2k8s

#vpc details for cluster: mcdgk8s
#vpcid=vpc-21fb5749
#cidrblock=172.20.0.0/24
#routetableid=rtb-f7ec759f
#subneta=subnet-0f862d67
#subnetb=subnet-5e31d324
#subnetc=subnet-2e86a363
#keypairname=dlt-blockchain-key
#volumename=dltefs

#vpc details for cluster: mcdg2k8s
vpcid=vpc-2725a74f
cidrblock=172.20.0.0/24
routetableid=rtb-1a2a5072
subneta=subnet-067eff6e
subnetb=subnet-d3bc44a9
subnetc=subnet-2e291e63
keypairname=dlt-blockchain-key
volumename=dltefs2

aws cloudformation deploy --stack-name mcdg2k8s-cmd-client --template-file ec2-for-efs/ec2-for-efs.yaml \
--capabilities CAPABILITY_NAMED_IAM \
--parameter-overrides VPCId=$vpcid CidrBlock=$cidrblock RouteTableID=$routetableid \
SubnetA=$subneta SubnetB=$subnetb SubnetC=$subnetc \
KeyName=$keypairname VolumeName=$volumename MountPoint=opt/share \
--profile $AWSAccountProfile --region $region


#aws cloudformation deploy --stack-name ec2-cmd-client-full --template-file ec2-for-efs/full-ec2-for-efs.yaml \
#--capabilities CAPABILITY_NAMED_IAM \
#--parameter-overrides KeyName=dlt-blockchain-key \
#--profile $AWSAccountProfile --region $region
