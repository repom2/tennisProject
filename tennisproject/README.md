### Reset the Development Environment

To reset the development environment and restart from a clean state, run

```bash
docker compose down --volumes --rmi all
'''

If you are using Docker Compose, Poetry can be used by prefixing commands with `docker compose exec app`. For example:

```bash
docker compose exec app poetry add <package name>
'''

docker compose exec db psql -U tennis