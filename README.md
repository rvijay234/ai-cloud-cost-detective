# AI Cloud Cost Detective

An intelligent AWS cost optimization tool that scans your cloud resources, detects cost issues, and provides AI-powered recommendations for reducing your AWS bill.

## Features

- **AWS Resource Scanning**: Automatically scans EC2, RDS, S3, Load Balancers, and Elastic IPs
- **Cost Issue Detection**: Identifies over-provisioned resources, unused resources, and misconfigurations
- **AI-Powered Analysis**: Uses Groq API to provide intelligent cost optimization recommendations
- **Live Progress Updates**: Real-time WebSocket updates during scanning
- **Detailed Reports**: Comprehensive cost breakdown with fix commands
- **JWT Authentication**: Secure user authentication with signup/login

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **PostgreSQL**: Database for storing scans and analysis results
- **SQLAlchemy**: ORM for database operations
- **Boto3**: AWS SDK for resource scanning
- **Groq API**: AI-powered cost analysis
- **PyJWT + bcrypt**: JWT authentication
- **WebSocket**: Real-time progress streaming

### Frontend
- **React**: UI framework
- **Vite**: Build tool
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **React Router**: Navigation
- **Axios**: HTTP client
- **Lucide React**: Icons

## Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL 13+
- AWS Account with appropriate IAM permissions
- Groq API key

## Environment Variables

### Backend (`.env` in `/backend` directory)
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/cloud_cost_detective
JWT_SECRET_KEY=your-secret-key-here-change-in-production
GROQ_API_KEY=your-groq-api-key
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
```

### Frontend (`.env` in `/frontend` directory)
```bash
VITE_API_URL=http://localhost:8000
```

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd ai-cloud-cost-detective
```

### 2. Backend Setup

#### Install Python Dependencies
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Set Up PostgreSQL Database
```bash
# Create database
createdb cloud_cost_detective

# Or using psql
psql -U postgres
CREATE DATABASE cloud_cost_detective;
\q
```

#### Configure Environment Variables
```bash
cp .env.example .env
# Edit .env with your actual values
```

#### Initialize Database
```bash
# The database tables will be created automatically when you run the app
# Or manually:
python -c "from database import engine, Base; Base.metadata.create_all(bind=engine)"
```

### 3. Frontend Setup

#### Install Node Dependencies
```bash
cd frontend
npm install
```

#### Configure Environment Variables
```bash
cp .env.example .env
# Edit .env if needed (defaults to http://localhost:8000)
```

### 4. Run the Application

#### Start Backend Server
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Start Frontend Development Server
```bash
cd frontend
npm run dev
```

#### Access the Application
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Usage

### 1. Sign Up
- Navigate to http://localhost:5173
- Click "Sign up" and create an account

### 2. Start a Scan
- After logging in, click "New Scan" on the dashboard
- The scan will automatically detect AWS resources in your configured region

### 3. View Results
- Watch the scan progress in real-time via WebSocket updates
- Once complete, view the detailed cost analysis report
- Review AI-powered recommendations with fix commands

### 4. Apply Recommendations
- Copy the provided AWS CLI commands
- Execute them to optimize your AWS resources

## AWS IAM Permissions

The AWS credentials used must have the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:DescribeAddresses",
        "ec2:DescribeTags",
        "rds:DescribeDBInstances",
        "s3:ListAllMyBuckets",
        "s3:GetBucketLocation",
        "s3:ListObjectsV2",
        "elasticloadbalancing:DescribeLoadBalancers",
        "elasticloadbalancing:DescribeLoadBalancerAttributes"
      ],
      "Resource": "*"
    }
  ]
}
```

## Project Structure

```
ai-cloud-cost-detective/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── auth.py              # JWT authentication
│   ├── aws_scanner.py       # AWS resource scanning
│   ├── cost_analyzer.py     # Cost issue detection
│   ├── groq_analyzer.py     # AI analysis integration
│   ├── websocket.py         # WebSocket manager
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── pages/           # React pages
│   │   ├── contexts/        # React contexts
│   │   ├── App.tsx          # Main app component
│   │   ├── main.tsx         # Entry point
│   │   └── index.css        # Tailwind CSS
│   ├── package.json         # Node dependencies
│   ├── vite.config.ts       # Vite configuration
│   ├── tailwind.config.js   # Tailwind configuration
│   └── .env.example         # Environment variables template
├── .gitignore
└── README.md
```

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Create a new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

### Scans
- `POST /api/scans` - Start a new scan
- `GET /api/scans` - List all scans for current user
- `GET /api/scans/{id}` - Get scan details with resources and analysis

### WebSocket
- `WS /ws/scans/{scan_id}` - Real-time scan progress updates

## Cost Detection Rules

The application detects the following cost issues:

### EC2 Instances
- Stopped instances (EBS costs still incur)
- Over-provisioned instance types
- Instances without Name tags

### RDS Instances
- Multi-AZ enabled on non-critical databases
- Over-provisioned instance classes

### S3 Buckets
- Empty buckets
- Large buckets without lifecycle policies

### Load Balancers
- Load balancers with no registered instances

### Elastic IPs
- Unassociated Elastic IPs (charged hourly)

## Development

### Backend Development
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### Build for Production
```bash
cd frontend
npm run build
```

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running
- Check DATABASE_URL in backend/.env
- Verify database exists: `psql -l`

### AWS API Errors
- Verify AWS credentials are correct
- Check IAM permissions
- Ensure region is correct

### Groq API Errors
- Verify GROQ_API_KEY is valid
- Check API quota limits

### WebSocket Connection Issues
- Ensure backend is running on port 8000
- Check firewall settings
- Verify CORS configuration in main.py

## Security Notes

- Change JWT_SECRET_KEY in production
- Use environment variables for all sensitive data
- Enable HTTPS in production
- Implement rate limiting for API endpoints
- Regularly rotate AWS credentials
- Use IAM roles instead of access keys when possible

## License

MIT License

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.
