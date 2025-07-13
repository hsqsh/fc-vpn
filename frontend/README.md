# BabelNet Frontend

Vue.js-based frontend application for BabelNet, featuring a modern dark-themed dashboard with real-time monitoring and user authentication.

## Features

- **Modern UI**: Dark theme with gradient background and glass-morphism effects
- **Real-time Dashboard**: Live proxy status, traffic monitoring, and K8s integration
- **User Authentication**: Beautiful login/register pages with session management
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Component-based Architecture**: Reusable components for maintainability

## Project Structure

```
frontend/
├── src/
│   ├── App.vue                 # Root component
│   ├── main.js                 # Application entry point
│   ├── router.js               # Vue Router configuration
│   ├── store.js                # Vuex state management
│   ├── pages/                  # Page components
│   │   ├── Dashboard.vue       # Main dashboard with status cards
│   │   ├── Login.vue           # User login page
│   │   ├── Register.vue        # User registration page
│   │   ├── Monitor.vue         # Traffic monitoring page
│   │   └── Profile.vue         # User profile page
│   └── components/             # Reusable components
│       ├── NetworkStatus.vue   # Network status display
│       └── TrafficMonitor.vue  # Traffic monitoring widget
├── public/
│   └── index.html              # HTML template
├── package.json                # Dependencies and scripts
├── vue.config.js               # Vue CLI configuration with proxy
└── README.md                   # This file
```

## Prerequisites

- Node.js 14+
- npm or yarn

## Installation

```bash
npm install
```

## Development

### Start Development Server

```bash
npm run serve
```

The application will be available at: http://localhost:8080

### Development Proxy

The application is configured with a development proxy to communicate with the backend API:

- Backend API: http://localhost:8000
- Proxy configuration: See `vue.config.js`

### Available Scripts

- `npm run serve` - Start development server
- `npm run build` - Build for production
- `npm run lint` - Lint and fix files

## Pages

### Dashboard (`/`)
The main dashboard displays:
- User authentication status (top-right)
- Network status card
- Proxy information (IP, active connections)
- Kubernetes pods and nodes status
- Traffic monitoring section

### Login (`/login`)
- Modern dark-themed login form
- Username/password authentication
- Link to registration page
- Automatic redirect to dashboard on success

### Register (`/register`)
- User registration form
- Link to login page
- Form validation and error handling

### Monitor (`/monitor`)
- Detailed traffic monitoring
- Real-time statistics
- Historical data visualization

### Profile (`/profile`)
- User profile management
- Account settings
- Session information

## Components

### NetworkStatus
Displays current network connectivity status with visual indicators.

**Props:**
- `status` (String): Network status ('online', 'offline', etc.)

### TrafficMonitor
Shows real-time traffic statistics and monitoring data.

**Props:**
- `status` (Object): Traffic status object with connection and traffic data

## Styling

### Design System
- **Color Palette**: Dark theme with low-saturation grays and blues
- **Typography**: Segoe UI font family with proper letter spacing
- **Spacing**: Consistent 8px grid system
- **Shadows**: Subtle shadows for depth and hierarchy

### CSS Classes
- `.auth-page` - Authentication page styling
- `.dashboard` - Dashboard layout and background
- `.card` - Status card components
- `.form-row` - Form input layouts

## State Management

### Vuex Store
The application uses Vuex for global state management:

```javascript
// store.js
export default new Vuex.Store({
  state: {
    // Global application state
  },
  mutations: {
    // State mutations
  },
  actions: {
    // Async actions
  }
});
```

### Local Storage
User authentication state is persisted using localStorage:
- User session data
- Authentication tokens
- User preferences

## API Integration

### Backend Communication
The frontend communicates with the backend through:

- **Authentication**: `/auth/login`, `/auth/register`
- **Proxy Status**: `/proxy/status`, `/proxy/ip`
- **Kubernetes**: `/k8s/pods`, `/k8s/nodes`

### Error Handling
- Network error handling with user-friendly messages
- Form validation and error display
- Graceful degradation for API failures

## Routing

### Vue Router Configuration
```javascript
// router.js
export default new Router({
  routes: [
    { path: '/', component: Dashboard },
    { path: '/login', component: Login },
    { path: '/register', component: Register },
    { path: '/monitor', component: Monitor },
    { path: '/profile', component: Profile }
  ]
});
```

### Navigation Guards
- Authentication checks for protected routes
- Automatic redirects based on user state

## Build and Deployment

### Production Build

```bash
npm run build
```

This creates a `dist/` directory with optimized production files.

### Docker Deployment

```bash
# Build Docker image
docker build -t babelnet-frontend .

# Run container
docker run -p 80:80 babelnet-frontend
```

### Static Hosting
The built application can be deployed to any static hosting service:
- AWS S3 + CloudFront
- Netlify
- Vercel
- GitHub Pages

## Development Guidelines

### Code Style
- Follow Vue.js style guide
- Use ES6+ features
- Implement proper error handling
- Add comments for complex logic

### Component Development
- Use single-file components (.vue)
- Implement proper prop validation
- Emit events for parent communication
- Keep components focused and reusable

### Performance
- Lazy load routes
- Optimize images and assets
- Minimize bundle size
- Implement proper caching strategies

## Troubleshooting

### Common Issues

1. **Proxy not working**: Check `vue.config.js` proxy configuration
2. **CORS errors**: Ensure backend is running and proxy is configured
3. **Build errors**: Check Node.js version and dependencies
4. **Styling issues**: Verify CSS class names and specificity

### Debug Mode
Enable Vue DevTools for debugging:
- Install Vue DevTools browser extension
- Use browser developer tools for network debugging

## Contributing

1. Follow Vue.js conventions
2. Write clean, maintainable code
3. Add proper documentation
4. Test changes thoroughly
5. Update this README when adding new features

## Browser Support

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## Performance Metrics

- First Contentful Paint: < 1.5s
- Largest Contentful Paint: < 2.5s
- Cumulative Layout Shift: < 0.1 