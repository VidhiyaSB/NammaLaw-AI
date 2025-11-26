# TamilGuardian Deployment Guide

## Hugging Face Spaces Deployment

### Prerequisites
1. Hugging Face account
2. API keys for required services
3. Git LFS installed

### Step 1: Prepare Repository
```bash
git clone <your-repo>
cd tamilguardian
git lfs track "*.bin" "*.pkl" "*.model"
```

### Step 2: Configure Environment Variables
In Hugging Face Spaces settings, add:
- `OPENAI_API_KEY`: Your OpenAI API key
- `NEBIUS_API_KEY`: Your Nebius API key (optional)
- `ELEVENLABS_API_KEY`: Your ElevenLabs API key (optional)
- `SECRET_KEY`: Random secret key for security

### Step 3: Create Space
1. Go to Hugging Face Spaces
2. Create new Space with Gradio SDK
3. Upload your code or connect Git repository
4. Set hardware to CPU Basic (or GPU if needed)

### Step 4: Deploy
The space will automatically build and deploy when you push code.

## Local Development

### Setup
```bash
# Clone repository
git clone <repo-url>
cd tamilguardian

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your API keys

# Run application
python app.py
```

### Testing
```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=src tests/
```

## Production Deployment

### Docker Deployment
```bash
# Build image
docker build -t tamilguardian .

# Run container
docker run -p 7860:7860 --env-file .env tamilguardian
```

### Kubernetes Deployment
See `k8s/` directory for Kubernetes manifests.

## Monitoring and Logging

### Health Checks
- Application health: `GET /health`
- MCP servers health: Available in admin interface

### Logs
- Application logs: `logs/tamilguardian.log`
- Access logs: Gradio built-in logging
- Error tracking: Configure Sentry (optional)

## Security Considerations

1. **API Keys**: Store securely in environment variables
2. **OAuth**: Use secure OAuth flow for Google services
3. **PII Protection**: Enable PII redaction in TTS
4. **Rate Limiting**: Implement rate limiting for production
5. **HTTPS**: Always use HTTPS in production

## Scaling

### Horizontal Scaling
- Deploy MCP servers as separate microservices
- Use load balancer for multiple app instances
- Implement Redis for session management

### Performance Optimization
- Cache embeddings and search results
- Use CDN for static assets
- Optimize model loading and inference

## Troubleshooting

### Common Issues
1. **Import Errors**: Check Python path and dependencies
2. **API Failures**: Verify API keys and network connectivity
3. **Memory Issues**: Increase container memory limits
4. **Slow Performance**: Check model loading and caching

### Debug Mode
Set `DEBUG=True` in environment for detailed logging.