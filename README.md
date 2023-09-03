# gatekeeper
Bot that assigns roles for the TheMoeWay discord server.

## Usage
> [!IMPORTANT]
> Ensure that `docker-compose.yml` has the correct env vars set.

- Bring container up
```bash
docker compose up -d
# Append --build if code has been changed after container was built
```

- Stop container
```bash
docker compose down
```

- To investigate
```bash
docker compose ps
docker compose logs
```