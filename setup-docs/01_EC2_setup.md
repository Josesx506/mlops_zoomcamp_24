### Set up an ec2 instance from CLI
Setup instruction developed from this Youtube [tutorial](https://www.youtube.com/watch?v=sIx7MO4rcCU) after configuring your aws cli with an access and secret key. <br><br>

**Implementation Steps**
- [x] Create key-pair and activate it
- [x] Create security group
    - [x] Specify inbound security group from your ip
- [x] Launch an instance, stop, and restart.
- [x] Terminate an instance

1. Check for existing key pairs
    ```bash
    $ aws ec2 describe-key-pairs
    ```
2. Create a new key-pair if you don't have one
    ```bash
    $ aws ec2 create-key-pair --key-name "mlops-zmcp-24-key-pair" --query "KeyMaterial" --output text > key-pairs/mlops-zmcp-24-key-pair.pem

    # Check the keypair name and id
    $ aws ec2 describe-key-pairs

    # Make it executable
    $ chmod 400 key-pairs/mlops-zmcp-24-key-pair.pem
    ```
3. Create security groups 
    ```bash
    # View any default security groups
    $ aws ec2 describe-security-groups
    ```
    1. Create a new security group
        ```bash
        # Check for  VPC ids (You can copy the default and add it to env for replication) 
        aws ec2 describe-vpcs

        # Create the security group
        aws ec2 create-security-group --group-name zmcp-sg --description "security-group-for-zoomcamp-24" --vpc-id vpc-*********

        # View the new security group
        $ aws ec2 describe-security-groups
        ```
    2. Assign ***ingress rules*** for this new group using your computers ip and specific port. You can check your local ip on https://checkip.amazonaws.com/. 
        ```bash
        # Create the ingress rule. It only worked with port 32 for me. It didnt work with port 42.
        $ aws ec2 authorize-security-group-ingress \
            --group-id sg-********* \
            --protocol tcp \
            --port 22 \
            --cidr **.*.***.***/32
        
        $ aws ec2 describe-security-groups
        ```
4. Copy an ami for a EC2 instance from the [aws-web-console-ec2](). I'm using the *Ubuntu Server 24.04 LTS (HVM), SSD Volume Type*. Access the subnet details with 
    ```bash
    $ aws ec2 describe-subnets --query "Subnets[*].[VpcId,AvailabilityZone,SubnetId]"
    ``` 
    For the **us-east-1** region, 6 public subnets are created by default and you can select a SubnetId from any one of them. I used the first one in my terminal with ***us-east-1c***.
    | key | details |
    | :------ | :------ |
    | AMI ID: | ami-0e001c9271cf7f3b9 |
    | Security Group ID: | sg-********* |
    | Subnet ID: | subnet-********* | 
    Pass all these details into the cli which launches the instance
    ```bash
    $ aws ec2 run-instances --image-id ami-0e001c9271cf7f3b9 \
        --count 1 \
        --instance-type t2.micro\
        --key-name mlops-zmcp-24-key-pair\
        --security-group-ids sg-*********\
        --subnet-id subnet-*********
    ```
5. You can check the instance status from the web console or with terminal.
    ```bash
    # Check the instance status and public IP address
    $ aws ec2 describe-instances \
        --query "Reservations[*].Instances[*].{Instance:InstanceId,PublicIpAddress:PublicIpAddress}"
    ```
    You can copy the `PublicIpAddress` from the cli or web console and use it to configure your ssh file. Navigate to the `~/.ssh` folder and creae a config file without any extensions. Populate the config file using this template
    ```bash
    Host  zmcp-t2micro        # You can name the instance with any name you want
        HostName 52.90.47.92  # public ip address goes here
        User ubuntu
        IdentityFile /path/to/pem/file/mlops-zmcp-24-key-pair.pem
        StrictHostKeyChecking no
    ```
    Now you can login to the instance from vs-code
6. Once you launch the instance, if you're not on a free tier, you start getting charged so you need to stop it when you're not using it. First get the instance Id
    ```bash
    # Get the instance id
    $ aws ec2 describe-instances --query "Reservations[*].Instances[*].{Instance:InstanceId,Subnet:SubnetId}"
    
    # Stop the instance
    $ aws ec2 stop-instances --instance-ids i-076ccf45ef2245ff6
    ```
7. After stopping, you can restart it at a later time and extract the public IP address with 
    ```bash
    $ aws ec2 start-instances --instance-ids i-076ccf45ef2245ff6
    $ aws ec2 describe-instances --query "Reservations[*].Instances[*].{Instance:InstanceId,PublicIpAddress:PublicIpAddress}"
    ```
8. For this tutorial, I deleted all the `security groups | instances | key-pairs ` after testing because the zoomcamp hadn't started yet.
    ```bash
    # key pairs
    $ aws ec2 describe-key-pairs
    $ aws ec2 delete-key-pair --key-name mlops-zmcp-24-key-pair

    # Instance
    $ aws ec2 describe-instances --query "Reservations[*].Instances[*].{Instance:InstanceId}"
    $ aws ec2 terminate-instances --instance-ids i-076ccf45ef2245ff6

    # Key pairs
    $ aws ec2 describe-security-groups --query "SecurityGroups[*].[GroupName,GroupId]" 
    $ aws ec2 delete-security-group --group-id sg-0e944865452c82bc9
    ```
9. Once all that is deleted you shouldn't be charged or you'll be charged less than $1.