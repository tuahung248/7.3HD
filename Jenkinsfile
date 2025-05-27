pipeline {
    agent any

    environment {
        PYTHON = '"C:\\Users\\tuant\\AppData\\Local\\Programs\\Python\\Python313\\python.exe"'
        PIP = '"C:\\Users\\tuant\\AppData\\Local\\Programs\\Python\\Python313\\python.exe" -m pip'
        FLAKE8 = '"C:\\Users\\tuant\\AppData\\Local\\Programs\\Python\\Python313\\Scripts\\flake8.exe"'
        BANDIT = '"C:\\Users\\tuant\\AppData\\Local\\Programs\\Python\\Python313\\Scripts\\bandit.exe"'
        DOCKERHUB_CREDENTIALS = credentials('dockerhub')
        IMAGE_NAME = "tuahung248/hr-policy-assistant"
        VERSION = "${env.BUILD_NUMBER}"
        STAGING_PORT = "8000"
        PROD_PORT = "8001"
    }

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
        retry(2)
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.GIT_COMMIT_SHORT = sh(
                        script: 'git rev-parse --short HEAD',
                        returnStdout: true
                    ).trim()
                }
            }
        }

        stage('Build') {
            steps {
                dir('backend') {
                    bat "${PIP} install --upgrade pip"
                    bat "${PIP} install -r requirements.txt"
                }
            }
            post {
                failure {
                    echo "Build failed - check dependency issues"
                }
            }
        }

        stage('Unit + Integration Test') {
            steps {
                dir('backend') {
                    bat 'if not exist test-reports mkdir test-reports'
                    bat "${PYTHON} -m pytest --junitxml=test-reports/results.xml --cov=. --cov-report=xml --cov-report=html"
                }
            }
            post {
                always {
                    junit 'backend/test-reports/*.xml'
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'backend/htmlcov',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])
                }
            }
        }

        stage('Code Quality Gate') {
            parallel {
                stage('Linting') {
                    steps {
                        dir('backend') {
                            bat "${PIP} install flake8"
                            bat "${FLAKE8} --config=.flake8 --output-file=flake8-report.txt main.py utils.py hr_policy_data.py || exit 0"
                        }
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: 'backend/flake8-report.txt', allowEmptyArchive: true
                        }
                    }
                }
                stage('Security Scan') {
                    steps {
                        dir('backend') {
                            bat "${PIP} install bandit"
                            bat "${BANDIT} -r . --format xml --output bandit-report.xml || exit 0"
                        }
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: 'backend/bandit-report.xml', allowEmptyArchive: true
                        }
                    }
                }
            }
            post {
                always {
                    script {
                        // Check for high severity security issues
                        if (fileExists('backend/bandit-report.xml')) {
                            def xml = readFile('backend/bandit-report.xml')
                            if (xml.contains('severity="HIGH"')) {
                                currentBuild.result = 'UNSTABLE'
                                echo 'WARNING: Security scan found HIGH severity issues!'
                            }
                        }
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                dir('backend') {
                    script {
                        def imageTag = "${env.VERSION}-${env.GIT_COMMIT_SHORT}"
                        bat "docker build -t ${IMAGE_NAME}:latest -t ${IMAGE_NAME}:${VERSION} -t ${IMAGE_NAME}:${imageTag} ."
                        env.FULL_IMAGE_TAG = imageTag
                    }
                }
            }
        }

        stage('Deploy to Staging') {
            steps {
                script {
                    // Stop existing staging container gracefully
                    bat """
                        docker ps --filter "name=hr-policy-assistant-staging" --format "{{.ID}}" > temp_id.txt
                        if exist temp_id.txt (
                            for /f %%i in (temp_id.txt) do docker stop %%i
                            for /f %%i in (temp_id.txt) do docker rm %%i
                        )
                        del temp_id.txt 2>nul || exit 0
                    """
                    
                    // Deploy to staging
                    bat "docker run -d --name hr-policy-assistant-staging -p ${STAGING_PORT}:8000 --restart unless-stopped ${IMAGE_NAME}:latest"
                    
                    // Wait for staging to be ready
                    sleep(time: 10, unit: 'SECONDS')
                }
            }
        }

        stage('Staging Health Check') {
            steps {
                script {
                    def maxRetries = 5
                    def retryCount = 0
                    def healthCheckPassed = false
                    
                    while (retryCount < maxRetries && !healthCheckPassed) {
                        try {
                            def result = bat(
                                script: "curl -s -o nul -w \"%%{http_code}\" http://localhost:${STAGING_PORT}/",
                                returnStdout: true
                            ).trim()
                            
                            echo "Staging health check attempt ${retryCount + 1}: ${result}"
                            
                            if (result == '200') {
                                healthCheckPassed = true
                                echo "Staging deployment successful!"
                            } else {
                                retryCount++
                                if (retryCount < maxRetries) {
                                    sleep(time: 10, unit: 'SECONDS')
                                }
                            }
                        } catch (Exception e) {
                            retryCount++
                            echo "Health check failed: ${e.getMessage()}"
                            if (retryCount < maxRetries) {
                                sleep(time: 10, unit: 'SECONDS')
                            }
                        }
                    }
                    
                    if (!healthCheckPassed) {
                        error "Staging deployment failed after ${maxRetries} attempts"
                    }
                }
            }
        }

        stage('Release to Production') {
            when {
                anyOf {
                    branch 'main'
                    branch 'master'
                }
            }
            steps {
                script {
                    // Manual approval for production deployment
                    input message: 'Deploy to Production?', ok: 'Deploy',
                          submitterParameter: 'APPROVER'
                    
                    echo "Production deployment approved by: ${env.APPROVER}"
                }
                
                dir('backend') {
                    // Push to DockerHub
                    bat "echo %DOCKERHUB_CREDENTIALS_PSW% | docker login -u %DOCKERHUB_CREDENTIALS_USR% --password-stdin"
                    bat "docker push ${IMAGE_NAME}:latest"
                    bat "docker push ${IMAGE_NAME}:${VERSION}"
                    bat "docker push ${IMAGE_NAME}:${env.FULL_IMAGE_TAG}"
                    
                    // Deploy to production
                    script {
                        // Graceful shutdown of existing production container
                        bat """
                            docker ps --filter "name=hr-policy-assistant-prod" --format "{{.ID}}" > temp_prod_id.txt
                            if exist temp_prod_id.txt (
                                for /f %%i in (temp_prod_id.txt) do docker stop %%i
                                for /f %%i in (temp_prod_id.txt) do docker rm %%i
                            )
                            del temp_prod_id.txt 2>nul || exit 0
                        """
                        
                        bat "docker run -d --name hr-policy-assistant-prod -p ${PROD_PORT}:8000 --restart unless-stopped ${IMAGE_NAME}:latest"
                    }
                }
            }
        }

        stage('Production Health Check & Monitoring') {
            when {
                anyOf {
                    branch 'main'
                    branch 'master'
                }
            }
            steps {
                script {
                    def maxRetries = 10
                    def retryCount = 0
                    def healthCheckPassed = false
                    
                    // Wait for container to start
                    sleep(time: 15, unit: 'SECONDS')
                    
                    while (retryCount < maxRetries && !healthCheckPassed) {
                        try {
                            def result = bat(
                                script: "curl -s -o nul -w \"%%{http_code}\" http://localhost:${PROD_PORT}/",
                                returnStdout: true
                            ).trim()
                            
                            echo "Production health check attempt ${retryCount + 1}: Status ${result}"
                            
                            if (result == '200') {
                                healthCheckPassed = true
                                echo "Production deployment successful!"
                                
                                // Additional health checks
                                bat "curl -s http://localhost:${PROD_PORT}/health || echo 'Health endpoint not available'"
                                
                            } else {
                                retryCount++
                                if (retryCount < maxRetries) {
                                    sleep(time: 15, unit: 'SECONDS')
                                }
                            }
                        } catch (Exception e) {
                            retryCount++
                            echo "Production health check failed: ${e.getMessage()}"
                            if (retryCount < maxRetries) {
                                sleep(time: 15, unit: 'SECONDS')
                            }
                        }
                    }
                    
                    if (!healthCheckPassed) {
                        error "Production deployment failed after ${maxRetries} attempts"
                    }
                }
            }
        }
    }

    post {
        success {
            script {
                def message = """
                ✅ Pipeline SUCCESS for HR Policy Assistant
                Branch: ${env.BRANCH_NAME}
                Build: #${env.BUILD_NUMBER}
                Commit: ${env.GIT_COMMIT_SHORT}
                Image: ${IMAGE_NAME}:${VERSION}
                Staging: http://localhost:${STAGING_PORT}
                Production: http://localhost:${PROD_PORT}
                """
                echo message
                
                // You can add Slack/Teams notification here
                // slackSend(message: message, color: 'good')
            }
        }
        
        failure {
            script {
                def message = """
                ❌ Pipeline FAILED for HR Policy Assistant
                Branch: ${env.BRANCH_NAME}
                Build: #${env.BUILD_NUMBER}
                Stage: ${env.STAGE_NAME}
                Check: ${env.BUILD_URL}
                """
                echo message
                
                // Cleanup failed containers
                bat 'docker rm -f hr-policy-assistant-staging hr-policy-assistant-prod 2>nul || exit 0'
                
                // You can add Slack/Teams notification here
                // slackSend(message: message, color: 'danger')
            }
        }
        
        unstable {
            echo "⚠️ Pipeline completed with warnings (likely security issues found)"
        }
        
        always {
            // Archive important artifacts
            archiveArtifacts artifacts: 'backend/test-reports/*.xml,backend/*-report.*', allowEmptyArchive: true
            
            // Clean up Docker images to save space (keep last 3 builds)
            script {
                bat """
                    for /f "skip=3 tokens=*" %%i in ('docker images ${IMAGE_NAME} --format "{{.ID}}" ^| findstr /v latest') do docker rmi %%i 2>nul || exit 0
                """
            }
            
            cleanWs()
            echo "🧹 Workspace and old Docker images cleaned up"
        }
    }
}
