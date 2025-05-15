import boto3
import time
import os

session = boto3.Session(profile_name='default',region_name='us-west-2')
ec2 = session.resource('ec2')


def Create_bucket():
    # Create an S3 client
    s3_client = session.client('s3')

    # Check if the bucket exists
    bucket_name = 'api-pokemon-'+ str(int(time.time()))

    def bucket_exists(bucket_name):
        # s3_client = boto3.client('s3')
        response = s3_client.list_buckets()
        buckets = [bucket['Name'] for bucket in response.get('Buckets', [])]
        # print (f'List of buckets: {buckets}')
        return bucket_name in buckets
    bucket_exists (bucket_name)

    if bucket_exists(bucket_name):
        print(f'Bucket {bucket_name} exists.')
    else:
        s3_client.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={
            'LocationConstraint': session.region_name
        }    
        )
        print(f'Bucket {bucket_name} created in {session.region_name} region')




def create_ec2_with_game_dependencies():
    # Initialize boto3 EC2 client
    region_name='us-west-2'
    ec2 = boto3.resource('ec2',region_name)  # Change region as needed
    ec2_client = boto3.client('ec2',region_name)  

    # Key pair name
    key_pair_name = 'pokemon-key'+ str(int(time.time()))
    key_file_path = f'{key_pair_name}.pem'
    response = ec2_client.create_key_pair(KeyName=key_pair_name)
    with open(key_file_path, 'w') as key_file:
            key_file.write(response['KeyMaterial'])
    os.chmod(key_file_path, 400)       

    # existing_keys = ec2_client.describe_key_pairs()
    # key_exists = any(key['KeyName'] == key_pair_name for key in existing_keys.get('KeyPairs', []))
    
    # if not key_exists:
    #     print(f"Creating new key pair: {key_pair_name}")
    #     response = ec2_client.create_key_pair(KeyName=key_pair_name)
        
    #     # Save the private key to a file
    #     with open(key_file_path, 'w') as key_file:
    #         key_file.write(response['KeyMaterial'])
        
    #     # Set correct permissions for the key file
    #     os.chmod(key_file_path, 400)
        
    #     print(f"Key pair created and saved to {key_file_path}")
    # else:
    #     print(f"Using existing key pair: {key_pair_name}")
    #     print(f"Make sure you have the private key file {key_file_path}")
    
    
    
    # Create security group with GUARANTEED SSH access
    security_group_name = 'pokemon-group'
    try:
        # Try to get existing security group
        response = ec2_client.describe_security_groups(
            Filters=[
                {'Name': 'group-name', 'Values': [security_group_name]}
            ]
        )
        if response['SecurityGroups']:
            security_group_id = response['SecurityGroups'][0]['GroupId']
            print(f"Using existing security group: {security_group_name} ({security_group_id})")
            
            # Make sure SSH is allowed - add it again to be certain
            try:
                ec2_client.authorize_security_group_ingress(
                    GroupId=security_group_id,
                    IpPermissions=[
                        {
                            'IpProtocol': 'tcp',
                            'FromPort': 22,
                            'ToPort': 22,
                            'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'SSH access from anywhere'}]
                        }
                    ]
                )
                print("Added SSH rule to security group")
            except ec2_client.exceptions.ClientError as e:
                if 'already exists' in str(e):
                    print("SSH rule already exists in security group")
                else:
                    raise
        else:
            raise ec2_client.exceptions.ClientError({"Error": {"Code": "InvalidGroup.NotFound"}}, "DescribeSecurityGroups")
            
    except ec2_client.exceptions.ClientError:
        print(f"Creating new security group: {security_group_name}")
        
        # Get default VPC ID
        vpc_response = ec2_client.describe_vpcs(
            Filters=[{'Name': 'isDefault', 'Values': ['true']}]
        )
        vpc_id = vpc_response['Vpcs'][0]['VpcId']
        
        # Create security group
        sg_response = ec2_client.create_security_group(
            GroupName=security_group_name,
            Description='Security group for Python game EC2 instance with SSH access',
            VpcId=vpc_id
        )
        security_group_id = sg_response['GroupId']
        
        # Add SSH inbound rule - explicitly allow from anywhere
        ec2_client.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 22,
                    'ToPort': 22,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'SSH access from anywhere'}]
                }
            ]
        )
        print(f"Security group created with SSH access: {security_group_id}")
    #seperate to a file

    # Bash script to install dependencies and setup your Python game
    user_data_script = user_data_script.txt
    """#!/bin/bash
    # Update package lists
    sudo yum  update -y

    # amazon-linux-extras enable python3.9

    yum install -y python3.9
    
    # Create symbolic links to make this the default python3
    # alternatives --set python3 /usr/bin/python3.9
    
    # Install pip for this specific version
    python3.9 -m ensurepip --upgrade
    python3.9 -m pip install --upgrade pip
    
    # Create a virtual environment with this specific Python version
    python3.9 -m venv /opt/python-game/venv

    source /opt/python-game/venv/bin/activate
    pip install pandas numpy pygame

    # Install git
    sudo yum  install -y git
    
    # Install system dependencies that might be needed for your game
    sudo yum install -y python3-dev libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
    
    # Create a directory for your game
    # mkdir -p /opt/API_POKEMON

    # clone from git
    git clone https://github.com/YoelTokatly/API_Pokemon.git /opt/python-game/API_Pokemon

    sudo chmod -p 400 pokemon2.db

    # Install Python game dependencies
    pip3 install --upgrade pip
    pip3 install -r /opt/python-game/API_Pokemon/requirements.txt
    pip3 install pygame numpy pandas sqlite3 requests random json

    

    
    # Or you could download your game files from S3
    # aws s3 cp s3://your-bucket/your-game.zip /opt/python-game/
    # cd /opt/python-game && unzip your-game.zip
    
    # Set up  environment variables
    echo 'export GAME_HOME=/opt/python-game' >> /etc/environment
    
    # Optional: Set the game to run on startup
    echo "@reboot python3 /opt/python-game/main.py" | crontab -
    
    # Log the completion of the setup
    echo "Game setup completed at $(date)" > /opt/python-game/setup_complete.log
    """
    
    # Create the EC2 instance
    instances = ec2.create_instances(
        ImageId='ami-07b0c09aab6e66ee9',  
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',  
        KeyName=key_pair_name,  
        SecurityGroupIds=[security_group_id],  
        UserData=user_data_script,
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'PythonGameServer'
                    },
                ]
            },
        ],
        BlockDeviceMappings=[
            {
                'DeviceName': '/dev/xvda',
                'Ebs': {
                    'VolumeSize': 8,  # Size in GB
                    'VolumeType': 'gp2',
                    'DeleteOnTermination': True
                }
            },
        ]
    )
    
    instance = instances[0]
    print(f"Waiting for instance {instance.id} to be running...")
    instance.wait_until_running()
    
    # Reload the instance to get the updated public IP
    instance.reload()
    
    print(f"Instance {instance.id} is now running")
    print(f"Public IP: {instance.public_ip_address}")
    print(f"Public DNS: {instance.public_dns_name}")
    print("\nTo connect to your instance via SSH:")
    print(f"ssh -i {key_file_path} ec2-user@{instance.public_dns_name}")
    
    return instance

if __name__ == "__main__":
    instance = create_ec2_with_game_dependencies()
    print("EC2 instance for Python game created successfully!")
    print("Note: The user-data script is still running in background.")
    print("You can SSH into the instance once it completes setup.")
    
