import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
<<<<<<< HEAD

=======
>>>>>>> 7a6687395d2c2a1d0ed0b85b4b982df424f16dc7

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "127.0.0.1",
    port: 8080,
  },
  plugins: [
    react(),
<<<<<<< HEAD

=======
>>>>>>> 7a6687395d2c2a1d0ed0b85b4b982df424f16dc7
  ].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));
