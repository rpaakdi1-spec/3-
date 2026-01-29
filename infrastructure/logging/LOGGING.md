# 🔍 Logging Infrastructure - ELK Stack

## Overview

This logging infrastructure uses the ELK Stack (Elasticsearch, Logstash, Kibana) with Beats (Filebeat, Metricbeat) for centralized log collection, processing, storage, and visualization.

## Architecture

```
Applications → Logstash → Elasticsearch → Kibana
Docker Logs → Filebeat → Logstash → Elasticsearch → Kibana
System Metrics → Metricbeat → Elasticsearch → Kibana
```

## Components

### 1. Elasticsearch (Port 9200, 9300)
- **Purpose**: Log storage and search engine
- **Version**: 8.11.0
- **Features**:
  - Full-text search
  - Index lifecycle management (ILM)
  - Security with authentication
  - Cluster health monitoring

### 2. Logstash (Port 5000, 5044, 9600)
- **Purpose**: Log processing and enrichment
- **Inputs**:
  - TCP port 5000 (JSON logs)
  - Beats port 5044 (Filebeat)
  - HTTP port 8080 (HTTP logs)
- **Features**:
  - JSON parsing
  - GeoIP enrichment
  - User agent parsing
  - Log level tagging
  - Slow query detection
  - Error log filtering

### 3. Kibana (Port 5601)
- **Purpose**: Log visualization and analysis
- **Features**:
  - Interactive dashboards
  - Log search and filtering
  - Real-time monitoring
  - Alert management
  - Reporting

### 4. Filebeat
- **Purpose**: Docker container log collection
- **Features**:
  - Docker container log shipping
  - System log collection
  - Automatic Docker metadata enrichment
  - JSON log parsing

### 5. Metricbeat
- **Purpose**: System and container metrics collection
- **Features**:
  - Docker container metrics
  - System metrics (CPU, memory, disk, network)
  - PostgreSQL metrics (optional)
  - Redis metrics (optional)

## Quick Start

### 1. Environment Variables

Create `.env` file in the `infrastructure/logging/` directory:

```bash
ELASTIC_PASSWORD=your_secure_password_here
```

**⚠️ Security Note**: Change the default password before deploying to production!

### 2. Start ELK Stack

```bash
cd infrastructure/logging
docker-compose -f docker-compose.logging.yml up -d
```

### 3. Verify Services

```bash
# Check service status
docker-compose -f docker-compose.logging.yml ps

# Check Elasticsearch health
curl -u elastic:your_secure_password http://localhost:9200/_cluster/health?pretty

# Check Logstash health
curl http://localhost:9600/_node/stats?pretty

# Access Kibana
# Open browser: http://localhost:5601
# Login: elastic / your_secure_password
```

### 4. View Logs

1. **Access Kibana**: http://localhost:5601
2. **Login** with credentials: `elastic / your_secure_password`
3. **Create Index Pattern**:
   - Go to **Management** → **Stack Management** → **Index Patterns**
   - Create pattern: `uvis-logs-*`
   - Select timestamp field: `@timestamp`
4. **View Logs**:
   - Go to **Analytics** → **Discover**
   - Select index pattern: `uvis-logs-*`

## Log Indices

### Main Indices

| Index Pattern | Description | Retention |
|---------------|-------------|-----------|
| `uvis-logs-*` | All application logs | 30 days |
| `uvis-errors-*` | Error logs (ERROR, FATAL, CRITICAL) | 90 days |
| `uvis-slow-queries-*` | Slow queries (> 1000ms) | 30 days |
| `metricbeat-docker-*` | Docker container metrics | 14 days |
| `metricbeat-system-*` | System metrics | 14 days |
| `filebeat-*` | Container logs from Filebeat | 30 days |

## Application Integration

### Backend (Python/FastAPI)

Add structured logging to your backend application:

```python
import logging
import json
from pythonjsonlogger import jsonlogger

# Configure JSON logger
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    '%(asctime)s %(name)s %(levelname)s %(message)s'
)
logHandler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# Example usage
logger.info("User login", extra={
    "user_id": 123,
    "username": "john_doe",
    "client_ip": "192.168.1.100",
    "user_agent": "Mozilla/5.0..."
})

logger.error("Database connection failed", extra={
    "error": str(exception),
    "database": "postgresql",
    "host": "db.example.com"
})
```

### Frontend (JavaScript/TypeScript)

Send logs to Logstash HTTP input:

```typescript
class Logger {
  private logstashUrl = 'http://logstash-host:8080';

  async log(level: string, message: string, metadata: any = {}) {
    try {
      await fetch(this.logstashUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          timestamp: new Date().toISOString(),
          level,
          message,
          service: 'frontend',
          ...metadata
        })
      });
    } catch (error) {
      console.error('Failed to send log:', error);
    }
  }

  info(message: string, metadata?: any) {
    this.log('INFO', message, metadata);
  }

  error(message: string, metadata?: any) {
    this.log('ERROR', message, metadata);
  }
}

// Usage
const logger = new Logger();
logger.info('User clicked button', { userId: 123, buttonId: 'submit' });
logger.error('API request failed', { endpoint: '/api/users', status: 500 });
```

## Kibana Dashboards

### Pre-configured Dashboards

1. **Application Overview**
   - Log volume over time
   - Error rate
   - Log level distribution
   - Top error messages

2. **Performance Monitoring**
   - Slow queries
   - Response times
   - Database query distribution
   - API endpoint performance

3. **System Metrics**
   - CPU usage
   - Memory usage
   - Disk I/O
   - Network traffic

4. **Docker Containers**
   - Container status
   - Container resource usage
   - Container logs
   - Container events

### Creating Custom Dashboards

1. Go to **Analytics** → **Dashboard**
2. Click **Create dashboard**
3. Add visualizations:
   - **Lens**: Drag-and-drop visualization builder
   - **TSVB**: Time series visualization
   - **Vega**: Advanced custom visualizations

## Alerting

### Configure Alerts in Kibana

1. Go to **Stack Management** → **Rules and Connectors**
2. Create alert rule:
   - **Trigger**: When error count > threshold
   - **Action**: Send email, Slack, webhook
   - **Frequency**: Check every 5 minutes

### Example Alert Rules

- **High Error Rate**: > 10 errors per minute
- **Slow Queries**: > 5 queries > 5 seconds in 10 minutes
- **Disk Usage**: > 80% disk usage
- **Memory Usage**: > 90% memory usage

## Retention and Storage

### Index Lifecycle Management (ILM)

Automatic index lifecycle management is configured:

1. **Hot Phase** (0-7 days):
   - Full indexing and search
   - Real-time analysis
   - Maximum performance

2. **Warm Phase** (7-30 days):
   - Read-only
   - Reduced replica count
   - Searchable

3. **Cold Phase** (30-90 days):
   - Compressed storage
   - Searchable archive
   - Reduced cost

4. **Delete Phase** (> 90 days):
   - Automatic deletion
   - Compliance with retention policies

### Storage Estimates

| Component | Daily Volume | 30-Day Total | Notes |
|-----------|--------------|--------------|-------|
| Application Logs | 5 GB | 150 GB | Compressed |
| Error Logs | 500 MB | 15 GB | Compressed |
| Metrics | 2 GB | 60 GB | Compressed |
| Total | ~7.5 GB | ~225 GB | With compression |

## Monitoring ELK Stack

### Health Checks

```bash
# Elasticsearch cluster health
curl -u elastic:password http://localhost:9200/_cluster/health?pretty

# Elasticsearch indices
curl -u elastic:password http://localhost:9200/_cat/indices?v

# Logstash node stats
curl http://localhost:9600/_node/stats?pretty

# Kibana status
curl http://localhost:5601/api/status
```

### Kibana Monitoring

1. Go to **Stack Management** → **Stack Monitoring**
2. View:
   - Elasticsearch cluster status
   - Index statistics
   - Node performance
   - Logstash pipeline performance

## Troubleshooting

### Common Issues

#### 1. Elasticsearch not starting

```bash
# Check logs
docker logs elasticsearch

# Check memory settings
# Increase heap size in docker-compose.logging.yml:
# ES_JAVA_OPTS: "-Xms1g -Xmx1g"

# Check disk space
df -h
```

#### 2. Logstash pipeline errors

```bash
# Check Logstash logs
docker logs logstash

# Verify pipeline configuration
docker exec logstash /usr/share/logstash/bin/logstash -t -f /usr/share/logstash/pipeline/logstash.conf

# Check Elasticsearch connection
docker exec logstash curl -u elastic:password http://elasticsearch:9200
```

#### 3. Kibana connection errors

```bash
# Check Kibana logs
docker logs kibana

# Verify Elasticsearch is running
docker exec kibana curl -u elastic:password http://elasticsearch:9200/_cluster/health

# Check kibana.yml configuration
docker exec kibana cat /usr/share/kibana/config/kibana.yml
```

#### 4. No logs appearing

```bash
# Check Filebeat is running
docker logs filebeat

# Verify Logstash is receiving logs
curl http://localhost:9600/_node/stats?pretty | jq '.pipelines.main.events.in'

# Check Elasticsearch indices
curl -u elastic:password http://localhost:9200/_cat/indices?v | grep uvis
```

## Security Best Practices

### 1. Change Default Passwords

```bash
# Generate secure password
openssl rand -base64 32

# Update ELASTIC_PASSWORD in .env file
echo "ELASTIC_PASSWORD=$(openssl rand -base64 32)" >> .env
```

### 2. Enable SSL/TLS

Update `elasticsearch.yml`:

```yaml
xpack.security.http.ssl.enabled: true
xpack.security.http.ssl.certificate: /path/to/cert.crt
xpack.security.http.ssl.key: /path/to/cert.key
```

### 3. Configure Firewall Rules

```bash
# Allow only specific IPs to access Kibana
sudo ufw allow from 10.0.0.0/8 to any port 5601

# Block external access to Elasticsearch
sudo ufw deny 9200
```

### 4. Regular Updates

```bash
# Update ELK Stack to latest version
docker-compose -f docker-compose.logging.yml pull
docker-compose -f docker-compose.logging.yml up -d
```

## Performance Tuning

### Elasticsearch

```yaml
# elasticsearch.yml
indices.memory.index_buffer_size: 30%
thread_pool.write.queue_size: 1000
```

### Logstash

```yaml
# logstash.yml
pipeline.workers: 4
pipeline.batch.size: 250
pipeline.batch.delay: 50
```

### Filebeat

```yaml
# filebeat.yml
queue.mem.events: 4096
queue.mem.flush.min_events: 2048
output.logstash.bulk_max_size: 2048
```

## Backup and Recovery

### Elasticsearch Snapshots

```bash
# Create snapshot repository
curl -X PUT "localhost:9200/_snapshot/backup_repo?pretty" -H 'Content-Type: application/json' -d'
{
  "type": "fs",
  "settings": {
    "location": "/backup/elasticsearch"
  }
}
'

# Create snapshot
curl -X PUT "localhost:9200/_snapshot/backup_repo/snapshot_1?wait_for_completion=true&pretty"

# Restore snapshot
curl -X POST "localhost:9200/_snapshot/backup_repo/snapshot_1/_restore?pretty"
```

## Cost Optimization

### Storage Optimization

1. **Enable compression**: Reduces storage by 50-70%
2. **Use ILM policies**: Automatic data lifecycle management
3. **Optimize index settings**: Reduce replica count for older data
4. **Archive old logs**: Move to S3 Glacier for long-term storage

### Resource Optimization

1. **Right-size heap**: 50% of available RAM, max 32GB
2. **Use SSDs**: 10x faster than HDDs for Elasticsearch
3. **Optimize shard count**: 1 shard per 50GB of data
4. **Monitor and scale**: Add nodes based on load

## Integration with Monitoring

The ELK Stack integrates with Prometheus and Grafana:

- **Elasticsearch Exporter**: Exposes Elasticsearch metrics to Prometheus
- **Grafana Dashboards**: Visualize Elasticsearch metrics
- **Alerting**: Combined alerting across logs and metrics

## Production Checklist

- [ ] Change default Elasticsearch password
- [ ] Enable SSL/TLS for Elasticsearch
- [ ] Configure firewall rules
- [ ] Set up index lifecycle management (ILM)
- [ ] Configure backup snapshots
- [ ] Set up alerting rules
- [ ] Create Kibana dashboards
- [ ] Configure log retention policies
- [ ] Test log ingestion from all services
- [ ] Document access procedures
- [ ] Set up monitoring for ELK Stack itself

## Support and Resources

- **Elasticsearch Documentation**: https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html
- **Logstash Documentation**: https://www.elastic.co/guide/en/logstash/current/index.html
- **Kibana Documentation**: https://www.elastic.co/guide/en/kibana/current/index.html
- **Beats Documentation**: https://www.elastic.co/guide/en/beats/libbeat/current/index.html

---

**Last Updated**: 2026-01-28  
**Version**: 1.0.0  
**Author**: GenSpark AI Developer
