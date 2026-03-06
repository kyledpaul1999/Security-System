# Security System Architecture

## Overview
This document outlines the architecture for a locally-hosted security system designed to replace ADT Pulse. The system integrates with Hikvision NVR (DS-7604NI-Q1/4P) and provides web-based monitoring, recording, and AI-powered person detection capabilities.

## System Architecture

### Microservices Design
The system follows a microservices architecture for scalability and maintainability:

```
┌─────────────────────────────────────────────────────────────────┐
│                        Load Balancer / API Gateway          │
└─────────────────────┬─────────────────────────────────────────┘
                    │
┌───────────────────┼───────────────────┬─────────────────────┐
│                   │                   │                     │
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│   Web App   │ │Auth Service │ │Camera Service│ │  AI Service │
│  (React)    │ │   (Node.js)  │ │  (Node.js)  │ │ (Python)    │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│Video Stream │ │Recording Mgt│ │Notification │ │   VPN       │
│  Service    │ │  Service     │ │   Service   │ │  Service    │
│ (Node.js/   │ │  (Node.js)   │ │  (Node.js)  │ │ (OpenVPN)   │
│  FFmpeg)    │ │              │ │             │ │             │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
                    │
┌───────────────────┼───────────────────┬─────────────────────┐
│                   │                   │                     │
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ PostgreSQL  │ │   Redis     │ │ MinIO/S3    │ │  Message    │
│  Database   │ │   Cache     │ │  Storage    │ │   Queue     │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
```

## Core Components

### 1. Web Application (React + TypeScript)
- **Purpose**: User interface for camera monitoring and system management
- **Features**:
  - Live camera streaming
  - Historical video playback
  - User management and permissions
  - Camera controls and configuration
  - Video export and clip management
  - AI detection alerts and logs

### 2. Authentication Service (Node.js + Express)
- **Purpose**: User authentication and authorization
- **Features**:
  - JWT-based authentication
  - Role-based access control (RBAC)
  - User session management
  - API key management for external access

### 3. Camera Integration Service (Node.js)
- **Purpose**: Hikvision NVR integration and camera control
- **Features**:
  - ONVIF protocol support
  - RTSP stream management
  - Camera configuration and PTZ control
  - Motion detection integration
  - Camera health monitoring

### 4. Video Streaming Service (Node.js + FFmpeg)
- **Purpose**: Live video streaming and transcoding
- **Features**:
  - RTSP to HLS conversion
  - Multi-resolution streaming
  - Bandwidth optimization
  - Stream authentication and security

### 5. Recording Management Service (Node.js)
- **Purpose**: Video recording and storage management
- **Features**:
  - Scheduled and motion-triggered recording
  - Video file segmentation and indexing
  - Storage lifecycle management
  - Video metadata extraction
  - Clip creation and export

### 6. AI Person Detection Service (Python)
- **Purpose**: AI-powered person detection and analysis
- **Features**:
  - Real-time person detection on video streams
  - Detection event logging
  - Confidence scoring
  - Integration with notification service
  - Configurable detection zones

### 7. Notification Service (Node.js)
- **Purpose**: Alert and notification management
- **Features**:
  - Email notifications
  - Push notifications (mobile app integration)
  - Webhook support
  - Alert scheduling and filtering

### 8. VPN Service (OpenVPN)
- **Purpose**: Secure remote access
- **Features**:
  - VPN server configuration
  - Client certificate management
  - Access logging
  - Bandwidth management

## Technology Stack

### Frontend
- **Framework**: React 18 with TypeScript
- **State Management**: Zustand
- **UI Library**: Tailwind CSS + Headless UI
- **Video Player**: Video.js
- **Charts**: Recharts for analytics
- **Icons**: Lucide React

### Backend Services
- **Runtime**: Node.js 20 LTS
- **Framework**: Express.js with TypeScript
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Message Queue**: Redis Pub/Sub or RabbitMQ
- **Storage**: MinIO (S3-compatible) or local storage
- **Video Processing**: FFmpeg

### AI/ML
- **Framework**: TensorFlow.js or PyTorch
- **Pre-trained Models**: YOLOv8 for person detection
- **Video Analysis**: OpenCV

### Infrastructure
- **Container**: Docker + Docker Compose
- **Reverse Proxy**: Nginx
- **VPN**: OpenVPN
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)

## Database Schema

### Core Tables
- **users**: User accounts and authentication
- **roles**: User roles and permissions
- **cameras**: Camera configuration and metadata
- **recordings**: Video recording metadata
- **detections**: AI detection events
- **clips**: Exported video clips
- **notifications**: Alert and notification logs
- **system_logs**: System activity logs

## Security Considerations

### Network Security
- VPN-only access for remote connections
- TLS/SSL encryption for all services
- API rate limiting and DDoS protection
- Network segmentation for services

### Application Security
- JWT token-based authentication
- Role-based access control
- Input validation and sanitization
- SQL injection prevention
- XSS and CSRF protection

### Data Security
- Encrypted video storage
- Secure key management
- Audit logging
- Data retention policies
- Backup and recovery procedures

## Scalability Design

### Horizontal Scaling
- Stateless microservices
- Load balancing with Nginx
- Database read replicas
- Redis clustering
- Object storage scaling

### Performance Optimization
- CDN for static assets
- Video streaming optimization
- Database indexing
- Caching strategies
- Asynchronous processing

## Deployment Architecture

### Development Environment
- Docker Compose for local development
- Hot reload for development services
- Local PostgreSQL and Redis
- MinIO for object storage

### Production Environment
- Docker Swarm or Kubernetes
- High availability setup
- Automated backups
- Monitoring and alerting
- Log aggregation

## Integration Points

### Hikvision NVR Integration
- ONVIF protocol for camera discovery
- RTSP streams for video feeds
- ISAPI for camera control
- Motion detection events

### External Services
- Email service (SMTP)
- Push notification service
- Cloud backup (optional)
- Mobile app API

## Monitoring and Maintenance

### Health Checks
- Service health endpoints
- Database connectivity
- Storage availability
- Camera connectivity
- AI service status

### Logging
- Structured logging with JSON
- Centralized log aggregation
- Log rotation and retention
- Security event logging

### Backup Strategy
- Database backups
- Video file backups
- Configuration backups
- Disaster recovery procedures

## Future Enhancements

### Advanced Features
- Facial recognition
- License plate detection
- Behavior analysis
- Integration with smart home systems
- Mobile applications
- Cloud backup integration
- Advanced analytics dashboard

### Performance Improvements
- GPU acceleration for AI processing
- Edge computing for real-time processing
- Advanced video compression
- Predictive storage management