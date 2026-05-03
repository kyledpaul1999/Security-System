import express, { Express, Request, Response } from 'express';
import { createProxyMiddleware } from 'http-proxy-middleware';

const app: Express = express();
const port: number = 3000;

// Get the target API service URL from an environment variable
const apiServiceUrl = process.env.API_SERVICE_URL || 'http://localhost:8000';

// Proxy middleware options
const apiProxy = createProxyMiddleware({
  target: apiServiceUrl,
  changeOrigin: true, // Needed for virtual-hosted sites
  pathRewrite: { '^/api': '' }, // Rewrite paths: /api/users -> /users
});

// Use the proxy middleware for all /api requests
app.use('/api', apiProxy);

app.get('/', (req: Request, res: Response) => {
  res.send('API Gateway is running!');
});

app.listen(port, () => {
  console.log(`API Gateway listening at http://localhost:${port}`);
  console.log(`Proxying /api requests to ${apiServiceUrl}`);
});
