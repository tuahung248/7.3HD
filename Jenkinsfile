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
    }

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                dir('backend') {
                    bat "${PIP} install --upgrade pip"
                    bat "${PIP} install -r requirements.txt"
                }
            }
        }

        stage('Unit + Integration Test') {
            steps {
                dir('backend') {
                    bat 'if not exist test-reports mkdir test-reports'
                    bat "${PYTHON} -m pytest --junitxml=test-reports/results.xml"
                }
                junit 'backend/test-reports/*.xml'
            }
        }

        stage('Code Quality Gate') {
            steps {
                dir('backend') {
                    bat "${PIP} install flake8"
                    bat "${FLAKE8} --config=.flake8 main.py utils.py hr_policy_data.py"
                }
            }
        }

        stage('Security Gate') {
            steps {
                dir('backend') {
                    bat "${PIP} install bandit"
                    bat "${BANDIT} -r . --format xml --output bandit-report.xml || exit 0"
                }
                archiveArtifacts artifacts: 'backend/bandit-report.xml', allowEmptyArchive: true
                script {
                    def xml = readFile('backend/bandit-report.xml')
                    if (xml.contains('severity=\"HIGH\"')) {
                        error('Security scan found HIGH severity issues!')
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                dir('backend') {
                    bat 'docker build -t %IMAGE_NAME%:latest -t %IMAGE_NAME%:%VERSION% .'
                }
            }
        }

        stage('Deploy to Staging') {
            steps {
                dir('backend') {
                    // Remove any container using port 8000 (Windows PowerShell version)
                    bat '''
                        FOR /F "tokens=*" %%i IN ('docker ps --filter "publish=8000" --format "{{.ID}}"') DO docker rm -f %%i
                    '''
                    // Run new container on port 8000 for staging
                    bat 'docker run -d --name hr-policy-assistant-staging -p 8000:8000 %IMAGE_NAME%:latest'
                }
            }
        }

        stage('Release to Production') {
            steps {
                dir('backend') {
                    // Secure DockerHub login using Jenkins credentials
                    bat 'docker login -u %DOCKERHUB_CREDENTIALS_USR% -p %DOCKERHUB_CREDENTIALS_PSW%'
                    bat 'docker push %IMAGE_NAME%:latest'
                    bat 'docker push %IMAGE_NAME%:%VERSION%'
                    bat 'docker rm -f hr-policy-assistant-prod || exit 0'
                    bat 'docker run -d --name hr-policy-assistant-prod -p 8001:8000 %IMAGE_NAME%:latest'
                }
            }
        }
        stage('Monitoring and Alerts') {
            steps {
                script {
                    bat 'where curl'
                    bat 'curl --version'
                    bat 'curl http://localhost:8001/'
                    def result = bat(
                        script: 'curl -s -o nul -w "%{http_code}" http://localhost:8001/',
                        returnStdout: true
                    ).trim()
                    echo "Health check result: ${result}"
                    if (result != '200') {
                        error "App is DOWN! Health check failed with status: ${result}"
                    }
                }
            }
        }
    } // <---- End of stages

    post {
        success {
            echo "Pipeline completed successfully! All quality gates and deployment stages passed."
        }
        failure {
            echo "Pipeline failed. Please check above logs and reports."
        }
        always {
            cleanWs()
            echo "Workspace cleaned up after build."
        }
    }
}
