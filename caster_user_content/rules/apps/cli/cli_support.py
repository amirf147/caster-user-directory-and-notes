TRELLO_COMMANDS = {
    "help": "--help ",
    "auth": "auth",
    "board": "board",
    "card": "card",
    "list": "list",
    "member": "member",
    "search": "search",
    "team": "team",
    "token": "token",
    "user": "user",
    "sync": "sync",
}

OLLAMA_COMMANDS = {
    "list": "ollama list",
    "serve": "ollama serve",
    "p s": "ollama ps",
    "show": "ollama show",
    "show deep": "ollama show deepseek-r1:1.5b",
    "stop": "ollama stop",
    "help list": "ollama help list",
    "help show": "ollama help show",
    "help serve": "ollama help serve",
    "help create": "ollama help create",
    "help ps": "ollama help ps",
    "help": "ollama help",
    "run": "ollama run",
    "run deep": "ollama run deepseek-r1:1.5b",
    "pull": "ollama pull",
    "create": "ollama create",
} 

DOCKER_COMMANDS = {
    "ps": "docker ps",
    "ps all": "docker ps -a",
    "images": "docker images",
    "stop": "docker stop",
    "start": "docker start",
    "restart": "docker restart",
    "remove": "docker rm",
    "remove image": "docker rmi",
    "pull": "docker pull",
    "run": "docker run",
    "exec": "docker exec",
    "logs": "docker logs",
    "build": "docker build",
    "compose up": "docker-compose up",
    "compose down": "docker-compose down",
    "compose p s": "docker-compose ps",
    "system prune": "docker system prune",
    "network list": "docker network ls",
    "volume list": "docker volume ls",
    "inspect": "docker inspect",
    "stats": "docker stats",
    "run nathan": "docker run -it --rm --name n8n -p 5678:5678 -p 11434:11434 -v n8n_data:/home/node/.n8n -e N8N_RUNNERS_ENABLED=true -e N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=true docker.n8n.io/n8nio/n8n",
} 

LIST_COMMANDS = {
    "names": "Get-ChildItemColor",
    "folders": "Get-ChildItem -Directory -Name",
    "recent": "Get-ChildItem | Sort-Object LastWriteTime | Format-List Name, LastWriteTime"
}

PYTHON_COMMANDS = {
    "create virtual": "-m venv .venv",
}

PIP_COMMANDS = {
    "install are": "install -r ",
    "install": "install ",
    "install upgrade pip": "install --upgrade pip",
}