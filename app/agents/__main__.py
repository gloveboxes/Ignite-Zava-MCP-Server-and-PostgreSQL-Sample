from agent_framework.devui import serve
import os

from .stock import workflow as stock_workflow


def main():
    port = os.environ.get("PORT", 8090)

    # Launch server with the workflow
    serve(entities=[stock_workflow], port=int(port), auto_open=True, tracing_enabled=True)


if __name__ == "__main__":
    main()
