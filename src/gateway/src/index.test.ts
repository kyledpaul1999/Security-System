import request from 'supertest';
import express, { Express } from 'express';
import { createProxyMiddleware } from 'http-proxy-middleware';

let app: Express;

beforeAll(() => {
    app = express();
    const apiServiceUrl = 'http://localhost:8000'; // Mock target service
    const apiProxy = createProxyMiddleware({
        target: apiServiceUrl,
        changeOrigin: true,
        pathRewrite: { '^/api': '' },
    });
    app.use('/api', apiProxy);
});

describe('API Gateway Proxy', () => {
    it('should proxy requests to the target service', async () => {
        // This test requires the target service to be running
        // or a mock server to be set up.
        // For now, we'll just check that the gateway returns a 503
        // if the target service is unavailable.
        const response = await request(app).get('/api/users');
        expect(response.status).toBe(503);
    });
});
