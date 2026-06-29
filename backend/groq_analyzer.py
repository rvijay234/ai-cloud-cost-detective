import os
from typing import List, Dict, Any
from groq import Groq
import json


class GroqAnalyzer:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        self.client = Groq(api_key=api_key)
    
    def analyze_resources(self, resources: List[Dict[str, Any]], region: str) -> Dict[str, Any]:
        """
        Analyze AWS resources for cost optimization opportunities using Groq AI
        """
        # Build a summary of resources for the prompt
        resource_summary = self._build_resource_summary(resources)
        
        prompt = f"""
You are an AWS cost optimization expert. Analyze the following AWS resources in the {region} region for cost optimization opportunities.

RESOURCES DATA:
{json.dumps(resource_summary, indent=2)}

Analyze these resources for:
1. Over-provisioned resources (instances larger than needed)
2. Unused/idle resources (stopped instances, empty buckets, unassociated IPs)
3. Misconfigurations (Multi-AZ where not needed, missing tags)
4. Wrong instance types for the workload
5. Cost optimization opportunities

For each issue found, provide:
- Severity (high/medium/low)
- Resource type and identifier
- Description of the issue
- Specific AWS CLI command to fix it
- Estimated monthly savings (in USD)

Return your analysis in this exact JSON format:
{{
    "summary": "Brief summary of the overall cost situation",
    "total_estimated_monthly_savings": <number>,
    "issues": [
        {{
            "severity": "high|medium|low",
            "resource_type": "ec2|rds|s3|eip|elb",
            "resource_id": "<resource identifier>",
            "resource_name": "<resource name if available>",
            "issue": "<description of the issue>",
            "recommendation": "<specific recommendation>",
            "fix_command": "<AWS CLI command to fix>",
            "estimated_savings": <number>
        }}
    ]
}}

Be specific and actionable. Provide real AWS CLI commands that the user can copy and run.
"""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AWS cost optimization expert. Provide specific, actionable recommendations with exact AWS CLI commands. Always respond in valid JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                response_format={"type": "json_object"},
                max_tokens=4096
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            # Fallback to basic analysis if Groq fails
            return self._fallback_analysis(resources, region)
    
    def _build_resource_summary(self, resources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build a structured summary of resources for the AI prompt"""
        summary = {
            "total_resources": len(resources),
            "by_type": {},
            "resources": []
        }
        
        # Group by type
        for resource in resources:
            rtype = resource["type"]
            if rtype not in summary["by_type"]:
                summary["by_type"][rtype] = []
            
            # Add simplified resource info
            resource_info = {
                "type": rtype,
                "name": resource.get("name"),
                "region": resource.get("region"),
                "instance_type": resource.get("instance_type"),
                "instance_id": resource.get("instance_id"),
                "state": resource.get("state"),
                "tags": resource.get("tags", [])
            }
            
            # Add type-specific info
            if rtype == "eip":
                resource_info["public_ip"] = resource.get("public_ip")
                resource_info["instance_associated"] = resource.get("instance_associated")
            elif rtype == "elb":
                resource_info["instances_count"] = resource.get("instances_count")
                resource_info["scheme"] = resource.get("scheme")
            
            summary["by_type"][rtype].append(resource_info)
            summary["resources"].append(resource_info)
        
        return summary
    
    def _fallback_analysis(self, resources: List[Dict[str, Any]], region: str) -> Dict[str, Any]:
        """Basic rule-based analysis if Groq API fails"""
        issues = []
        total_savings = 0
        
        for resource in resources:
            rtype = resource["type"]
            
            # Check for unassociated Elastic IPs (high severity)
            if rtype == "eip" and not resource.get("instance_associated"):
                issues.append({
                    "severity": "high",
                    "resource_type": "eip",
                    "resource_id": resource.get("instance_id"),
                    "resource_name": resource.get("name"),
                    "issue": f"Elastic IP {resource.get('public_ip')} is not associated with any instance",
                    "recommendation": "Release the unassociated Elastic IP to avoid charges",
                    "fix_command": f"aws ec2 release-address --allocation-id {resource.get('instance_id')} --region {region}",
                    "estimated_savings": 3.6  # ~$3.60/month for unassociated EIP
                })
                total_savings += 3.6
            
            # Check for empty S3 buckets (low severity)
            elif rtype == "s3":
                issues.append({
                    "severity": "low",
                    "resource_type": "s3",
                    "resource_id": resource.get("instance_id"),
                    "resource_name": resource.get("name"),
                    "issue": f"S3 bucket {resource.get('name')} may be empty or underutilized",
                    "recommendation": "Review bucket contents and implement lifecycle policies if needed",
                    "fix_command": f"aws s3 ls s3://{resource.get('name')} --region {region}",
                    "estimated_savings": 0
                })
        
        return {
            "summary": f"Basic analysis of {len(resources)} AWS resources in {region}. Found {len(issues)} potential optimization issues.",
            "total_estimated_monthly_savings": total_savings,
            "issues": issues
        }
