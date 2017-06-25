output "CTF url" {
  value = "${aws_elb.elb.dns_name}"
}
