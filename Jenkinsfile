pipeline {
    agent any
    environment {
        COMPOSE_FILE = "docker-compose.yml"
        DOCKERFILE = "Dockerfile-jenkins"
        MONGO_URL = "mongodb://mongodb:27017"
        DB_NAME = "mongodb"
        APP_PORT = 8081
        MONGO_PLATFORM = "linux/arm64"
    }
    stages {
        stage("Build and start image") {
            steps {
                sh "cp .env.dev .env"
                sh "docker-compose build"
                sh "docker-compose up -d"
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    sh 'docker-compose exec -T app pytest -p no:cacheprovider'
                }
            }
        }
    }

    post {
        always {
            script {
                sh 'docker-compose down'
            }
        }
    }
}
