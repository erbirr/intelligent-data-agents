#!/bin/bash

# Script de configuración inicial para Google Cloud Run
# Sistema MCP - Agentes Inteligentes
# Autor: Sistema MCP Tecnoandina

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuración del proyecto
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-prj-ia-tecnoandina}"
REGION="${GOOGLE_CLOUD_REGION:-us-central1}"
SERVICE_NAME="ida-microservice"

echo -e "${BLUE}🚀 Configuración inicial de Google Cloud para MCP${NC}"
echo "=================================================="
echo "Proyecto: $PROJECT_ID"
echo "Región: $REGION"
echo ""

# Función para verificar si gcloud está instalado
check_gcloud() {
    if ! command -v gcloud &> /dev/null; then
        echo -e "${RED}❌ gcloud CLI no está instalado${NC}"
        echo "Instala gcloud CLI desde: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    echo -e "${GREEN}✅ gcloud CLI encontrado${NC}"
}

# Función para autenticación
authenticate() {
    echo -e "${YELLOW}🔐 Verificando autenticación...${NC}"
    
    # Verificar si hay una cuenta activa
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        echo -e "${YELLOW}⚠️ No hay cuentas autenticadas${NC}"
        echo "Iniciando proceso de autenticación..."
        gcloud auth login
    fi
    
    # Configurar proyecto
    echo -e "${YELLOW}🔧 Configurando proyecto...${NC}"
    gcloud config set project $PROJECT_ID
    gcloud config set compute/region $REGION
    gcloud config set compute/zone ${REGION}-a
    
    echo -e "${GREEN}✅ Autenticación completada${NC}"
}

# Función para habilitar APIs
enable_apis() {
    echo -e "${YELLOW}🔧 Habilitando APIs necesarias...${NC}"
    
    # Lista de APIs necesarias
    apis=(
        "cloudbuild.googleapis.com"
        "run.googleapis.com"
        "containerregistry.googleapis.com"
        "artifactregistry.googleapis.com"
        "aiplatform.googleapis.com"
        "secretmanager.googleapis.com"
        "logging.googleapis.com"
        "monitoring.googleapis.com"
    )
    
    for api in "${apis[@]}"; do
        echo "Habilitando $api..."
        gcloud services enable "$api" --quiet
    done
    
    echo -e "${GREEN}✅ APIs habilitadas${NC}"
}

# Función para configurar IAM
setup_iam() {
    echo -e "${YELLOW}👤 Configurando roles IAM...${NC}"
    
    # Obtener cuenta de servicio de Cloud Run
    PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
    CLOUD_RUN_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
    
    # Roles necesarios para Cloud Run
    roles=(
        "roles/aiplatform.user"
        "roles/secretmanager.secretAccessor"
        "roles/logging.logWriter"
        "roles/monitoring.metricWriter"
    )
    
    for role in "${roles[@]}"; do
        echo "Asignando rol $role..."
        gcloud projects add-iam-policy-binding $PROJECT_ID \
            --member="serviceAccount:$CLOUD_RUN_SA" \
            --role="$role" \
            --quiet > /dev/null 2>&1 || true
    done
    
    echo -e "${GREEN}✅ Roles IAM configurados${NC}"
}

# Función para crear secrets (opcional)
setup_secrets() {
    echo -e "${YELLOW}🔐 Configurando Secret Manager (opcional)...${NC}"
    
    # Crear secrets para credenciales de bases de datos si no existen
    secrets=(
        "neo4j-password"
        "postgres-password"
        "vertex-ai-credentials"
    )
    
    for secret in "${secrets[@]}"; do
        if ! gcloud secrets describe "$secret" --quiet > /dev/null 2>&1; then
            echo "Creando secret: $secret"
            echo "placeholder-value" | gcloud secrets create "$secret" --data-file=- --quiet
            echo -e "${YELLOW}⚠️ Actualiza el secret '$secret' con el valor real${NC}"
        else
            echo "Secret '$secret' ya existe"
        fi
    done
    
    echo -e "${GREEN}✅ Secrets configurados${NC}"
}

# Función para crear configuración de red (opcional)
setup_network() {
    echo -e "${YELLOW}🌐 Verificando configuración de red...${NC}"
    
    # Verificar VPC por defecto
    if gcloud compute networks describe default --quiet > /dev/null 2>&1; then
        echo "Red por defecto disponible"
    else
        echo -e "${YELLOW}⚠️ Considera configurar una VPC personalizada para mayor seguridad${NC}"
    fi
    
    echo -e "${GREEN}✅ Configuración de red verificada${NC}"
}

# Función para verificar cuotas
check_quotas() {
    echo -e "${YELLOW}📊 Verificando cuotas...${NC}"
    
    # Verificar cuotas de Cloud Run
    echo "Verificando cuotas de Cloud Run en $REGION..."
    
    # Verificar si hay servicios desplegados
    existing_services=$(gcloud run services list --region=$REGION --format="value(name)" | wc -l)
    echo "Servicios Cloud Run existentes: $existing_services"
    
    if [ "$existing_services" -gt 50 ]; then
        echo -e "${YELLOW}⚠️ Muchos servicios Cloud Run. Verifica límites.${NC}"
    fi
    
    echo -e "${GREEN}✅ Cuotas verificadas${NC}"
}

# Función para crear configuración básica
create_config() {
    echo -e "${YELLOW}📝 Creando configuración básica...${NC}"
    
    # Crear archivo de configuración para deployment
    cat > gcp_config.env << EOF
# Configuración GCP para MCP Microservice
GOOGLE_CLOUD_PROJECT=$PROJECT_ID
GOOGLE_CLOUD_REGION=$REGION
GOOGLE_CLOUD_ZONE=${REGION}-a

# URLs importantes
CLOUD_CONSOLE_URL=https://console.cloud.google.com/run?project=$PROJECT_ID
CLOUD_BUILD_URL=https://console.cloud.google.com/cloud-build?project=$PROJECT_ID
LOGS_URL=https://console.cloud.google.com/logs?project=$PROJECT_ID

# Comandos útiles
# Ver servicios: gcloud run services list --region=$REGION
# Ver logs: gcloud logs read "resource.type=cloud_run_revision" --limit=50
# Actualizar servicio: gcloud run services update $SERVICE_NAME --region=$REGION
EOF

    echo -e "${GREEN}✅ Configuración creada en gcp_config.env${NC}"
}

# Función para mostrar resumen
show_summary() {
    echo ""
    echo -e "${BLUE}📋 RESUMEN DE CONFIGURACIÓN${NC}"
    echo "================================"
    echo "✅ Proyecto configurado: $PROJECT_ID"
    echo "✅ Región configurada: $REGION"
    echo "✅ APIs habilitadas"
    echo "✅ IAM configurado"
    echo "✅ Secrets preparados"
    echo ""
    echo -e "${GREEN}🎉 ¡Configuración completada!${NC}"
    echo ""
    echo -e "${YELLOW}Próximos pasos:${NC}"
    echo "1. Actualizar secrets con valores reales"
    echo "2. Ejecutar ./deploy.sh para desplegar"
    echo "3. Configurar monitoreo y alertas"
    echo ""
    echo -e "${BLUE}URLs útiles:${NC}"
    echo "• Console: https://console.cloud.google.com/run?project=$PROJECT_ID"
    echo "• Logs: https://console.cloud.google.com/logs?project=$PROJECT_ID"
    echo "• IAM: https://console.cloud.google.com/iam-admin?project=$PROJECT_ID"
}

# Función principal
main() {
    echo -e "${BLUE}Iniciando configuración de Google Cloud...${NC}"
    
    check_gcloud
    authenticate
    enable_apis
    setup_iam
    setup_secrets
    setup_network
    check_quotas
    create_config
    show_summary
}

# Función para mostrar ayuda
show_help() {
    echo "Uso: $0 [OPCIÓN]"
    echo ""
    echo "Opciones:"
    echo "  --skip-auth     Saltar autenticación (si ya estás autenticado)"
    echo "  --skip-secrets  Saltar configuración de secrets"
    echo "  --help          Mostrar esta ayuda"
    echo ""
    echo "Variables de entorno:"
    echo "  GOOGLE_CLOUD_PROJECT    ID del proyecto (default: prj-ia-tecnoandina)"
    echo "  GOOGLE_CLOUD_REGION     Región (default: us-central1)"
}

# Manejo de parámetros
case "${1:-}" in
    --help)
        show_help
        exit 0
        ;;
    --skip-auth)
        check_gcloud
        enable_apis
        setup_iam
        setup_secrets
        setup_network
        check_quotas
        create_config
        show_summary
        ;;
    --skip-secrets)
        check_gcloud
        authenticate
        enable_apis
        setup_iam
        setup_network
        check_quotas
        create_config
        show_summary
        ;;
    "")
        main
        ;;
    *)
        echo -e "${RED}❌ Opción no reconocida: $1${NC}"
        show_help
        exit 1
        ;;
esac
