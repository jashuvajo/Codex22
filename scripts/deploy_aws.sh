#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 3 ]]; then
  echo "Usage: $0 <aws-region> <aws-account-id> <acm-certificate-arn>"
  echo "Example: $0 ap-south-1 123456789012 arn:aws:acm:ap-south-1:123456789012:certificate/xxxx"
  exit 1
fi

AWS_REGION="$1"
AWS_ACCOUNT_ID="$2"
ACM_CERT_ARN="$3"
IMAGE_TAG="${IMAGE_TAG:-$(git rev-parse --short HEAD)}"
ECR_REPO="${ECR_REPO:-nexusquant-backend}"
IMAGE_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}:${IMAGE_TAG}"

command -v aws >/dev/null || { echo "aws CLI is required"; exit 1; }
command -v terraform >/dev/null || { echo "terraform is required"; exit 1; }
command -v docker >/dev/null || { echo "docker is required"; exit 1; }

aws ecr describe-repositories --repository-names "$ECR_REPO" --region "$AWS_REGION" >/dev/null 2>&1 ||   aws ecr create-repository --repository-name "$ECR_REPO" --region "$AWS_REGION" >/dev/null

aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

docker build --platform linux/amd64 -t "$IMAGE_URI" ./backend
docker push "$IMAGE_URI"

cd infra/aws
terraform init
terraform apply -auto-approve   -var "aws_region=${AWS_REGION}"   -var "backend_image=${IMAGE_URI}"   -var "acm_certificate_arn=${ACM_CERT_ARN}"   -var "create_route53_record=false"

echo "Deploy complete. Review outputs for ALB DNS and service endpoints."
