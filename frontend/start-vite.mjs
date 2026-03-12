// ESM-compatible Vite launcher for Node.js v24+
import { createServer } from 'vite';

const server = await createServer({
  server: { host: true, port: 5173 },
});
await server.listen();
server.printUrls();
