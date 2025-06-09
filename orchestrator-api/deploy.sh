#!/bin/bash

# Script de despliegue para MCP Microservice en Google Cloud Run
# Autor: Sistema MCP
# Fecha: 2025-06-04

set -e  # Salir si cualquier comando falla

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables de configuración
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-prj-ia-tecnoandina}"
REGION="${GOOGLE_CLOUD_REGION:-us-central1}"
SERVICE_NAME="ida-microservice"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo -e "${BLUE}🚀 Iniciando despliegue de MCP Microservice${NC}"
echo "========================================"
echo "Proyecto: $PROJECT_ID"
echo "Región: $REGION"
echo "Servicio: $SERVICE_NAME"
echo "Imagen: $IMAGE_NAME"
echo ""

# Función para mostrar ayuda
show_help() {
    echo "Uso: $0 [OPCIÓN]"
    echo ""
    echo "Opciones:"
    echo "  --build-only    Solo construir la imagen, no desplegar"
    echo "  --deploy-only   Solo desplegar (asume que la imagen ya existe)"
    echo "  --local        Construir y ejecutar localmente"
    echo "  --help         Mostrar esta ayuda"
    echo ""
    echo "Variables de entorno:"
    echo "  GOOGLE_CLOUD_PROJECT    ID del proyecto GCP"
    echo "  GOOGLE_CLOUD_REGION     Región de despliegue"
    echo ""
}

# Función para verificar herramientas
check_tools() {
    echo -e "${YELLOW}🔍 Verificando herramientas...${NC}"
    
    if ! command -v gcloud &> /dev/null; then
        echo -e "${RED}❌ gcloud CLI no está instalado${NC}"
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker no está instalado${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Herramientas verificadas${NC}"
}

# Función para verificar autenticación
check_auth() {
    echo -e "${YELLOW}🔐 Verificando autenticación...${NC}"
    
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        echo -e "${RED}❌ No hay cuentas autenticadas en gcloud${NC}"
        echo "Ejecuta: gcloud auth login"
        exit 1
    fi
    
    # Verificar proyecto
    CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null || echo "")
    if [ "$CURRENT_PROJECT" != "$PROJECT_ID" ]; then
        echo -e "${YELLOW}⚠️  Configurando proyecto: $PROJECT_ID${NC}"
        gcloud config set project $PROJECT_ID
    fi
    
    echo -e "${GREEN}✅ Autenticación verificada${NC}"
}

# Función para habilitar APIs necesarias
enable_apis() {
    echo -e "${YELLOW}🔧 Habilitando APIs necesarias...${NC}"
    
    gcloud services enable \
        cloudbuild.googleapis.com \
        run.googleapis.com \
        containerregistry.googleapis.com \
        aiplatform.googleapis.com \
        --quiet
    
    echo -e "${GREEN}✅ APIs habilitadas${NC}"
}

# Función para construir imagen
build_image() {
    echo -e "${YELLOW}🔨 Construyendo imagen Docker...${NC}"
    
    # Crear tag con timestamp para versionado
    TIMESTAMP=$(date +%Y%m%d-%H%M%S)
    IMAGE_TAG="$IMAGE_NAME:$TIMESTAMP"
    IMAGE_LATEST="$IMAGE_NAME:latest"
    
    # Detectar si necesitamos especificar plataforma
    if [[ "$(uname -m)" == "arm64" ]] || [[ "$(uname -m)" == "aarch64" ]]; then
        echo -e "${YELLOW}⚠️  Detectada arquitectura ARM, construyendo para AMD64...${NC}"
        PLATFORM_FLAG="--platform linux/amd64"
    else
        PLATFORM_FLAG=""
    fi
    
    # Construir con la plataforma correcta
    docker build $PLATFORM_FLAG -t "$IMAGE_TAG" -t "$IMAGE_LATEST" .
    
    echo -e "${GREEN}✅ Imagen construida: $IMAGE_LATEST${NC}"
    
    # Subir imagen a Container Registry
    echo -e "${YELLOW}📤 Subiendo imagen a Container Registry...${NC}"
    docker push "$IMAGE_TAG"
    docker push "$IMAGE_LATEST"
    
    echo -e "${GREEN}✅ Imagen subida al registry${NC}"
    
    # Guardar tag para deployment
    echo "$IMAGE_TAG" > .last-image-tag
}

# Función para desplegar a Cloud Run
deploy_service() {
    echo -e "${YELLOW}🚀 Desplegando a Cloud Run...${NC}"
    
    # Usar el último tag construido o latest
    if [ -f .last-image-tag ]; then
        IMAGE_TAG=$(cat .last-image-tag)
    else
        IMAGE_TAG="$IMAGE_NAME:latest"
    fi
    
    gcloud run deploy $SERVICE_NAME \
        --image="$IMAGE_TAG" \
        --region="$REGION" \
        --platform=managed \
        --allow-unauthenticated \
        --memory=1Gi \
        --cpu=1 \
        --timeout=300 \
        --max-instances=10 \
        --min-instances=0 \
        --concurrency=80 \
        --port=8080 \
        --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=$REGION,ENV=production,LLM_ENABLED=true" \
        --quiet
    
    # Obtener URL del servicio
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")
    
    echo -e "${GREEN}✅ Servicio desplegado exitosamente${NC}"
    echo -e "${BLUE}🌐 URL del servicio: $SERVICE_URL${NC}"
    echo -e "${BLUE}📚 Documentación API: $SERVICE_URL/docs${NC}"
    echo -e "${BLUE}🖥️  Frontend: $SERVICE_URL/static/index.html${NC}"
}

# Función para ejecutar localmente
run_local() {
    echo -e "${YELLOW}🏠 Construyendo para ejecución local...${NC}"
    
    docker build -t ida-microservice-local .
    
    echo -e "${YELLOW}🏃 Ejecutando contenedor localmente...${NC}"
    echo "Presiona Ctrl+C para detener"
    
    docker run -p 8080:8080 \
        -e GOOGLE_CLOUD_PROJECT="$PROJECT_ID" \
        -e GOOGLE_CLOUD_LOCATION="$REGION" \
        -e ENV=development \
        -e LLM_ENABLED=true \
        --name ida-microservice-local \
        --rm \
        ida-microservice-local
}

# Función para limpiar recursos
cleanup() {
    echo -e "${YELLOW}🧹 Limpiando recursos temporales...${NC}"
    
    # Limpiar imágenes locales viejas
    docker image prune -f || true
    
    # Limpiar archivo temporal
    rm -f .last-image-tag
    
    echo -e "${GREEN}✅ Limpieza completada${NC}"
}

# Función principal
main() {
    case "${1:-}" in
        --help)
            show_help
            exit 0
            ;;
        --build-only)
            check_tools
            check_auth
            enable_apis
            build_image
            ;;
        --deploy-only)
            check_tools
            check_auth
            enable_apis
            deploy_service
            ;;
        --local)
            check_tools
            run_local
            ;;
        "")
            # Despliegue completo por defecto
            check_tools
            check_auth
            enable_apis
            build_image
            deploy_service
            cleanup
            ;;
        *)
            echo -e "${RED}❌ Opción no reconocida: $1${NC}"
            show_help
            exit 1
            ;;
    esac
}

# Trap para limpiar en caso de interrupción
trap cleanup EXIT

# Ejecutar función principal
main "$@"

echo -e "${GREEN}🎉 ¡Despliegue completado exitosamente!${NC}"
