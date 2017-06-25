
## How do I use this on AWS?
One way to get up and running quickly with CTFd on AWS is to use terraform.  

### Requirements
 - Terraform cli 
 - AWS cli (configured)
 - AWS account with an existing key pair, VPC, and at least 2 subnets

``` 
brew install terraform
brew install aws-cli
```

### Usage
In the ./aws directory, create a terraform.tfvars file.  You can copy the existing one, and replace the variables with values appropriate for you.  From within the aws directory:

```
terraform apply
```

###
That's it

