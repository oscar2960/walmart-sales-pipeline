// Jenkinsfile - Pipeline declarativo de CI/CD
//
// Disparado automáticamente por un Webhook de GitHub (configurado vía
// Ngrok para exponer Jenkins local a Internet). Ejecuta: checkout,
// instalación de dependencias, lint, pruebas unitarias, build de imagen
// Docker, pruebas de integración contra PostgreSQL real y despliegue
// local con docker-compose.

pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    triggers {
        // Requiere el plugin "GitHub Integration" y el Webhook configurado
        // en GitHub -> Settings -> Webhooks apuntando a la URL de Ngrok.
        githubPush()
    }

    environment {
        IMAGE_NAME = "walmart-sales-app"
        IMAGE_TAG  = "${env.BUILD_NUMBER}"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Instalar dependencias') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt -r requirements-dev.txt
                '''
            }
        }

        stage('Análisis estático (Lint)') {
            steps {
                sh '''
                    . venv/bin/activate
                    flake8 app tests --max-line-length=120
                '''
            }
        }

        stage('Pruebas unitarias') {
            steps {
                sh '''
                    . venv/bin/activate
                    mkdir -p reports
                    pytest tests/ -v --cov=app --junitxml=reports/junit.xml
                '''
            }
            post {
                always {
                    junit 'reports/junit.xml'
                }
            }
        }

        stage('Build imagen Docker') {
            steps {
                sh 'docker build -t $IMAGE_NAME:$IMAGE_TAG -t $IMAGE_NAME:latest .'
            }
        }

        stage('Pruebas de integración (Docker Compose)') {
            steps {
                sh '''
                    docker compose down -v --remove-orphans || true
                    docker compose up -d postgres
                    echo "Esperando a que PostgreSQL esté saludable..."
                    sleep 10
                    docker compose run --rm app python -m app.main
                '''
            }
            post {
                always {
                    sh 'docker compose down -v --remove-orphans || true'
                }
            }
        }

        stage('Despliegue local') {
            when {
                anyOf {
                    branch 'main'
                    branch 'master'
                }
            }
            steps {
                sh '''
                    docker compose down || true
                    docker compose up -d --build
                '''
            }
        }
    }

    post {
        success {
            echo "✅ Pipeline ejecutado con éxito - Build #${env.BUILD_NUMBER}"
        }
        failure {
            echo "❌ Pipeline falló - Build #${env.BUILD_NUMBER}. Revisar logs."
        }
    }
}
