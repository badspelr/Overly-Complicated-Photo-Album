#!/bin/bash

# Photo Album Docker Development Helper
# Makes the long docker-compose commands easier to use

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

COMPOSE_FILES="-f docker-compose.light.yml -f docker-compose.dev.yml"

case "$1" in
  up)
    echo -e "${GREEN}Starting Photo Album in DEVELOPMENT mode...${NC}"
    docker-compose $COMPOSE_FILES up -d
    echo -e "${GREEN}✓ Started! Access at http://localhost:8000${NC}"
    echo -e "${YELLOW}Code is mounted - edit files and refresh browser!${NC}"
    ;;
  down)
    echo -e "${YELLOW}Stopping Photo Album...${NC}"
    docker-compose $COMPOSE_FILES down
    echo -e "${GREEN}✓ Stopped${NC}"
    ;;
  restart)
    echo -e "${YELLOW}Restarting Photo Album...${NC}"
    docker-compose $COMPOSE_FILES restart
    echo -e "${GREEN}✓ Restarted${NC}"
    ;;
  logs)
    docker-compose $COMPOSE_FILES logs -f
    ;;
  shell)
    docker-compose $COMPOSE_FILES exec web python manage.py shell
    ;;
  bash)
    docker-compose $COMPOSE_FILES exec web bash
    ;;
  ps)
    docker-compose $COMPOSE_FILES ps
    ;;
  *)
    echo "Photo Album Development Helper"
    echo ""
    echo "Usage: ./dev.sh [command]"
    echo ""
    echo "Commands:"
    echo "  up       - Start in development mode"
    echo "  down     - Stop all services"
    echo "  restart  - Restart all services"
    echo "  logs     - View logs (Ctrl+C to exit)"
    echo "  shell    - Open Django shell"
    echo "  bash     - Open bash in web container"
    echo "  ps       - Show running containers"
    echo ""
    echo "Examples:"
    echo "  ./dev.sh up       # Start development"
    echo "  ./dev.sh logs     # Watch logs"
    echo "  ./dev.sh down     # Stop everything"
    ;;
esac
