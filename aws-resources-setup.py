import boto3
import configparser
config = configparser.ConfigParser()
config.read_file(open('dwh.cfg'))

KEY                    = config.get('AWS','KEY')
SECRET                 = config.get('AWS','SECRET')

DWH_CLUSTER_TYPE       = config.get("DWH","DWH_CLUSTER_TYPE")
DWH_NUM_NODES          = config.get("DWH","DWH_NUM_NODES")
DWH_NODE_TYPE          = config.get("DWH","DWH_NODE_TYPE")

DWH_CLUSTER_IDENTIFIER = config.get("DWH","DWH_CLUSTER_IDENTIFIER")
DWH_DB                 = config.get("DWH","DWH_DB")
DWH_DB_USER            = config.get("DWH","DWH_DB_USER")
DWH_DB_PASSWORD        = config.get("DWH","DWH_DB_PASSWORD")
DWH_PORT               = config.get("DWH","DWH_PORT")

DWH_IAM_ROLE_NAME      = config.get("DWH", "DWH_IAM_ROLE_NAME")

# (DWH_DB_USER, DWH_DB_PASSWORD, DWH_DB)

pd.DataFrame({"Param":
                  ["DWH_CLUSTER_TYPE", "DWH_NUM_NODES", "DWH_NODE_TYPE", "DWH_CLUSTER_IDENTIFIER", "DWH_DB", "DWH_DB_USER", "DWH_DB_PASSWORD", "DWH_PORT", "DWH_IAM_ROLE_NAME"],
              "Value":
                  [DWH_CLUSTER_TYPE, DWH_NUM_NODES, DWH_NODE_TYPE, DWH_CLUSTER_IDENTIFIER, DWH_DB, DWH_DB_USER, DWH_DB_PASSWORD, DWH_PORT, DWH_IAM_ROLE_NAME]
             })



# Create clients and resources for IAM, EC2, S3, and Redshift

# To interact with EC2 and S3, utilize boto3.resource; for IAM and Redshift, use boto3.client. If you require additional details on boto3, refer to the boto3 documentation.

# Note: We create clients and resources in the us-west-2 region. Choose the same region in your AWS Web Console to see these resources.



ec2 = boto3.resource('ec2',
                       region_name="us-east-1",
                       aws_access_key_id=KEY,
                       aws_secret_access_key=SECRET
                    )

s3 = boto3.resource('s3',
                       region_name="us-east-1",
                       aws_access_key_id=KEY,
                       aws_secret_access_key=SECRET
                   )

iam = boto3.client('iam',aws_access_key_id=KEY,
                    aws_secret_access_key=SECRET,
                    region_name="us-east-1",
                  )

redshift = boto3.client('redshift',
                        region_name="us-east-1",
                        aws_access_key_id=KEY,
                        aws_secret_access_key=SECRET
                       )



from botocore.exceptions import ClientError

#1.1 Create the role, 
try:
    print("1.1 Creating a new IAM Role") 
    dwhRole = iam.create_role(
        Path='/',
        RoleName=DWH_IAM_ROLE_NAME,
        Description = "Allows Redshift clusters to call AWS services on your behalf.",
        AssumeRolePolicyDocument=json.dumps(
            {'Statement': [{'Action': 'sts:AssumeRole',
               'Effect': 'Allow',
               'Principal': {'Service': 'redshift.amazonaws.com'}}],
               'Version': '2012-10-17'})
    )    
except Exception as e:
    print(e)
    
    
print("1.2 Attaching Policy")

iam.attach_role_policy(RoleName=DWH_IAM_ROLE_NAME,
                       PolicyArn="arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
                      )['ResponseMetadata']['HTTPStatusCode']

print("1.3 Get the IAM role ARN")
roleArn = iam.get_role(RoleName=DWH_IAM_ROLE_NAME)['Role']['Arn']

print(roleArn)


# STEP 2:  Redshift Cluster

# - Create a [RedShift Cluster](https://console.aws.amazon.com/redshiftv2/home)
# - For complete arguments to `create_cluster`, see [docs](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift.html#Redshift.Client.create_cluster)

try:
    response = redshift.create_cluster(        
        #HW
        ClusterType=DWH_CLUSTER_TYPE,
        NodeType=DWH_NODE_TYPE,
        NumberOfNodes=int(DWH_NUM_NODES),

        #Identifiers & Credentials
        DBName=DWH_DB,
        ClusterIdentifier=DWH_CLUSTER_IDENTIFIER,
        MasterUsername=DWH_DB_USER,
        MasterUserPassword=DWH_DB_PASSWORD,
        
        #Roles (for s3 access)
        IamRoles=[roleArn]  
    )
except Exception as e:
    print(e)



def prettyRedshiftProps(props):
    pd.set_option('display.max_colwidth', -1)
    keysTo
Jupyter Notebook
L3 Exercise 2 - IaC - Solution Last Checkpoint: 12/19/2023 (autosaved) Current Kernel Logo

Python 3

    File
    Edit
    View
    Insert
    Cell
    Kernel
    Widgets
    Help

Exercise 2: Creating Redshift Cluster using the AWS python SDK
An example of Infrastructure-as-code

import pandas as pd

import boto3

import json

STEP 0: (Prerequisite) Save the AWS Access key
1. Create a new IAM user

IAM service is a global service, meaning newly created IAM users are not restricted to a specific region by default.

    Go to AWS IAM service and click on the "Add user" button to create a new IAM user in your AWS account.
    Choose a name of your choice.
    Select "Programmatic access" as the access type. Click Next.
    Choose the Attach existing policies directly tab, and select the "AdministratorAccess". Click Next.
    Skip adding any tags. Click Next.
    Review and create the user. It will show you a pair of access key ID and secret.
    Take note of the pair of access key ID and secret. This pair is collectively known as Access key.



Snapshot of a pair of an Access key
2. Save the access key and secret

Edit the file dwh.cfg in the same folder as this notebook and save the access key and secret against the following variables:

KEY= <YOUR_AWS_KEY>
SECRET= <YOUR_AWS_SECRET>

For example:

KEY=6JW3ATLQ34PH3AKI
SECRET=wnoBHA+qUBFgwCRHJqgqrLU0i

3. Troubleshoot

If your keys are not working, such as getting an InvalidAccessKeyId error, then you cannot retrieve them again. You have either of the following two options:

    Option 1 - Create a new pair of access keys for the existing user

        Go to the IAM dashboard and view the details of the existing (Admin) user.

        Select on the Security credentials tab, and click the Create access key button. It will generate a new pair of access key ID and secret.

        Save the new access key ID and secret in your dwh.cfg file



Snapshot of creating a new Access keys for the existing user

    Option 2 - Create a new IAM user with Admin access - Refer to the instructions at the top.

Load DWH Params from a file

import configparser

config = configparser.ConfigParser()

config.read_file(open('dwh.cfg'))

​

KEY                    = config.get('AWS','KEY')

SECRET                 = config.get('AWS','SECRET')

​

DWH_CLUSTER_TYPE       = config.get("DWH","DWH_CLUSTER_TYPE")

DWH_NUM_NODES          = config.get("DWH","DWH_NUM_NODES")

DWH_NODE_TYPE          = config.get("DWH","DWH_NODE_TYPE")

​

DWH_CLUSTER_IDENTIFIER = config.get("DWH","DWH_CLUSTER_IDENTIFIER")

DWH_DB                 = config.get("DWH","DWH_DB")

DWH_DB_USER            = config.get("DWH","DWH_DB_USER")

DWH_DB_PASSWORD        = config.get("DWH","DWH_DB_PASSWORD")

DWH_PORT               = config.get("DWH","DWH_PORT")

​

DWH_IAM_ROLE_NAME      = config.get("DWH", "DWH_IAM_ROLE_NAME")

​

(DWH_DB_USER, DWH_DB_PASSWORD, DWH_DB)

​

pd.DataFrame({"Param":

                  ["DWH_CLUSTER_TYPE", "DWH_NUM_NODES", "DWH_NODE_TYPE", "DWH_CLUSTER_IDENTIFIER", "DWH_DB", "DWH_DB_USER", "DWH_DB_PASSWORD", "DWH_PORT", "DWH_IAM_ROLE_NAME"],

              "Value":

                  [DWH_CLUSTER_TYPE, DWH_NUM_NODES, DWH_NODE_TYPE, DWH_CLUSTER_IDENTIFIER, DWH_DB, DWH_DB_USER, DWH_DB_PASSWORD, DWH_PORT, DWH_IAM_ROLE_NAME]

             })

	Param 	Value
0 	DWH_CLUSTER_TYPE 	multi-node
1 	DWH_NUM_NODES 	4
2 	DWH_NODE_TYPE 	dc2.large
3 	DWH_CLUSTER_IDENTIFIER 	dwhCluster
4 	DWH_DB 	dwh
5 	DWH_DB_USER 	dwhuser
6 	DWH_DB_PASSWORD 	Passw0rd
7 	DWH_PORT 	5439
8 	DWH_IAM_ROLE_NAME 	dwhRole

(DWH_DB_USER, DWH_DB_PASSWORD, DWH_DB)

('dwhuser', 'Passw0rd', 'dwh')

Create clients and resources for IAM, EC2, S3, and Redshift

To interact with EC2 and S3, utilize boto3.resource; for IAM and Redshift, use boto3.client. If you require additional details on boto3, refer to the boto3 documentation.

Note: We create clients and resources in the us-west-2 region. Choose the same region in your AWS Web Console to see these resources.

import boto3

​

ec2 = boto3.resource('ec2',

                       region_name="us-west-2",

                       aws_access_key_id=KEY,

                       aws_secret_access_key=SECRET

                    )

​

s3 = boto3.resource('s3',

                       region_name="us-west-2",

                       aws_access_key_id=KEY,

                       aws_secret_access_key=SECRET

                   )

​

iam = boto3.client('iam',aws_access_key_id=KEY,

                     aws_secret_access_key=SECRET,

                     region_name='us-west-2'

                  )

​

redshift = boto3.client('redshift',

                       region_name="us-west-2",

                       aws_access_key_id=KEY,

                       aws_secret_access_key=SECRET

                       )

Check out the sample data sources on S3

sampleDbBucket =  s3.Bucket("awssampledbuswest2")

for obj in sampleDbBucket.objects.filter(Prefix="ssbgz"):

    print(obj)

# for obj in sampleDbBucket.objects.all():

#     print(obj)

STEP 1: IAM ROLE

    Create an IAM Role that makes Redshift able to access S3 bucket (ReadOnly)

from botocore.exceptions import ClientError

​

#1.1 Create the role, 

try:

    print("1.1 Creating a new IAM Role") 

    dwhRole = iam.create_role(

        Path='/',

        RoleName=DWH_IAM_ROLE_NAME,

        Description = "Allows Redshift clusters to call AWS services on your behalf.",

        AssumeRolePolicyDocument=json.dumps(

            {'Statement': [{'Action': 'sts:AssumeRole',

               'Effect': 'Allow',

               'Principal': {'Service': 'redshift.amazonaws.com'}}],

             'Version': '2012-10-17'})

    )    

except Exception as e:

    print(e)

    

    

print("1.2 Attaching Policy")

​

iam.attach_role_policy(RoleName=DWH_IAM_ROLE_NAME,

                       PolicyArn="arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"

                      )['ResponseMetadata']['HTTPStatusCode']

​

print("1.3 Get the IAM role ARN")

roleArn = iam.get_role(RoleName=DWH_IAM_ROLE_NAME)['Role']['Arn']

​

print(roleArn)

STEP 2: Redshift Cluster

    Create a RedShift Cluster
    For complete arguments to create_cluster, see docs

try:

    response = redshift.create_cluster(        

        #HW

        ClusterType=DWH_CLUSTER_TYPE,

        NodeType=DWH_NODE_TYPE,

        NumberOfNodes=int(DWH_NUM_NODES),

​

        #Identifiers & Credentials

        DBName=DWH_DB,

        ClusterIdentifier=DWH_CLUSTER_IDENTIFIER,

        MasterUsername=DWH_DB_USER,

        MasterUserPassword=DWH_DB_PASSWORD,

        

        #Roles (for s3 access)

        IamRoles=[roleArn]  

    )

except Exception as e:

    print(e)

2.1 Show = ["ClusterIdentifier", "NodeType", "ClusterStatus", "MasterUsername", "DBName", "Endpoint", "NumberOfNodes", 'VpcId']
    x = [(k, v) for k,v in props.items() if k in keysToShow]
    return pd.DataFrame(data=x, columns=["Key", "Value"])

myClusterProps = redshift.describe_clusters(ClusterIdentifier=DWH_CLUSTER_IDENTIFIER)['Clusters'][0]
prettyRedshiftProps(myClusterProps)