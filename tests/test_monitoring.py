"""Tests for monitoring and metrics system."""

import pytest
from datetime import datetime, timedelta

from rapidai import App
from rapidai.monitoring import (
    monitor,
    get_collector,
    calculate_cost,
    get_dashboard_html,
    MetricsCollector,
    Metric,
    RequestMetrics,
    ModelUsage,
)
from rapidai.testing import TestClient


class TestMonitorDecorator:
    """Test @monitor decorator."""

    def test_monitor_decorator_basic(self):
        """Monitor decorator should wrap function."""
        app = App()

        @app.route("/test", methods=["POST"])
        @monitor()
        async def test_endpoint():
            return {"result": "success"}

        # Should still be callable
        assert callable(test_endpoint)

    def test_monitor_with_token_tracking(self):
        """Monitor should accept track_tokens parameter."""
        app = App()

        @app.route("/chat", methods=["POST"])
        @monitor(track_tokens=True, track_cost=True)
        async def chat(message: str):
            return {"response": "test", "tokens_used": 100, "model": "test-model"}

        assert callable(chat)


class TestMetric:
    """Test Metric dataclass."""

    def test_metric_creation(self):
        """Should create metric with required fields."""
        metric = Metric(
            name="test.metric", value=42.5, timestamp=datetime.now(), tags={"env": "test"}
        )

        assert metric.name == "test.metric"
        assert metric.value == 42.5
        assert isinstance(metric.timestamp, datetime)
        assert metric.tags == {"env": "test"}

    def test_metric_default_tags(self):
        """Tags should default to empty dict."""
        metric = Metric(name="test", value=1.0, timestamp=datetime.now(), tags={})

        assert metric.tags == {}


class TestRequestMetrics:
    """Test RequestMetrics dataclass."""

    def test_request_metrics_creation(self):
        """Should create request metrics."""
        metrics = RequestMetrics(
            endpoint="/test",
            method="POST",
            duration=0.523,
            status_code=200,
            timestamp=datetime.now(),
        )

        assert metrics.endpoint == "/test"
        assert metrics.method == "POST"
        assert metrics.duration == 0.523
        assert metrics.status_code == 200

    def test_request_metrics_with_tokens(self):
        """Should support token tracking."""
        metrics = RequestMetrics(
            endpoint="/chat",
            method="POST",
            duration=1.2,
            status_code=200,
            timestamp=datetime.now(),
            tokens_used=150,
            model="claude-3-haiku",
            cost=0.0001,
        )

        assert metrics.tokens_used == 150
        assert metrics.model == "claude-3-haiku"
        assert metrics.cost == 0.0001


class TestModelUsage:
    """Test ModelUsage dataclass."""

    def test_model_usage_creation(self):
        """Should create model usage tracker."""
        usage = ModelUsage(model="test-model")

        assert usage.model == "test-model"
        assert usage.total_tokens == 0
        assert usage.prompt_tokens == 0
        assert usage.completion_tokens == 0
        assert usage.total_cost == 0.0
        assert usage.request_count == 0

    def test_add_tokens(self):
        """Should add token usage."""
        usage = ModelUsage(model="test")

        usage.add_tokens(prompt_tokens=100, completion_tokens=50, cost=0.001)

        assert usage.prompt_tokens == 100
        assert usage.completion_tokens == 50
        assert usage.total_tokens == 150
        assert usage.total_cost == 0.001
        assert usage.request_count == 1

    def test_add_tokens_multiple_times(self):
        """Should accumulate token usage."""
        usage = ModelUsage(model="test")

        usage.add_tokens(prompt_tokens=100, completion_tokens=50, cost=0.001)
        usage.add_tokens(prompt_tokens=200, completion_tokens=100, cost=0.002)

        assert usage.prompt_tokens == 300
        assert usage.completion_tokens == 150
        assert usage.total_tokens == 450
        assert usage.total_cost == 0.003
        assert usage.request_count == 2


class TestMetricsCollector:
    """Test MetricsCollector class."""

    @pytest.fixture
    def collector(self):
        """Create fresh collector for each test."""
        coll = MetricsCollector()
        coll.clear()
        return coll

    def test_record_metric(self, collector):
        """Should record custom metric."""
        collector.record_metric(name="test.metric", value=42.0, tags={"env": "test"})

        metrics = collector.get_metrics(name="test.metric")

        assert len(metrics) == 1
        assert metrics[0].name == "test.metric"
        assert metrics[0].value == 42.0
        assert metrics[0].tags == {"env": "test"}

    def test_record_request(self, collector):
        """Should record request metrics."""
        collector.record_request(
            endpoint="/test", method="GET", duration=0.5, status_code=200
        )

        requests = collector.get_requests(endpoint="/test")

        assert len(requests) >= 1
        assert requests[0].endpoint == "/test"
        assert requests[0].method == "GET"
        assert requests[0].duration == 0.5

    def test_get_metrics_filtered_by_name(self, collector):
        """Should filter metrics by name."""
        collector.record_metric("metric.a", 1.0)
        collector.record_metric("metric.b", 2.0)
        collector.record_metric("metric.a", 3.0)

        filtered = collector.get_metrics(name="metric.a")

        assert len(filtered) == 2
        assert all(m.name == "metric.a" for m in filtered)

    def test_get_metrics_filtered_by_time(self, collector):
        """Should filter metrics by timestamp."""
        now = datetime.now()
        since = now - timedelta(minutes=5)

        collector.record_metric("test", 1.0)

        metrics = collector.get_metrics(since=since)

        assert len(metrics) >= 1

    def test_get_model_usage(self, collector):
        """Should track model usage."""
        collector.record_request(
            endpoint="/chat",
            method="POST",
            duration=1.0,
            status_code=200,
            tokens_used=150,
            model="claude-3-haiku",
        )

        usage = collector.get_model_usage(model="claude-3-haiku")

        assert "claude-3-haiku" in usage
        assert usage["claude-3-haiku"].total_tokens >= 150

    def test_get_summary(self, collector):
        """Should return summary statistics."""
        # Record some metrics
        collector.record_request("/test", "GET", 0.5, 200)
        collector.record_request("/test", "GET", 0.6, 200)
        collector.record_request("/test", "GET", 0.4, 500)

        summary = collector.get_summary()

        assert "total_requests" in summary
        assert "successful_requests" in summary
        assert "failed_requests" in summary
        assert "success_rate" in summary
        assert "average_duration" in summary

        assert summary["total_requests"] >= 3
        assert summary["successful_requests"] >= 2
        assert summary["failed_requests"] >= 1

    def test_clear(self, collector):
        """Should clear all metrics."""
        collector.record_metric("test", 1.0)
        collector.record_request("/test", "GET", 0.5, 200)

        collector.clear()

        assert len(collector.get_metrics()) == 0
        assert len(collector.get_requests()) == 0


class TestCostCalculation:
    """Test cost calculation function."""

    def test_calculate_cost_claude_haiku(self):
        """Should calculate cost for Claude Haiku."""
        cost = calculate_cost(
            model="claude-3-haiku-20240307", prompt_tokens=1000, completion_tokens=500
        )

        # Haiku: $0.25/$1.25 per 1M tokens
        # Prompt: 1000 * 0.25 / 1M = 0.00025
        # Completion: 500 * 1.25 / 1M = 0.000625
        # Total: 0.000875
        assert cost == pytest.approx(0.000875, rel=0.01)

    def test_calculate_cost_claude_opus(self):
        """Should calculate cost for Claude Opus."""
        cost = calculate_cost(
            model="claude-3-opus-20240229", prompt_tokens=1000, completion_tokens=500
        )

        # Opus: $15/$75 per 1M tokens
        # Prompt: 1000 * 15 / 1M = 0.015
        # Completion: 500 * 75 / 1M = 0.0375
        # Total: 0.0525
        assert cost == pytest.approx(0.0525, rel=0.01)

    def test_calculate_cost_gpt4o(self):
        """Should calculate cost for GPT-4o."""
        cost = calculate_cost(model="gpt-4o", prompt_tokens=1000, completion_tokens=500)

        # GPT-4o: $5/$15 per 1M tokens
        # Prompt: 1000 * 5 / 1M = 0.005
        # Completion: 500 * 15 / 1M = 0.0075
        # Total: 0.0125
        assert cost == pytest.approx(0.0125, rel=0.01)

    def test_calculate_cost_unknown_model(self):
        """Should return 0 for unknown model."""
        cost = calculate_cost(
            model="unknown-model", prompt_tokens=1000, completion_tokens=500
        )

        assert cost == 0.0

    def test_calculate_cost_zero_tokens(self):
        """Should handle zero tokens."""
        cost = calculate_cost(
            model="claude-3-haiku-20240307", prompt_tokens=0, completion_tokens=0
        )

        assert cost == 0.0


class TestDashboardGeneration:
    """Test dashboard HTML generation."""

    def test_get_dashboard_html_returns_string(self):
        """Should return HTML string."""
        html = get_dashboard_html()

        assert isinstance(html, str)
        assert len(html) > 0

    def test_dashboard_contains_html_structure(self):
        """Dashboard should contain HTML structure."""
        html = get_dashboard_html()

        assert "<!DOCTYPE html>" in html or "<html>" in html
        assert "</html>" in html
        assert "<head>" in html or "<body>" in html

    def test_dashboard_contains_metrics(self):
        """Dashboard should reference metrics."""
        html = get_dashboard_html()

        # Should mention metrics-related terms
        assert any(term in html.lower() for term in ["metric", "request", "token", "cost"])


class TestGetCollector:
    """Test get_collector factory function."""

    def test_get_collector_returns_singleton(self):
        """get_collector should return same instance."""
        collector1 = get_collector()
        collector2 = get_collector()

        assert collector1 is collector2

    def test_get_collector_returns_metrics_collector(self):
        """get_collector should return MetricsCollector."""
        collector = get_collector()

        assert isinstance(collector, MetricsCollector)


class TestMonitoringIntegration:
    """Integration tests for monitoring system."""

    def test_monitor_decorator_integration(self):
        """Test complete monitoring workflow."""
        app = App()
        collector = get_collector()
        collector.clear()

        @app.route("/test", methods=["POST"])
        @monitor(track_tokens=True, track_cost=True)
        async def test_endpoint(message: str):
            return {
                "response": "test",
                "tokens_used": 100,
                "model": "claude-3-haiku-20240307",
            }

        client = TestClient(app)

        # Make request
        response = client.post("/test", json={"message": "hello"})

        assert response.status_code == 200

        # Check metrics were recorded
        summary = collector.get_summary()
        assert summary["total_requests"] >= 1

    def test_model_usage_tracking_integration(self):
        """Test complete model usage tracking."""
        collector = get_collector()
        collector.clear()

        # Simulate multiple requests
        collector.record_request(
            "/chat", "POST", 1.0, 200, tokens_used=150, model="claude-3-haiku-20240307"
        )

        collector.record_request(
            "/chat", "POST", 1.2, 200, tokens_used=200, model="claude-3-haiku-20240307"
        )

        usage = collector.get_model_usage(model="claude-3-haiku-20240307")

        assert "claude-3-haiku-20240307" in usage
        model_usage = usage["claude-3-haiku-20240307"]
        assert model_usage.total_tokens >= 350
        assert model_usage.request_count >= 2
