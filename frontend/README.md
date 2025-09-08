# SEO Agent Dashboard Frontend

A modern, responsive web interface for the SEO Agent API. This frontend provides an intuitive way to interact with the SEO analysis capabilities of the backend service.

## Features

### 🎯 Core Functionality
- **SEO Query Analysis**: Submit natural language queries for SEO analysis
- **Real-time Results**: Get instant feedback and detailed analysis results
- **Query History**: Keep track of previous queries for easy reuse
- **Export Results**: Download analysis results as JSON files

### 🎨 User Interface
- **Modern Design**: Clean, professional interface with gradient backgrounds
- **Responsive Layout**: Works seamlessly on desktop, tablet, and mobile devices
- **Dark/Light Elements**: Optimized for readability and user experience
- **Interactive Components**: Hover effects, animations, and smooth transitions

### 📊 Results Display
- **Analysis Summary**: Clear overview of the SEO analysis results
- **Keyword Extraction**: Automatically extracted keywords from the analysis
- **Metrics Dashboard**: Visual metrics and statistics
- **Raw Data View**: Complete JSON response for developers

### 🚀 Technical Features
- **API Integration**: Seamless connection to FastAPI backend
- **Error Handling**: Graceful error handling with user-friendly messages
- **Local Storage**: Persistent query history and preferences
- **Toast Notifications**: Real-time feedback for user actions
- **Keyboard Shortcuts**: Ctrl/Cmd+Enter to analyze, Escape to focus input

## Getting Started

### Prerequisites
- FastAPI backend server running on `http://localhost:8000`
- Modern web browser with JavaScript enabled

### Running the Frontend

#### Option 1: Through FastAPI (Recommended)
1. Start your FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```
2. Open your browser and navigate to:
   ```
   http://localhost:8000
   ```

#### Option 2: Direct File Access
1. Open `frontend/index.html` directly in your web browser
2. Ensure the FastAPI server is running for API functionality

### Usage

1. **Enter Your Query**: Type your SEO-related question or request in the text area
2. **Analyze**: Click the "Analyze" button or press Ctrl/Cmd+Enter
3. **View Results**: Review the analysis summary, keywords, metrics, and raw response
4. **Export Data**: Use the export button to download results as JSON
5. **Query History**: Click on previous queries in the sidebar to reuse them

## API Configuration

The frontend is configured to connect to the FastAPI backend at `http://localhost:8000`. If your backend is running on a different port or host, update the `API_BASE_URL` in `js/api.js`:

```javascript
const API_BASE_URL = 'http://your-backend-host:port';
```

## File Structure

```
frontend/
├── index.html          # Main HTML file
├── css/
│   └── styles.css      # All styles and responsive design
├── js/
│   ├── api.js          # API service and backend communication
│   ├── ui.js           # UI controller and interface management
│   └── main.js         # Main application logic and initialization
└── README.md           # This file
```

## Browser Compatibility

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Development

### Adding New Features
1. **API Changes**: Update `js/api.js` for new endpoints
2. **UI Components**: Modify `js/ui.js` for interface changes
3. **Application Logic**: Update `js/main.js` for new functionality
4. **Styling**: Edit `css/styles.css` for visual changes

### Debugging
- Open browser Developer Tools (F12)
- Check Console tab for JavaScript errors
- Use Network tab to monitor API requests
- Inspect Elements for styling issues

## Customization

### Styling
- Colors: Modify the CSS custom properties in `styles.css`
- Layout: Adjust the CSS Grid layout in the `.container` class
- Animations: Update CSS transitions and keyframes

### Functionality
- Add new result display formats in `ui.js`
- Extend keyword extraction logic
- Add new metrics calculations
- Implement additional export formats

## Troubleshooting

### Common Issues

1. **"Unable to connect to API server"**
   - Ensure FastAPI backend is running
   - Check the API_BASE_URL configuration
   - Verify CORS settings in the backend

2. **Blank page or no content**
   - Check browser console for JavaScript errors
   - Ensure all script files are loading correctly
   - Verify file paths are correct

3. **Styling issues**
   - Check if CSS file is loading
   - Verify font imports from Google Fonts
   - Check for CSS syntax errors

### Support
- Check the browser console for error messages
- Ensure all dependencies are properly loaded
- Verify the backend API is responding correctly

## License

This frontend is part of the SEO Agent project and follows the same licensing terms.
