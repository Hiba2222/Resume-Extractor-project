#!/bin/bash
# =============================================================================
# CV Extractor - AI-Powered Resume Processing Launcher
# =============================================================================
# Professional launch script for the CV Extractor application
# Supports Docker, Python direct execution, and various utility functions
# =============================================================================

# Colors for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Print enhanced header
echo -e "${CYAN}================================================================${NC}"
echo -e "${CYAN}              🤖 CV EXTRACTOR LAUNCHER 🚀                     ${NC}"
echo -e "${CYAN}          AI-Powered Resume Processing Platform               ${NC}"
echo -e "${CYAN}================================================================${NC}"
echo -e "${YELLOW}Features: Multiple AI Models | Modern Web UI | Real-time Processing${NC}"
echo -e "${BLUE}Models: Llama 3, Mistral, Microsoft Phi${NC}"

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}Error: Docker is not running.${NC}"
        echo -e "${YELLOW}Please start Docker Desktop and try again.${NC}"
        exit 1
    fi
}

# Function to start with Docker
start_with_docker() {
    echo -e "${GREEN}🐳 Starting CV Extractor with Docker...${NC}"
    check_docker
    
    echo -e "${YELLOW}🔨 Building and starting containers...${NC}"
    echo -e "${BLUE}This may take a few minutes on first run...${NC}"
    
    if [ -f "docker-compose.yml" ]; then
        docker-compose up --build
    elif [ -f "Dockerfile" ]; then
        echo -e "${YELLOW}📦 Building Docker image...${NC}"
        docker build -t cv-extractor .
        echo -e "${GREEN}🚀 Starting container...${NC}"
        docker run -p 5000:5000 cv-extractor
    else
        echo -e "${RED}❌ No Docker configuration found${NC}"
        echo -e "${YELLOW}Please ensure Dockerfile or docker-compose.yml exists${NC}"
        exit 1
    fi
}

# Function to start with Python directly
start_with_python() {
    echo -e "${GREEN}🐍 Starting CV Extractor with Python...${NC}"
    echo -e "${YELLOW}Checking Python installation...${NC}"
    
    if command -v python3 &>/dev/null; then
        PYTHON_CMD="python3"
        echo -e "${GREEN}✓ Python 3 found${NC}"
    elif command -v python &>/dev/null; then
        PYTHON_CMD="python"
        echo -e "${GREEN}✓ Python found${NC}"
    else
        echo -e "${RED}❌ Error: Python not found.${NC}"
        echo -e "${YELLOW}Please install Python 3.8+ and try again.${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}📦 Installing/updating dependencies...${NC}"
    if [ -f "requirements.txt" ]; then
        $PYTHON_CMD -m pip install -r requirements.txt
        echo -e "${GREEN}✓ Dependencies installed${NC}"
    else
        echo -e "${YELLOW}⚠️  No requirements.txt found${NC}"
    fi
    
    echo -e "${GREEN}🚀 Starting the web application...${NC}"
    echo -e "${CYAN}🌐 Access the application at: ${PURPLE}http://localhost:5000${NC}"
    echo -e "${BLUE}📱 Mobile-friendly interface available${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
    echo ""
    
    # Use the correct path for the Flask app
    $PYTHON_CMD web/app.py
}

# Function to show usage examples and run utilities
show_usage() {
    echo -e "${GREEN}📋 CV Extractor Usage Examples & Utilities${NC}"
    echo ""
    
    if command -v python3 &>/dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &>/dev/null; then
        PYTHON_CMD="python"
    else
        echo -e "${RED}❌ Error: Python not found.${NC}"
        exit 1
    fi
    
    echo -e "${CYAN}🧪 Testing:${NC}"
    echo -e "${BLUE}  $PYTHON_CMD scripts/run_tests.py${NC}                    # Run all tests"
    echo -e "${BLUE}  $PYTHON_CMD -m pytest tests/test_web.py -v${NC}         # Run web tests"
    echo ""
    
    echo -e "${CYAN}📊 Evaluation:${NC}"
    echo -e "${BLUE}  $PYTHON_CMD scripts/run_evaluation.py${NC}              # Run model evaluation"
    echo -e "${BLUE}  $PYTHON_CMD scripts/run_evaluation.py --cv-dir data/input${NC}  # Evaluate dataset"
    echo ""
    
    echo -e "${CYAN}🔧 Development:${NC}"
    echo -e "${BLUE}  $PYTHON_CMD web/app.py${NC}                            # Start web server directly"
    echo -e "${BLUE}  $PYTHON_CMD scripts/run_web.py${NC}                    # Alternative web startup"
    echo ""
    
    echo -e "${CYAN}📁 Project Structure:${NC}"
    echo -e "${YELLOW}  web/templates/    ${NC}# Organized HTML templates"
    echo -e "${YELLOW}  web/static/css/   ${NC}# Modular CSS architecture"
    echo -e "${YELLOW}  web/static/js/    ${NC}# JavaScript modules"
    echo -e "${YELLOW}  app/             ${NC}# Core application logic"
    echo -e "${YELLOW}  tests/           ${NC}# Comprehensive test suite"
    echo ""
    
    read -p "Press Enter to return to main menu..."
}

# Function to run tests
run_tests() {
    echo -e "${GREEN}🧪 Running CV Extractor Tests...${NC}"
    
    if command -v python3 &>/dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &>/dev/null; then
        PYTHON_CMD="python"
    else
        echo -e "${RED}❌ Error: Python not found.${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}📋 Running comprehensive test suite...${NC}"
    $PYTHON_CMD scripts/run_tests.py
    
    read -p "Press Enter to return to main menu..."
}

# Function to stop Docker containers
stop_docker() {
    echo -e "${YELLOW}🛑 Stopping Docker containers...${NC}"
    
    if [ -f "docker-compose.yml" ]; then
        docker-compose down
    else
        echo -e "${YELLOW}Stopping any running cv-extractor containers...${NC}"
        docker stop $(docker ps -q --filter ancestor=cv-extractor) 2>/dev/null || true
    fi
    
    echo -e "${GREEN}✓ Docker containers stopped.${NC}"
    read -p "Press Enter to return to main menu..."
}

# Main menu
show_menu() {
    echo -e "\n${CYAN}════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}🎯 Choose an option:${NC}"
    echo -e "${CYAN}════════════════════════════════════════════${NC}"
    echo -e "${BLUE}1.${NC} 🐳 Start Web App with Docker ${PURPLE}(recommended)${NC}"
    echo -e "${BLUE}2.${NC} 🐍 Start Web App with Python directly"
    echo -e "${BLUE}3.${NC} 📋 Show usage examples & utilities"
    echo -e "${BLUE}4.${NC} 🧪 Run test suite"
    echo -e "${BLUE}5.${NC} 🛑 Stop running Docker containers"
    echo -e "${BLUE}6.${NC} 👋 Exit"
    echo -e "${CYAN}════════════════════════════════════════════${NC}"
    
    read -p "Enter your choice [1-6]: " choice
    
    case $choice in
        1) start_with_docker ;;
        2) start_with_python ;;
        3) show_usage ;;
        4) run_tests ;;
        5) stop_docker ;;
        6) echo -e "${GREEN}👋 Exiting. Thank you for using CV Extractor!${NC}"; exit 0 ;;
        *) echo -e "${RED}❌ Invalid choice. Please try again.${NC}"; show_menu ;;
    esac
}

# Main execution
main() {
    # Check if we're in the right directory
    if [ ! -f "web/app.py" ]; then
        echo -e "${RED}❌ Error: Please run this script from the project root directory${NC}"
        echo -e "${YELLOW}Expected to find: web/app.py${NC}"
        exit 1
    fi
    
    # Show the menu
    show_menu
}

# Start the application
main 