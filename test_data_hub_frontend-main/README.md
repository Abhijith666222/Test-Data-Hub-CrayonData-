# Test Data Environment - Frontend

A modern, Windows-style React application for AI-powered synthetic data generation and validation.

## 🚀 Features

- **Modern Windows UI**: Clean, intuitive interface that looks and feels like a native Windows application
- **Multi-page Application**: Complete workflow from data source connection to data generation and validation
- **Real-time Updates**: WebSocket-based real-time logging and progress tracking
- **Responsive Design**: Works seamlessly on desktop and tablet devices
- **TypeScript**: Full type safety and better development experience
- **Tailwind CSS**: Modern styling with custom Windows-inspired design system

## 📋 Prerequisites

- Node.js 16+ 
- npm or yarn
- Backend server running (see main README for backend setup)

## 🛠️ Installation

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Start the development server:**
   ```bash
   npm start
   # or
   yarn start
   ```

4. **Open your browser:**
   Navigate to `http://localhost:3000`

## 🏗️ Project Structure

```
frontend/
├── public/                 # Static files
│   ├── index.html         # Main HTML template
│   └── favicon.ico        # App icon
├── src/
│   ├── components/        # Reusable UI components
│   │   └── Layout.tsx     # Main layout with sidebar
│   ├── context/           # React context for state management
│   │   └── AppContext.tsx # Main application state
│   ├── pages/             # Page components
│   │   ├── HomePage.tsx           # Dashboard/home page
│   │   ├── ProductOverviewPage.tsx # Product features overview
│   │   ├── CreateSystemPage.tsx   # Product selection
│   │   ├── DataSourcePage.tsx     # Data source configuration
│   │   ├── SchemaAnalysisPage.tsx # Schema analysis results
│   │   ├── DataGenerationPage.tsx # Data generation and preview
│   │   ├── DestinationPage.tsx    # Destination configuration
│   │   └── RunDetailsPage.tsx     # Individual run details
│   ├── services/          # API services
│   │   └── apiService.ts  # Backend communication
│   ├── App.tsx            # Main app component with routing
│   ├── index.tsx          # App entry point
│   └── index.css          # Global styles and Tailwind imports
├── package.json           # Dependencies and scripts
├── tailwind.config.js     # Tailwind CSS configuration
├── postcss.config.js      # PostCSS configuration
└── tsconfig.json          # TypeScript configuration
```

## 🎨 Design System

The application uses a custom Windows-inspired design system built with Tailwind CSS:

### Colors
- **Windows Colors**: Neutral grays for backgrounds and text
- **Accent Colors**: Blue tones for primary actions and highlights
- **Status Colors**: Green (success), Yellow (warning), Red (error)

### Components
- **Cards**: Windows-style cards with subtle shadows and borders
- **Buttons**: Multiple button styles (primary, secondary, success, warning, error)
- **Forms**: Consistent form inputs with focus states
- **Tables**: Data grids with sorting and pagination
- **Modals**: Overlay dialogs for confirmations and forms

### Typography
- **Font Family**: Segoe UI (Windows system font)
- **Font Sizes**: Consistent scale from xs to 4xl
- **Font Weights**: Regular, medium, semibold, bold

## 📱 Pages Overview

### 1. Home Page (`/`)
- Dashboard with existing runs overview
- Quick statistics and status cards
- Navigation to create new systems
- Recent runs list with quick actions

### 2. Product Overview (`/overview`)
- Feature showcase and capabilities
- Product line descriptions
- Use cases and technology stack
- Call-to-action sections

### 3. Create System (`/create`)
- Product selection cards
- Feature comparison
- Available vs. coming soon products

### 4. Data Source (`/data-source`)
- Multiple data source type selection
- Connection configuration forms
- Sample data option for demo mode
- Collapsible configuration sections

### 5. Schema Analysis (`/schema-analysis`)
- AI analysis results display
- Collapsible table details
- Test scenario selection
- Natural language scenario input

### 6. Data Generation (`/data-generation`)
- File explorer sidebar
- Data preview with sorting and filtering
- Pagination and search functionality
- Export and push options

### 7. Destination (`/destination`)
- Destination type selection
- Connection configuration
- Data transfer progress
- Security notices

### 8. Run Details (`/run/:id`)
- Individual run information
- Status overview and quick actions
- File management
- Configuration settings

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the frontend directory:

```env
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

### API Configuration
The application communicates with the backend through the `apiService.ts` file. Update the `API_BASE_URL` constant if your backend runs on a different port.

## 🚀 Deployment

### Quick Start

1. **Build for Production:**
   ```bash
   npm run build
   # or
   yarn build
   ```

2. **Deploy to Render:**
   ```bash
   npm run deploy:render
   ```

3. **Full Deployment Check:**
   ```bash
   npm run deploy:check
   ```

### Deployment Options

#### Render (Recommended)
- **Automatic**: Use `render.yaml` for instant setup
- **Manual**: Follow [DEPLOYMENT.md](./DEPLOYMENT.md) for step-by-step guide
- **Scripts**: Use `scripts/deploy.bat` (Windows) or `scripts/deploy.sh` (Linux/Mac)

#### Other Platforms
- **Vercel**: Connect GitHub repo, automatic deployments
- **Netlify**: Drag & drop build folder or connect repo
- **GitHub Pages**: Use `gh-pages` package

### Environment Configuration

Create `.env` file based on `env.example`:

```env
REACT_APP_API_BASE_URL=https://your-backend-domain.com
REACT_APP_WS_URL=wss://your-backend-domain.com
REACT_APP_APP_ENVIRONMENT=production
```

### Production Build

```bash
# Build optimized production bundle
npm run build

# Serve locally for testing
npm install -g serve
serve -s build -l 3000
```

### Docker Deployment

```dockerfile
FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

**📖 For detailed deployment instructions, see [DEPLOYMENT.md](./DEPLOYMENT.md)**

## 🧪 Development

### Available Scripts
- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App

### Code Style
- Use TypeScript for all new components
- Follow the existing component structure
- Use Tailwind CSS classes for styling
- Implement proper error handling
- Add loading states for async operations

### Adding New Pages
1. Create a new component in `src/pages/`
2. Add the route to `src/App.tsx`
3. Update the navigation in `src/components/Layout.tsx`
4. Add any necessary API calls to `src/services/apiService.ts`

## 🔗 Integration

### Backend API
The frontend integrates with the FastAPI backend through REST endpoints and WebSocket connections:

- **REST API**: Data operations, file management, run management
- **WebSocket**: Real-time logging and progress updates
- **File Downloads**: CSV and JSON file previews

### State Management
Uses React Context for global state management:
- Current run information
- Selected products and configurations
- Loading states and error handling
- Real-time logs

## 🐛 Troubleshooting

### Common Issues

1. **Backend Connection Failed**
   - Ensure the backend server is running on port 8000
   - Check CORS configuration in the backend
   - Verify API endpoints are accessible

2. **Build Errors**
   - Clear node_modules and reinstall dependencies
   - Check TypeScript configuration
   - Verify all imports are correct

3. **Styling Issues**
   - Ensure Tailwind CSS is properly configured
   - Check for conflicting CSS rules
   - Verify PostCSS configuration

### Development Tips

- Use React Developer Tools for debugging
- Check the browser console for API errors
- Monitor WebSocket connections in Network tab
- Use the Redux DevTools for state inspection

## 📄 License

This project is part of the Test Data Environment system. See the main README for license information.

## 🤝 Contributing

1. Follow the existing code style and patterns
2. Add proper TypeScript types for new features
3. Include loading states and error handling
4. Test on different screen sizes
5. Update documentation for new features

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the backend documentation
3. Check the main project README
4. Open an issue in the project repository 