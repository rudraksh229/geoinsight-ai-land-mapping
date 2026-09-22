import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'GeoInsight AI',
        short_name: 'GeoInsight AI',
        description: 'AI-based land mapping and analysis system',
        theme_color: '#0f172a',
        background_color: '#ffffff',
        display: 'standalone',
        start_url: '/',
        icons: [
          {
            src: '/WhatsApp Image 2026-09-22 at 12.42.01 PM.jpeg',
            sizes: '512x512',
            type: 'image/png'
          }
        ]
      }
    })
  ]
})