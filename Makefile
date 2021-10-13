.PHONY: dev-run
dev-run: ## Run as newly build docker container in development mode
	docker build -t tranche_monitor .
	docker run tranche_monitor

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
