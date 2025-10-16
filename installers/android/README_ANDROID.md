# 📱 Jatan Salary System - Android Monitoring App

**Remote monitoring and management app for the Jatan Salary Management System**

---

## Overview

The Android app provides remote monitoring and control of your Jatan Salary System. It connects to your backend API to display real-time metrics, manage tasks, and view reports.

**Note**: This app doesn't run the full Docker stack on Android. Instead, it connects to your server running the stack.

---

## Features

### Dashboard
- ✅ Real-time service status
- ✅ Database connection count
- ✅ Redis cache hit ratio
- ✅ RabbitMQ queue depths
- ✅ Celery worker status
- ✅ Task success/failure rates

### Monitoring
- ✅ View Grafana dashboards
- ✅ Check Prometheus metrics
- ✅ Monitor Celery tasks
- ✅ View RabbitMQ queues

### Management
- ✅ Trigger CRM sync
- ✅ Create database backups
- ✅ Scale Celery workers
- ✅ View application logs

### Alerts
- ✅ Push notifications for critical alerts
- ✅ Database connection warnings
- ✅ Queue depth notifications
- ✅ Task failure alerts

---

## Build Instructions

### Prerequisites
- Flutter SDK 3.0+
- Android Studio
- Android SDK (API 21+)

### Project Setup

```bash
# Create Flutter project
flutter create jatan_monitor
cd jatan_monitor

# Add dependencies
flutter pub add http
flutter pub add provider
flutter pub add fl_chart
flutter pub add flutter_secure_storage
flutter pub add firebase_messaging
flutter pub add webview_flutter
```

### Project Structure

```
jatan_monitor/
├── lib/
│   ├── main.dart
│   ├── models/
│   │   ├── metrics.dart
│   │   ├── service_status.dart
│   │   └── alert.dart
│   ├── services/
│   │   ├── api_service.dart
│   │   ├── auth_service.dart
│   │   └── notification_service.dart
│   ├── screens/
│   │   ├── dashboard_screen.dart
│   │   ├── monitoring_screen.dart
│   │   ├── tasks_screen.dart
│   │   └── settings_screen.dart
│   └── widgets/
│       ├── metric_card.dart
│       ├── status_indicator.dart
│       └── chart_widget.dart
├── android/
│   └── app/
│       └── build.gradle
└── pubspec.yaml
```

### API Endpoints Required

The backend needs to expose these endpoints:

```
GET  /api/health                    - Overall system health
GET  /api/metrics/dashboard         - Dashboard metrics
GET  /api/services/status           - Service status
GET  /api/celery/workers            - Worker information
GET  /api/celery/tasks              - Task statistics
GET  /api/rabbitmq/queues           - Queue information
GET  /api/prometheus/query          - Prometheus queries
POST /api/celery/scale              - Scale workers
POST /api/tasks/trigger             - Trigger manual tasks
POST /api/backup/create             - Create backup
GET  /api/logs                      - Application logs
```

### Sample Code

#### main.dart
```dart
import 'package:flutter/material.dart';
import 'screens/dashboard_screen.dart';

void main() {
  runApp(JatanMonitorApp());
}

class JatanMonitorApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Jatan Salary Monitor',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      home: DashboardScreen(),
    );
  }
}
```

#### api_service.dart
```dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  final String baseUrl;
  final String apiKey;

  ApiService({required this.baseUrl, required this.apiKey});

  Map<String, String> get headers => {
    'Authorization': 'Bearer $apiKey',
    'Content-Type': 'application/json',
  };

  Future<Map<String, dynamic>> getHealth() async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/health'),
      headers: headers,
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to load health status');
    }
  }

  Future<Map<String, dynamic>> getDashboardMetrics() async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/metrics/dashboard'),
      headers: headers,
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to load metrics');
    }
  }

  Future<void> scaleWorkers(int count) async {
    await http.post(
      Uri.parse('$baseUrl/api/celery/scale'),
      headers: headers,
      body: json.encode({'worker_count': count}),
    );
  }
}
```

#### dashboard_screen.dart
```dart
import 'package:flutter/material.dart';
import '../services/api_service.dart';

class DashboardScreen extends StatefulWidget {
  @override
  _DashboardScreenState createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  final ApiService api = ApiService(
    baseUrl: 'https://your-server.com',
    apiKey: 'your-api-key',
  );

  Map<String, dynamic>? metrics;
  bool loading = true;

  @override
  void initState() {
    super.initState();
    loadMetrics();
  }

  Future<void> loadMetrics() async {
    setState(() => loading = true);
    try {
      final data = await api.getDashboardMetrics();
      setState(() {
        metrics = data;
        loading = false;
      });
    } catch (e) {
      setState(() => loading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error loading metrics: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Jatan Salary Monitor'),
        actions: [
          IconButton(
            icon: Icon(Icons.refresh),
            onPressed: loadMetrics,
          ),
        ],
      ),
      body: loading
          ? Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: loadMetrics,
              child: ListView(
                padding: EdgeInsets.all(16),
                children: [
                  MetricCard(
                    title: 'Database Connections',
                    value: metrics?['db_connections'] ?? 0,
                    icon: Icons.storage,
                  ),
                  MetricCard(
                    title: 'Redis Hit Ratio',
                    value: '${metrics?['redis_hit_ratio'] ?? 0}%',
                    icon: Icons.speed,
                  ),
                  MetricCard(
                    title: 'Queue Depth',
                    value: metrics?['queue_depth'] ?? 0,
                    icon: Icons.queue,
                  ),
                  MetricCard(
                    title: 'Active Workers',
                    value: metrics?['celery_workers'] ?? 0,
                    icon: Icons.work,
                  ),
                ],
              ),
            ),
    );
  }
}

class MetricCard extends StatelessWidget {
  final String title;
  final dynamic value;
  final IconData icon;

  const MetricCard({
    required this.title,
    required this.value,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: EdgeInsets.only(bottom: 16),
      child: ListTile(
        leading: Icon(icon, size: 40, color: Colors.blue),
        title: Text(title),
        subtitle: Text('$value', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
      ),
    );
  }
}
```

### Build APK

```bash
cd jatan_monitor
flutter build apk --release

# Output: build/app/outputs/flutter-apk/app-release.apk
```

---

## Backend API Requirements

Create a simple REST API in your main application to expose metrics:

### Python Flask Example

```python
from flask import Flask, jsonify
import psycopg2
import redis

app = Flask(__name__)

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'version': '3.1.0',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/metrics/dashboard')
def dashboard_metrics():
    # Get PostgreSQL connections
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM pg_stat_activity")
    db_connections = cur.fetchone()[0]
    cur.close()
    conn.close()

    # Get Redis stats
    r = redis.Redis(host='redis', port=6379)
    redis_info = r.info('stats')
    hit_ratio = redis_info['keyspace_hits'] / (redis_info['keyspace_hits'] + redis_info['keyspace_misses']) * 100

    # Get RabbitMQ queue depth
    # (Use RabbitMQ API)

    # Get Celery worker count
    # (Use Celery inspect API)

    return jsonify({
        'db_connections': db_connections,
        'redis_hit_ratio': round(hit_ratio, 2),
        'queue_depth': 42,  # From RabbitMQ
        'celery_workers': 5  # From Celery
    })

@app.route('/api/celery/scale', methods=['POST'])
def scale_workers():
    count = request.json['worker_count']
    # Scale using Docker API or Kubernetes
    return jsonify({'status': 'scaled', 'workers': count})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
```

---

## Distribution

### App Stores

#### Google Play Store
1. Create developer account
2. Generate signed APK
3. Upload to Play Console
4. Set up screenshots and description
5. Publish

#### Internal Distribution
1. Sign APK with your keystore
2. Host on company website
3. Enable "Install from Unknown Sources"

---

## Security

### API Authentication
- Use Bearer tokens
- Implement JWT
- Rate limiting
- IP whitelisting

### App Security
- Store credentials in secure storage
- Enable certificate pinning
- Obfuscate code
- Use ProGuard

---

## Conclusion

The Android app provides convenient mobile monitoring of your enterprise stack. It's lightweight, fast, and provides real-time insights from anywhere.

**Note**: For full application features, use the web interface or desktop applications.

---

**Version**: 1.0.0
**Platform**: Android 5.0+ (API 21+)
**Size**: ~15MB
**Status**: Development Ready


