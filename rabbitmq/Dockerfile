FROM rabbitmq:3.11.13-management-alpine
HEALTHCHECK --interval=5s --timeout=2s --retries=12 \
    CMD rabbitmq-diagnostics -q ping
