import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react({
      // Enable React Fast Refresh
      fastRefresh: true,
      // Include .jsx files
      include: "**/*.{jsx,tsx}",
    }),
  ],
  
  // Path resolution
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
      '@components': resolve(__dirname, './src/components'),
      '@services': resolve(__dirname, './src/services'),
      '@types': resolve(__dirname, './src/types'),
      '@utils': resolve(__dirname, './src/utils'),
      '@assets': resolve(__dirname, './src/assets'),
    },
  },
  
  // Development server configuration
  server: {
    port: 3000,
    host: true, // Allow external connections
    strictPort: true,
    open: false, // Don't auto-open browser
    cors: true,
    proxy: {
      // Proxy API requests to FastAPI backend
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        ws: true, // Enable WebSocket proxying
      },
      // Proxy static file requests
      '/uploads': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      '/templates': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      '/previews': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
  
  // Build configuration
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false, // Disable source maps in production
    minify: 'terser',
    target: 'es2020',
    rollupOptions: {
      output: {
        // Manual chunk splitting for better caching
        manualChunks: {
          // Vendor chunks
          'react-vendor': ['react', 'react-dom'],
          'ui-vendor': ['react-colorful', 'react-dropzone'],
          'utils-vendor': ['axios', 'clsx'],
        },
        // Asset file naming
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name?.split('.') || []
          let extType = info[info.length - 1]
          
          if (/png|jpe?g|svg|gif|tiff|bmp|ico/i.test(extType)) {
            extType = 'images'
          } else if (/woff2?|eot|ttf|otf/i.test(extType)) {
            extType = 'fonts'
          } else if (/css/i.test(extType)) {
            extType = 'css'
          }
          
          return `assets/${extType}/[name]-[hash][extname]`
        },
        // Chunk file naming
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
      },
    },
    // Terser options for better minification
    terserOptions: {
      compress: {
        drop_console: true, // Remove console.log in production
        drop_debugger: true,
      },
    },
    // Chunk size warning limit
    chunkSizeWarningLimit: 1000,
  },
  
  // Preview configuration (for production build preview)
  preview: {
    port: 3000,
    host: true,
    strictPort: true,
    open: false,
  },
  
  // CSS configuration
  css: {
    devSourcemap: true,
    preprocessorOptions: {
      scss: {
        additionalData: `@import "@/styles/variables.scss";`,
      },
    },
    postcss: {
      plugins: [
        // PostCSS plugins are configured in postcss.config.js
      ],
    },
  },
  
  // Environment variables
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
    __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
  },
  
  // Optimization
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-colorful',
      'react-dropzone',
      'axios',
      'clsx',
    ],
    exclude: [
      // Exclude any problematic dependencies
    ],
  },
  
  // ESBuild configuration
  esbuild: {
    // Remove console and debugger in production
    drop: process.env.NODE_ENV === 'production' ? ['console', 'debugger'] : [],
    // JSX configuration
    jsxFactory: 'React.createElement',
    jsxFragment: 'React.Fragment',
  },
  
  // Worker configuration
  worker: {
    format: 'es',
  },
  
  // JSON configuration
  json: {
    namedExports: true,
    stringify: false,
  },
})