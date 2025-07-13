# FC-VPN

A cloud-native elastic VPN solution with SOCKS5 proxy functionality, featuring a modern web dashboard and Kubernetes integration simulation.

## Features

- **SOCKS5 Proxy Server**: High-performance traffic forwarding with real-time monitoring
- **Modern Web Dashboard**: Beautiful dark-themed UI with real-time status display
- **User Authentication**: Register/login system with session management
- **Kubernetes Integration**: Mock K8s API for pod/node status monitoring
- **Cloud-Native Ready**: Designed for AWS EKS deployment with auto-scaling

## Project Structure

```
fc-vpn/
├── backend/                 # FastAPI backend service
│   ├── app/
│   │   ├── __init__.py
│   │   ├── proxy.py         # SOCKS5 proxy core logic + API endpoints
│   │   ├── auth.py          # User authentication (register/login)
│   │   ├── k8s_mock.py      # Kubernetes mock API
│   │   └── config.py        # Configuration settings
│   ├── main.py              # FastAPI application entry point
│   ├── requirements.txt     # Python dependencies
│   └── README.md           # Backend documentation
├── frontend/                # Vue.js frontend application
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   ├── router.js        # Vue Router configuration
│   │   ├── store.js         # Vuex state management
│   │   ├── pages/           # Page components
│   │   │   ├── Dashboard.vue    # Main dashboard
│   │   │   ├── Login.vue        # Login page
│   │   │   ├── Register.vue     # Registration page
│   │   │   ├── Monitor.vue      # Traffic monitoring
│   │   │   └── Profile.vue      # User profile
│   │   └── components/      # Reusable components
│   │       ├── NetworkStatus.vue
│   │       └── TrafficMonitor.vue
│   ├── public/
│   │   └── index.html
│   ├── package.json
│   ├── vue.config.js        # Vue CLI configuration with proxy
│   └── README.md           # Frontend documentation
├── docker/                  # Docker deployment files
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   └── docker-compose.yml
├── docs/                    # Project documentation
│   ├── proposal.md
│   └── proposal.pdf
└── README.md               # This file
```

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 14+
- npm or yarn

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd fc-vpn
   ```

2. **Start Backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```
   Backend will be available at: http://localhost:8000

3. **Start Frontend**
   ```bash
   cd frontend
   npm install
   npm run serve
   ```
   Frontend will be available at: http://localhost:8080

4. **Access the Application**
   - Dashboard: http://localhost:8080/#/
   - Login: http://localhost:8080/#/login
   - Register: http://localhost:8080/#/register

### Docker Deployment

```bash
cd docker
docker-compose up --build
```

## API Documentation

### Authentication Endpoints

- `POST /auth/register` - User registration
- `POST /auth/login` - User login

### Proxy Endpoints

- `GET /proxy/status` - Get proxy status and statistics
- `GET /proxy/ip` - Get proxy server IP address

### Kubernetes Mock Endpoints

- `GET /k8s/pods` - Get mock pod information
- `GET /k8s/nodes` - Get mock node information

### Interactive API Docs

Visit http://localhost:8000/docs for interactive API documentation (Swagger UI).

## Features in Detail

### SOCKS5 Proxy
- Supports CONNECT command for TCP forwarding
- Handles IPv4 and domain name targets
- Multi-threaded client handling
- Real-time traffic monitoring

### Web Dashboard
- Modern dark theme with gradient background
- Real-time proxy status display
- User authentication status
- Kubernetes pod/node monitoring
- Responsive design

### User Management
- User registration and login
- Session persistence with localStorage
- Secure password handling (ready for database integration)

## Development

### Backend Development
- FastAPI framework with automatic API documentation
- Modular architecture with separate routers
- Ready for database integration (currently using in-memory storage)
- Comprehensive error handling

### Frontend Development
- Vue.js 2.x with Vue Router and Vuex
- Modern ES6+ JavaScript
- Responsive design with CSS Grid/Flexbox
- Proxy configuration for development

## Deployment

### Cloud Deployment (AWS EKS)
The application is designed for Kubernetes deployment with:
- Horizontal pod autoscaling
- Load balancing
- Health checks and monitoring
- Configurable resource limits

### Local Production
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm run build
# Serve the dist/ directory with a web server
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Add your license here]

## Support

For questions and support, please open an issue in the repository.
