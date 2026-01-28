.PHONY: help validate clean open-notebook check-notebook

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo '┌─────────────────────────────────────────────────┐'
	@echo '│  ZAAI-SYSTEM - Make Commands                    │'
	@echo '└─────────────────────────────────────────────────┘'
	@echo ''
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ''

validate: ## Run all validation checks
	@echo "🔍 Running validation checks..."
	@echo ""
	@echo "✓ Checking notebook structure..."
	@python3 -c "import json; nb = json.load(open('ZAAI_ScrollDaemon.ipynb')); assert 'cells' in nb; print(f'  Notebook has {len(nb[\"cells\"])} cells')"
	@echo ""
	@echo "✓ Checking required files..."
	@test -f README.md && echo "  ✓ README.md" || exit 1
	@test -f LICENSE && echo "  ✓ LICENSE" || exit 1
	@test -f CONTRIBUTING.md && echo "  ✓ CONTRIBUTING.md" || exit 1
	@test -f CODE_OF_CONDUCT.md && echo "  ✓ CODE_OF_CONDUCT.md" || exit 1
	@test -f SECURITY.md && echo "  ✓ SECURITY.md" || exit 1
	@echo ""
	@echo "✅ All validation checks passed!"

check-notebook: ## Validate Jupyter notebook structure
	@echo "🔍 Validating notebook..."
	@python3 -c "import json; nb = json.load(open('ZAAI_ScrollDaemon.ipynb')); assert 'cells' in nb and 'metadata' in nb; print(f'✓ Notebook is valid with {len(nb[\"cells\"])} cells')"

open-notebook: ## Open the notebook in Jupyter (requires Jupyter installation)
	@echo "📓 Opening notebook..."
	@jupyter notebook ZAAI_ScrollDaemon.ipynb 2>/dev/null || echo "⚠️  Jupyter not installed. Run: pip install jupyter"

clean: ## Remove temporary files and caches
	@echo "🧹 Cleaning temporary files..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type d -name ".pytest_cache" -delete
	@find . -type d -name ".ipynb_checkpoints" -delete
	@echo "✅ Cleanup complete!"

install-dev: ## Install development dependencies
	@echo "📦 Installing dependencies..."
	@pip install -r requirements.txt
	@pip install jupyter jupyterlab
	@echo "✅ Dependencies installed!"

tree: ## Show repository structure
	@echo "📁 Repository structure:"
	@echo ""
	@tree -I '.git|__pycache__|*.pyc|.ipynb_checkpoints' -L 3 || find . -not -path '*/\.*' -type f | sort

status: ## Show git status and recent commits
	@echo "📊 Repository status:"
	@echo ""
	@git status -s
	@echo ""
	@echo "Recent commits:"
	@git log --oneline -5

colab: ## Show link to open in Google Colab
	@echo "🚀 Open in Google Colab:"
	@echo ""
	@echo "https://colab.research.google.com/github/Zygros/ZAAI-SYSTEM/blob/main/ZAAI_ScrollDaemon.ipynb"
	@echo ""
