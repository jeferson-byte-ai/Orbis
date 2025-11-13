"""
Orbis - Startup Script
Safe initialization with error handling
"""
import sys
import os
import logging

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment():
    """Check if environment is properly configured"""
    logger.info("🔍 Checking environment...")
    
    # Check .env file
    if not os.path.exists(".env"):
        logger.error("❌ .env file not found!")
        return False
    
    # Check data directory
    if not os.path.exists("data"):
        logger.info("📁 Creating data directory...")
        os.makedirs("data", exist_ok=True)
    
    logger.info("✅ Environment check passed")
    return True

def start_server():
    """Start the FastAPI server with uvicorn"""
    logger.info("🚀 Starting Orbis Backend...")
    
    try:
        import uvicorn
        from backend.config import settings
        
        uvicorn.run(
            "backend.main:app",
            host=settings.api_host,
            port=settings.api_port,
            reload=settings.debug,
            log_level=settings.log_level.lower()
        )
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.error("💡 Try: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if check_environment():
        start_server()
    else:
        logger.error("❌ Environment check failed. Please fix the issues above.")
        sys.exit(1)
