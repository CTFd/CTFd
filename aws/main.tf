provider "aws" {
  region = "${var.aws_region}"
}

resource "aws_elb" "elb" {
  name = "${var.app_name}"

  subnets = [
    "${var.subnet_ids}",
  ]

  security_groups = [
    "${var.lb_security_group}",
  ]

  listener {
    instance_port     = "8000"
    instance_protocol = "http"
    lb_port           = 80
    lb_protocol       = "http"
  }

  health_check {
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 3
    target              = "HTTP:8000/"
    interval            = 30
  }
}

resource "aws_autoscaling_group" "asg" {
  vpc_zone_identifier = [
    "${var.subnet_ids}",
  ]

  name                  = "${var.app_name}-${aws_launch_configuration.lc.name}"
  max_size              = "1"
  min_size              = "1"
  desired_capacity      = "1"
  wait_for_elb_capacity = "1"
  force_delete          = true
  launch_configuration  = "${aws_launch_configuration.lc.name}"

  load_balancers = [
    "${aws_elb.elb.name}",
  ]

  tag {
    key                 = "Name"
    value               = "${var.app_name}"
    propagate_at_launch = "true"
  }

  lifecycle {
    create_before_destroy = true
  }
}

data "template_file" "userdata" {
  template = "${file("${path.module}/userdata.sh")}"

  vars {
    GUNICORN = "${data.template_file.gunicorn.rendered}"
  }
}

data "template_file" "gunicorn" {
  template = "${file("${path.module}/gunicorn.sh")}"

  vars {
    DATABASE_URL   = "mysql+pymysql://${var.db_user}:${var.db_pass}@${aws_db_instance.default.endpoint}/ctfd"
    DATABASE_CHECK = "${aws_db_instance.default.address} -u ${var.db_user} -p${var.db_pass}"
    BUCKET         = "${aws_s3_bucket.bucket.id}"
  }
}

resource "aws_launch_configuration" "lc" {
  image_id      = "${data.aws_ami.ubuntu.id}"
  instance_type = "t2.micro"
  user_data     = "${data.template_file.userdata.rendered}"
  key_name      = "${var.key_name}"

  security_groups = [
    "${var.app_security_group}",
  ]

  iam_instance_profile = "${aws_iam_instance_profile.iam_instance_profile.id}"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_iam_instance_profile" "iam_instance_profile" {
  name = "${var.app_name}"
  role = "${aws_iam_role.role.name}"
}

resource "aws_db_instance" "default" {
  allocated_storage      = 10
  storage_type           = "gp2"
  engine                 = "mariaDB"
  engine_version         = "10.0.24"
  instance_class         = "db.t2.micro"
  name                   = "ctfdb"
  username               = "${var.db_user}"
  password               = "${var.db_pass}"
  db_subnet_group_name   = "default"
  vpc_security_group_ids = ["${var.app_security_group}"]
}

resource "aws_s3_bucket" "bucket" {
  acl = "private"

  versioning {
    enabled = true
  }
}

data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-xenial-16.04-amd64-server-*"]
  }
}

resource "aws_iam_role_policy" "policy" {
  name = "policy"
  role = "${aws_iam_role.role.id}"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket"
      ],
      "Resource": [
        "${aws_s3_bucket.bucket.arn}"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListObject"
      ],
      "Resource": [
        "${aws_s3_bucket.bucket.arn}/*"
      ]
    }
  ]
}
EOF
}

resource "aws_iam_role" "role" {
  name = "instance_role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    },
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": "s3.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}
