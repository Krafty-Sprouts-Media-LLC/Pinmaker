# Pinterest Template Generator - Frontend

A React TypeScript application for generating Pinterest templates using AI image analysis.

## Features

- 🖼️ Drag & drop image upload
- 🤖 AI-powered image analysis
- 🎨 Template generation with customizable styles
- 🎯 Real-time preview
- 📱 Responsive design
- 💾 Export functionality (PNG/JPG)

## Tech Stack

- React 19 with TypeScript
- Axios for API calls
- React Dropzone for file uploads
- Fabric.js for canvas manipulation
- HTML2Canvas for export functionality

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.\
You will also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can’t go back!**

If you aren’t satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you’re on your own.

You don’t have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn’t feel obligated to use this feature. However we understand that this tool wouldn’t be useful if you couldn’t customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).

## Environment Variables

Create `.env` files for different environments:

### Development (.env)
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_PREFIX=/api/v1
```

### Production (.env.production)
```
REACT_APP_API_URL=https://pinmaker.kraftysprouts.com
REACT_APP_API_PREFIX=/api/v1
```

## Deployment to Netlify

### Option 1: Drag & Drop
1. Run `npm run build`
2. Drag the `build` folder to Netlify dashboard

### Option 2: Git Integration
1. Push code to GitHub repository
2. Connect repository to Netlify
3. Set build command: `npm run build`
4. Set publish directory: `build`
5. Add environment variables in Netlify dashboard:
   - `REACT_APP_API_URL=https://pinmaker.kraftysprouts.com`
   - `REACT_APP_API_PREFIX=/api/v1`

### Option 3: Netlify CLI
```bash
npm install -g netlify-cli
netlify login
netlify deploy --prod --dir=build
```

## API Integration

The frontend connects to a FastAPI backend with the following endpoints:

- `POST /api/v1/analyze` - Image analysis
- `POST /api/v1/generate-template` - Template generation
- `POST /api/v1/generate-preview` - Preview generation
- `POST /api/v1/export` - Export functionality
- `GET /uploads/{filename}` - Uploaded files
- `GET /templates/{filename}` - Template files
- `GET /previews/{filename}` - Preview images

## Project Structure

```
src/
├── components/
│   ├── ImageUploader.tsx
│   ├── TemplateEditor.tsx
│   └── TemplateExporter.tsx
├── config/
│   └── api.ts
├── App.tsx
└── index.tsx
```

## Backend Repository

The backend is hosted separately at: `https://pinmaker.kraftysprouts.com`
