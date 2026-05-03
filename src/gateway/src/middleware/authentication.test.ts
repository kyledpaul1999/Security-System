
import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { authenticateToken } from './authentication';

const JWT_SECRET = process.env.JWT_SECRET || 'your-default-secret';

describe('authenticateToken middleware', () => {
  let mockRequest: Partial<Request>;
  let mockResponse: Partial<Response>;
  let nextFunction: NextFunction = jest.fn();

  beforeEach(() => {
    mockRequest = {};
    mockResponse = {
      sendStatus: jest.fn(),
    };
  });

  it('should return 401 if no token is provided', () => {
    mockRequest.headers = {};
    authenticateToken(mockRequest as Request, mockResponse as Response, nextFunction);
    expect(mockResponse.sendStatus).toHaveBeenCalledWith(401);
  });

  it('should return 403 if token is invalid', () => {
    mockRequest.headers = { authorization: 'Bearer invalidtoken' };
    authenticateToken(mockRequest as Request, mockResponse as Response, nextFunction);
    expect(mockResponse.sendStatus).toHaveBeenCalledWith(403);
  });

  it('should call next() if token is valid', () => {
    const user = { id: '1', role: 'admin' };
    const token = jwt.sign(user, JWT_SECRET);
    mockRequest.headers = { authorization: `Bearer ${token}` };
    authenticateToken(mockRequest as Request, mockResponse as Response, nextFunction);
    expect(nextFunction).toHaveBeenCalled();
    expect(mockRequest.user).toMatchObject(user);
  });
});
