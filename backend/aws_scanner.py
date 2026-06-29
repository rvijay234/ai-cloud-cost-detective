import boto3
from typing import List, Dict, Any, Optional
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError


class AWSScanner:
    def __init__(self, region: Optional[str] = None):
        self.region = region or 'us-east-1'
        try:
            self.session = boto3.Session(region_name=self.region)
        except (NoCredentialsError, PartialCredentialsError):
            self.session = None
    
    def _get_tag_value(self, tags: List[Dict], key: str) -> str:
        """Extract tag value by key from AWS tags list"""
        if not tags:
            return None
        for tag in tags:
            if tag.get('Key') == key:
                return tag.get('Value')
        return None
    
    def scan_ec2(self) -> List[Dict[str, Any]]:
        """Scan EC2 instances"""
        if not self.session:
            raise ValueError("AWS credentials not configured")
        
        try:
            ec2 = self.session.client('ec2')
            response = ec2.describe_instances()
            resources = []
            
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    resources.append({
                        'type': 'ec2',
                        'name': self._get_tag_value(instance.get('Tags', []), 'Name'),
                        'region': instance['Placement']['AvailabilityZone'][:-1],
                        'instance_type': instance.get('InstanceType'),
                        'instance_id': instance.get('InstanceId'),
                        'state': instance['State']['Name'],
                        'tags': instance.get('Tags', [])
                    })
            
            return resources
        except ClientError as e:
            raise Exception(f"EC2 scan failed: {str(e)}")
    
    def scan_rds(self) -> List[Dict[str, Any]]:
        """Scan RDS instances"""
        if not self.session:
            raise ValueError("AWS credentials not configured")
        
        try:
            rds = self.session.client('rds')
            response = rds.describe_db_instances()
            resources = []
            
            for db in response['DBInstances']:
                resources.append({
                    'type': 'rds',
                    'name': db['DBInstanceIdentifier'],
                    'region': db.get('AvailabilityZone', self.region)[:-1] if db.get('AvailabilityZone') else self.region,
                    'instance_type': db.get('DBInstanceClass'),
                    'instance_id': db['DBInstanceIdentifier'],
                    'engine': db.get('Engine'),
                    'state': db['DBInstanceStatus'],
                    'tags': db.get('TagList', [])
                })
            
            return resources
        except ClientError as e:
            raise Exception(f"RDS scan failed: {str(e)}")
    
    def scan_s3(self) -> List[Dict[str, Any]]:
        """Scan S3 buckets"""
        if not self.session:
            raise ValueError("AWS credentials not configured")
        
        try:
            s3 = self.session.client('s3')
            response = s3.list_buckets()
            resources = []
            
            for bucket in response['Buckets']:
                # Get bucket location
                try:
                    location_response = s3.get_bucket_location(Bucket=bucket['Name'])
                    bucket_region = location_response.get('LocationConstraint') or 'us-east-1'
                except:
                    bucket_region = self.region
                
                resources.append({
                    'type': 's3',
                    'name': bucket['Name'],
                    'region': bucket_region,
                    'instance_type': None,
                    'instance_id': bucket['Name'],
                    'creation_date': bucket['CreationDate'].isoformat(),
                    'tags': []
                })
            
            return resources
        except ClientError as e:
            raise Exception(f"S3 scan failed: {str(e)}")
    
    def scan_elastic_ips(self) -> List[Dict[str, Any]]:
        """Scan Elastic IPs"""
        if not self.session:
            raise ValueError("AWS credentials not configured")
        
        try:
            ec2 = self.session.client('ec2')
            response = ec2.describe_addresses()
            resources = []
            
            for addr in response['Addresses']:
                resources.append({
                    'type': 'eip',
                    'name': addr.get('AssociationId') or addr['PublicIp'],
                    'region': addr.get('Region', self.region),
                    'instance_type': None,
                    'instance_id': addr.get('AllocationId'),
                    'public_ip': addr['PublicIp'],
                    'instance_associated': addr.get('InstanceId') is not None,
                    'tags': addr.get('Tags', [])
                })
            
            return resources
        except ClientError as e:
            raise Exception(f"Elastic IP scan failed: {str(e)}")
    
    def scan_load_balancers(self) -> List[Dict[str, Any]]:
        """Scan Load Balancers (Classic and Application/Network)"""
        if not self.session:
            raise ValueError("AWS credentials not configured")
        
        resources = []
        
        # Scan Classic Load Balancers
        try:
            elb = self.session.client('elb')
            response = elb.describe_load_balancers()
            
            for lb in response['LoadBalancerDescriptions']:
                resources.append({
                    'type': 'elb',
                    'name': lb['LoadBalancerName'],
                    'region': lb['AvailabilityZones'][0][:-1] if lb['AvailabilityZones'] else self.region,
                    'instance_type': 'classic',
                    'instance_id': lb['LoadBalancerName'],
                    'scheme': lb['Scheme'],
                    'dns_name': lb['DNSName'],
                    'instances_count': len(lb['Instances']),
                    'tags': []
                })
        except ClientError as e:
            if 'LoadBalancersNotFound' not in str(e):
                raise Exception(f"Classic ELB scan failed: {str(e)}")
        
        # Scan Application/Network Load Balancers
        try:
            elbv2 = self.session.client('elbv2')
            response = elbv2.describe_load_balancers()
            
            for lb in response['LoadBalancers']:
                resources.append({
                    'type': 'elb',
                    'name': lb['LoadBalancerName'],
                    'region': lb['AvailabilityZones'][0]['SubnetId'].split('-')[0] if lb['AvailabilityZones'] else self.region,
                    'instance_type': lb['Type'],
                    'instance_id': lb['LoadBalancerArn'],
                    'scheme': lb['Scheme'],
                    'dns_name': lb['DNSName'],
                    'state': lb['State']['Code'],
                    'tags': []
                })
        except ClientError as e:
            if 'LoadBalancersNotFound' not in str(e):
                raise Exception(f"Modern ELB scan failed: {str(e)}")
        
        return resources
    
    def scan_all(self) -> Dict[str, List[Dict[str, Any]]]:
        """Scan all AWS resource types"""
        return {
            'ec2': self.scan_ec2(),
            'rds': self.scan_rds(),
            's3': self.scan_s3(),
            'elastic_ips': self.scan_elastic_ips(),
            'load_balancers': self.scan_load_balancers()
        }
