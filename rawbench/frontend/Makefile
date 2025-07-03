.PHONY: install dev build preview clean lint format

# Install dependencies
install:
	npm install

# Start development server
dev:
	npm run dev

# Build for production
build:
	npm run build

# Preview production build
preview:
	npm run preview

# Clean build artifacts
clean:
	rm -rf dist
	rm -rf node_modules/.cache

# Lint code
lint:
	npm run lint

# Format code
format:
	npm run format

# Run all checks
check: lint format

# Setup project (install + build)
setup: install build

# Development workflow
dev-setup: install dev
