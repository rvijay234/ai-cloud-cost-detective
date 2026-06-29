# AI Cloud Cost Detective 🔍

An AI-powered full-stack web application that scans your AWS resources, detects cost inefficiencies, and provides actionable fix commands with estimated monthly savings.

## 🎯 What It Does

- Scans AWS resources (EC2, RDS, S3, Elastic IPs, Load Balancers) using Boto3
- Uses Groq AI (LLaMA 3.3 70B) to analyze resources for cost issues
- Detects over-provisioned, unused, and misconfigured resources
- Provides exact AWS CLI commands to fix each issue
- Shows estimated monthly savings
- Stores analysis history in PostgreSQL
- Real-time progress tracking via polling

## 🏗️ Architecture

```
User → React Frontend (Vite + TypeScript + Tailwind)
              ↓
       FastAPI Backend
         ↙    ↓    ↘
   Boto3   Groq AI  PostgreSQL
   (AWS)  (Analysis) (History)
```

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React + Vite + TypeScript + Tailwind CSS |
| Backend | Python FastAPI |
| Auth | Custom JWT (PyJWT + bcrypt) |
| Cloud Scanner | AWS Boto3 |
| AI Analysis | Groq API (llama-3.3-70b-versatile) |
| Database | PostgreSQL (Docker) |
| Progress | Polling (every 2 seconds) |

## 📋 Prerequisites

- Python 3.10+
- Node.js 18+
- Docker
- AWS Account with IAM credentials
- Groq API key (free at console.groq.com)

## 🚀 Setup & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/rvijay234/ai-cloud-cost-detective.git
cd ai-cloud-cost-detective
```

### 2. Start PostgreSQL with Docker

```bash
docker run -d \
  --name cost-detective-db \
  -e POSTGRES_USER=costadmin \
  -e POSTGRES_PASSWORD=costpass123 \
  -e POSTGRES_DB=costdetective \
  -p 5432:5432 \
  -v costdetective_data:/var/lib/postgresql/data \
  postgres:16-alpine
```

Verify it's running:
```bash
docker ps | grep cost-detective-db
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
nano .env
```

Fill in your `.env`:
```
GROQ_API_KEY=your_groq_api_key
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=ap-southeast-2
DATABASE_URL=postgresql://costadmin:costpass123@localhost:5432/costdetective
JWT_SECRET_KEY=your_random_secret_string
```

Run the backend:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

API docs available at: `http://localhost:8001/docs`

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run the frontend
npm run dev
```

Frontend available at: `http://localhost:5173`

## 📁 Project Structure

```
ai-cloud-cost-detective/
├── backend/
│   ├── main.py              # FastAPI app, routes, background tasks
│   ├── aws_scanner.py       # Boto3 AWS resource scanning
│   ├── groq_analyzer.py     # Groq AI cost analysis
│   ├── db.py                # SQLAlchemy models and DB connection
│   ├── auth.py              # JWT authentication
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # React Router setup
│   │   ├── contexts/
│   │   │   └── AuthContext.tsx    # JWT management
│   │   ├── pages/
│   │   │   ├── Login.tsx         # Login page
│   │   │   ├── Signup.tsx        # Signup page
│   │   │   ├── Dashboard.tsx     # Main dashboard
│   │   │   ├── Report.tsx        # Analysis report
│   │   │   └── History.tsx       # Past analyses
│   │   └── components/
│   │       ├── Navbar.tsx        # Navigation
│   │       └── ProgressTracker.tsx # Analysis progress
│   ├── vite.config.ts       # Vite + proxy config
│   └── package.json
└── README.md
```

## 🔌 API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/auth/signup` | Create account | No |
| POST | `/api/auth/login` | Login, get JWT | No |
| GET | `/api/auth/me` | Get current user | Yes |
| GET | `/api/regions` | List AWS regions | No |
| POST | `/api/analyze` | Start cost analysis | Yes |
| GET | `/api/history` | Get past analyses | Yes |
| GET | `/api/analysis/{id}` | Get analysis details | Yes |

## 💡 What It Detects

- **Unused Elastic IPs** — EIPs not attached to running instances (costs ~$3/month each)
- **Over-provisioned EC2** — Instances sized larger than needed
- **Unused RDS instances** — Idle database instances
- **S3 without lifecycle policies** — Buckets accumulating unnecessary storage costs
- **Idle Load Balancers** — Load balancers with no traffic

## 🔒 Security

- Passwords hashed with bcrypt
- JWT tokens for authentication
- `.env` file excluded from git
- AWS credentials stored only in environment variables

## 🐛 Common Issues & Fixes

### bcrypt version conflict
```bash
pip install bcrypt==4.0.1
```

### Missing email-validator
```bash
pip install pydantic[email] email-validator
```

### Missing python-jose
```bash
pip install python-jose[cryptography]
```

### Port already in use
```bash
pkill -f "uvicorn main:app"
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### AWS AuthFailure
- Check your `.env` has real AWS credentials (not placeholder values)
- Verify credentials work: `aws sts get-caller-identity`
- Make sure IAM user has `ReadOnlyAccess` policy

### Docker read-only filesystem
```bash
docker container prune -f
docker run -d --name cost-detective-db ...
```

## 📊 Request Flow

```
① User signs up/logs in → JWT token stored in localStorage
② User selects AWS region → clicks Run Analysis
③ Frontend sends POST /api/analyze with JWT header
④ Backend creates analysis record in PostgreSQL
⑤ Background task scans AWS resources with Boto3
⑥ Resources sent to Groq AI for cost analysis
⑦ Results stored in PostgreSQL
⑧ Frontend polls GET /api/analysis/{id} every 2 seconds
⑨ On completion, redirects to Report page
⑩ Report shows issues, savings, and AWS CLI fix commands
```

## 🔑 Getting API Keys

### Groq API Key (Free)
1. Go to `https://console.groq.com`
2. Sign up → API Keys → Create key

### AWS Credentials
1. AWS Console → IAM → Users → your user
2. Security Credentials → Create Access Key
3. Attach `ReadOnlyAccess` policy to your IAM user

## 📝 Environment Variables

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Groq API key for AI analysis |
| `AWS_ACCESS_KEY_ID` | AWS IAM access key |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM secret key |
| `AWS_REGION` | Default AWS region (e.g. ap-southeast-2) |
| `DATABASE_URL` | PostgreSQL connection string |
| `JWT_SECRET_KEY` | Secret key for JWT signing |

## 🎓 Learning Outcomes

- Building full-stack AI applications with FastAPI and React
- AWS resource scanning with Boto3
- Integrating LLM APIs (Groq) for intelligent analysis
- JWT authentication implementation
- PostgreSQL with SQLAlchemy ORM
- Background task processing in FastAPI
- Docker for local development databases
- Real-world cost optimization techniques
