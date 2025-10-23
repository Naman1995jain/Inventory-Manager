CI / CD setup (GitHub Actions) — Inventory-Manager

Overview
--------
This project uses Docker Compose to run Backend, Frontend and Postgres. The provided GitHub Actions workflow (.github/workflows/deploy.yml) performs a push-triggered SSH deployment: it connects to your server, fetches the latest code, and runs docker compose up -d --build on the server.

What the workflow doesok
- Checks out the repo
- Sets up SSH key material from GitHub Secrets
- Connects to your server and resets the working tree to the pushed branch
- Runs docker compose pull (optional) then docker compose up -d --build

Required GitHub secrets
- SSH_PRIVATE_KEY — the private key for the deploy user (PEM format)
- DEPLOY_HOST — IP or hostname of your server
- DEPLOY_USER — username to SSH as (recommended: a dedicated deploy user)
- DEPLOY_PATH — absolute path to the project on the server (where docker-compose.yml lives)
- SSH_KNOWN_HOSTS — (optional) content for ~/.ssh/known_hosts; if missing the workflow will run ssh-keyscan automatically

Recommended server setup
1. Create a deploy user (no passwd login)
   - sudo adduser deploy
   - mkdir -p /home/deploy/.ssh && chown deploy:deploy /home/deploy/.ssh && chmod 700 /home/deploy/.ssh
2. Add your public key to /home/deploy/.ssh/authorized_keys
3. Install docker and docker compose plugin
   - https://docs.docker.com/engine/install/
   - For compose plugin: https://docs.docker.com/compose/install/
4. Ensure the deploy user can run docker (add to docker group)
   - sudo usermod -aG docker deploy
5. Clone the repo to DEPLOY_PATH and make sure docker-compose.yml is present
   - sudo -u deploy git clone <repo> <DEPLOY_PATH>

Notes and extra options
- If you prefer to build images in CI and push to a registry, add build steps in the workflow to login to your registry (GHCR, Docker Hub), build and push images. Then on the server use docker compose pull before up to fetch images.
- For zero-downtime deploys consider using a reverse proxy (nginx) with healthchecks, or use docker compose's update patterns and a temporary service name swap.
- Keep secrets outside your repo. Use environment variables and a secrets manager when possible.

Testing and rollback
- Test by pushing a small change to the branch used by the workflow (main/master)
- Rollback: ssh into server and run git reset --hard origin/<old-commit-or-tag> && docker compose up -d --build

Security notes
- Limit SSH key scope. Use a deploy-only key. Consider using forced commands or restricting agent forwarding.
- Keep Docker and the OS up to date.
