# BabelNet Backend

FastAPI-based backend service for BabelNet, providing SOCKS5 proxy functionality, user authentication, and Kubernetes integration simulation.

## Features

- **SOCKS5 Proxy Server**: High-performance TCP traffic forwarding
- **RESTful API**: FastAPI with automatic OpenAPI documentation
- **User Authentication**: Register/login system with session management
- **Kubernetes Mock API**: Simulated K8s endpoints for development
- **Real-time Monitoring**: Proxy status and traffic statistics

## Project Structure

```
backend/
├── app/
│   ├── __init__.py          # Package marker
│   ├── proxy.py             # SOCKS5 proxy + API endpoints
│   ├── auth.py              # User authentication
│   ├── k8s_mock.py          # Kubernetes mock API
│   └── config.py            # Configuration settings
├── main.py                  # FastAPI application entry point
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Installation

```bash
pip install -r requirements.txt
```

## Development

### Start Development Server

```bash
uvicorn main:app --reload
```

The server will be available at: http://localhost:8000

### Interactive API Documentation

Visit http://localhost:8000/docs for Swagger UI documentation.

## API Endpoints

### Authentication

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "username": "user123",
  "password": "password123"
}
```

**Response:**
```json
{
  "msg": "Register success"
}
```

#### Login User
```http
POST /auth/login
Content-Type: application/json

{
  "username": "user123",
  "password": "password123"
}
```

**Response:**
```json
{
  "msg": "Login success",
  "username": "user123"
}
```

### Proxy Management

#### Get Proxy Status
```http
GET /proxy/status
```

**Response:**
```json
{
  "active_connections": 5,
  "total_connections": 100,
  "total_traffic_up": 1024000,
  "total_traffic_down": 2048000
}
```

#### Get Proxy IP
```http
GET /proxy/ip
```

**Response:**
```json
{
  "ip": "192.168.1.100"
}
```

### Kubernetes Mock API

#### Get Pods
```http
GET /k8s/pods
```

**Response:**
```json
{
  "pods": [
    {
      "name": "vpn-proxy-1",
      "status": "Running",
      "ip": "10.0.0.1"
    },
    {
      "name": "vpn-proxy-2",
      "status": "Pending",
      "ip": "10.0.0.2"
    }
  ]
}
```

#### Get Nodes
```http
GET /k8s/nodes
```

**Response:**
```json
{
  "nodes": [
    {
      "name": "node-1",
      "status": "Ready"
    },
    {
      "name": "node-2",
      "status": "NotReady"
    }
  ]
}
```

## SOCKS5 Proxy

The SOCKS5 proxy server runs on port 8888 by default and supports:

- **CONNECT command** for TCP forwarding
- **IPv4 and domain name** target addresses
- **No authentication** (for development)
- **Multi-threaded** client handling
- **Real-time traffic** monitoring

### Usage

Configure your client to use SOCKS5 proxy:
- Host: `localhost` (or your server IP)
- Port: `8888`

### Testing

```bash
# Test with curl
curl --socks5 localhost:8888 http://example.com

# Test with Python
import requests
proxies = {
    'http': 'socks5h://localhost:8888',
    'https': 'socks5h://localhost:8888'
}
response = requests.get('http://httpbin.org/ip', proxies=proxies)
print(response.json())
```

## Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
LISTEN_HOST=0.0.0.0
LISTEN_PORT=8888
API_HOST=0.0.0.0
API_PORT=8000
```

### Development vs Production

- **Development**: Uses in-memory user storage
- **Production**: Ready for database integration (SQLite, PostgreSQL, etc.)

## Deployment

### Local Production

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Docker

```bash
docker build -t babelnet-backend .
docker run -p 8000:8000 -p 8888:8888 babelnet-backend
```

### Kubernetes

The application is designed for Kubernetes deployment with:
- Health check endpoints
- Configurable resource limits
- Horizontal pod autoscaling support

## Development Notes

### Adding New Endpoints

1. Create a new router in the appropriate module
2. Add the router to `main.py`
3. Update this README with the new endpoint documentation

### Database Integration

To add database support:

1. Install database driver (e.g., `sqlalchemy`, `asyncpg`)
2. Create database models
3. Replace in-memory storage with database operations
4. Add database connection management

### Security Considerations

- Add password hashing (bcrypt, argon2)
- Implement JWT tokens for authentication
- Add rate limiting
- Enable HTTPS in production
- Add input validation and sanitization

## Troubleshooting

### Common Issues

1. **Port already in use**: Change ports in config.py
2. **CORS errors**: Configure CORS middleware in main.py
3. **Proxy not working**: Check firewall settings and port availability

### Logs

Enable debug logging by setting the log level:

```bash
uvicorn main:app --log-level debug
```

## Contributing

1. Follow PEP 8 style guidelines
2. Add type hints to functions
3. Write docstrings for all public functions
4. Add tests for new features
5. Update API documentation 