  llm-multiroute/Dockerfile
  - Python 3.12 slim base image
  - Installs FastAPI/uvicorn dependencies
  - Exposes port 8080
  - Runs uvicorn on 0.0.0.0:8080
  llm-frontend-python/Dockerfile
  - Python 3.12 slim base image
  - Installs Flask/requests dependencies
  - Exposes port 5000
  - Runs python app.py
  docker-compose.yml (project root)
  - Defines a shared llm-network (bridge driver) so both containers can communicate
  - llm-multiroute service: passes through all Ollama config via environment
   variables (reads from your host .env or shell)
  - llm-frontend-python service: sets BACKEND_URL=http://llm-multiroute:8080
   so the frontend proxy reaches the backend using Docker's internal DNS, and FLASK_DEBUG=false for production
  - depends_on ensures the backend starts before the frontend 
  
  How to run
  # Set your API key (or put it in a .env file at the project root)
  export OLLAMA_API_KEY=your_key_here 
  
  # Build and start both services 
  docker compose up --build

  The frontend will be available at http://localhost:5000 and the backend  API at http://localhost:8080.  


  # Added to both image publishing workflows
  - GHCR login — Authenticates to ghcr.io with the built-in GITHUB_TOKEN.
  Image-publishing jobs request packages: write permission and skip publishing on pull requests.
  - Metadata extraction — Uses docker/metadata-action@v5 to generate smart tags:
    - sha-<commit> on every build
    - Branch name tag (e.g., main)
    - PR number tag on pull requests
    - Semver tag if you use git tags (e.g., v1.0.0)
    - latest only on the default branch
  - Conditional push — Builds on all triggers but only pushes to GHCR on
   push events (not on PRs, which get build-only validation)
  Image names on GHCR
  ┌─────────────────────┬────────────────────────────────┐             
  │      Workflow       │             Image              │             
  ├─────────────────────┼────────────────────────────────┤             
  │ llm-multiroute      │ ghcr.io/<owner>/llmapp09-llm-multiroute      │
  ├─────────────────────┼────────────────────────────────┤             
  │ llm-frontend-python │ ghcr.io/<owner>/llmapp09-llm-frontend-python │
  └─────────────────────┴────────────────────────────────┘             
  No registry secret is required. GitHub Actions uses GITHUB_TOKEN with
  packages: write permission to publish packages under the repository owner.

  Manual builds
  Log in to GHCR before running either build.sh script. Use a GitHub token
  with write:packages permission:

  export GHCR_OWNER="your-github-owner"
  export GHCR_TOKEN="your-github-token"
  echo "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_OWNER" --password-stdin

  Then run build.sh from the corresponding llm-multiroute or
  llm-frontend-python directory. The scripts publish the :latest tag.