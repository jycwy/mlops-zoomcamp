#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if LocalStack is ready
wait_for_localstack() {
    print_status "Waiting for LocalStack to be ready..."
    for i in {1..30}; do
        if curl -s http://localhost:4566/_localstack/health > /dev/null 2>&1; then
            print_status "LocalStack is ready!"
            return 0
        fi
        print_status "Waiting for LocalStack... (attempt $i/30)"
        sleep 2
    done
    print_error "LocalStack failed to start within 60 seconds"
    return 1
}

# Function to create S3 buckets
create_s3_buckets() {
    print_status "Creating S3 buckets..."
    
    # Create the main bucket for predictions
    aws --endpoint-url=http://localhost:4566 s3 mb s3://nyc-duration-prediction-alexey 2>/dev/null || print_warning "Bucket nyc-duration-prediction-alexey might already exist"
    
    # Create bucket for input data (used by integration test)
    aws --endpoint-url=http://localhost:4566 s3 mb s3://nyc-duration 2>/dev/null || print_warning "Bucket nyc-duration might already exist"
    
    print_status "S3 buckets created successfully"
}

# Function to cleanup
cleanup() {
    print_status "Cleaning up..."
    docker-compose down
    print_status "Cleanup completed"
}

# Main execution
main() {
    print_status "Starting MLOps Integration Test"
    
    # Check if required files exist
    if [ ! -f "batch.py" ]; then
        print_error "batch.py not found. Please run this script from the homework directory."
        exit 1
    fi
    
    if [ ! -f "model.bin" ]; then
        print_error "model.bin not found. Please ensure the model file exists."
        exit 1
    fi
    
    if [ ! -f "docker-compose.yaml" ]; then
        print_error "docker-compose.yaml not found. Please ensure Docker Compose configuration exists."
        exit 1
    fi
    
    # Export environment variables
    export S3_ENDPOINT_URL="http://localhost:4566"
    export INPUT_FILE_PATTERN="s3://nyc-duration/yellow_tripdata_{year:04d}-{month:02d}.parquet"
    export OUTPUT_FILE_PATTERN="s3://nyc-duration-prediction-alexey/taxi_type=fhv/year={year:04d}/month={month:02d}/predictions.parquet"
    
    print_status "Environment variables set:"
    print_status "  S3_ENDPOINT_URL=$S3_ENDPOINT_URL"
    print_status "  INPUT_FILE_PATTERN=$INPUT_FILE_PATTERN"
    print_status "  OUTPUT_FILE_PATTERN=$OUTPUT_FILE_PATTERN"
    
    # Start LocalStack
    print_status "Starting LocalStack..."
    docker-compose up -d
    
    # Set trap to cleanup on exit
    trap cleanup EXIT
    
    # Wait for LocalStack to be ready
    if ! wait_for_localstack; then
        print_error "Failed to start LocalStack"
        exit 1
    fi
    
    # Create S3 buckets
    create_s3_buckets
    
    # Install Python dependencies if Pipfile exists
    if [ -f "Pipfile" ]; then
        print_status "Installing Python dependencies..."
        pipenv install --dev
    fi
    
    # Run the integration test
    print_status "Running integration test..."
    cd integration-test
    
    # Create .env file for the integration test
    echo "S3_ENDPOINT_URL=$S3_ENDPOINT_URL" > .env
    echo "INPUT_FILE_PATTERN=$INPUT_FILE_PATTERN" >> .env
    echo "OUTPUT_FILE_PATTERN=$OUTPUT_FILE_PATTERN" >> .env
    
    # Run the integration test
    if pipenv run python integration_test.py test; then
        print_status "Integration test completed successfully!"
        echo -e "${GREEN}✅ All tests passed!${NC}"
    else
        print_error "Integration test failed!"
        echo -e "${RED}❌ Test execution failed!${NC}"
        exit 1
    fi
    
    cd ..
}

# Handle command line arguments
case "${1:-}" in
    --no-cleanup)
        print_warning "Running without cleanup (LocalStack will remain running)"
        trap - EXIT
        main
        ;;
    --cleanup-only)
        print_status "Cleaning up existing LocalStack containers..."
        cleanup
        ;;
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --no-cleanup    Don't stop LocalStack after test completion"
        echo "  --cleanup-only  Only cleanup existing LocalStack containers"
        echo "  --help, -h      Show this help message"
        echo ""
        echo "Default: Run integration test with automatic cleanup"
        ;;
    "")
        main
        ;;
    *)
        print_error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac 