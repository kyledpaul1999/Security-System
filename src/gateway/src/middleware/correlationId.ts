import { Request, Response, NextFunction } from 'express';
import { v4 as uuidv4 } from 'uuid';

export const correlationIdMiddleware = (req: Request, res: Response, next: NextFunction) => {
  const existing = req.headers['x-correlation-id'];
  const correlationId: string = Array.isArray(existing)
    ? existing[0]
    : (existing || uuidv4());
  req.headers['x-correlation-id'] = correlationId;
  res.setHeader('X-Correlation-ID', correlationId);
  next();
};
