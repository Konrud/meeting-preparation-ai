import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

// https://vite.dev/config/
// eslint-disable-next-line @typescript-eslint/no-unused-vars
export default defineConfig(({ command, mode }) => {
  const env = loadEnv(mode, path.resolve(__dirname, "../env"), "");

  return {
    plugins: [react()],
    // Make environment variables available to the client
    define: {
      __APP_ENV__: JSON.stringify(env),
    },
    // Alternative approach using envDir (this tells Vite where to look for .env files)
    envDir: path.resolve(__dirname, "../env"),
  };
});
