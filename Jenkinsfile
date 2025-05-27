pipeline {
    agent any

    environment {
        PYTHON = '"C:\\Users\\tuant\\AppData\\Local\\Programs\\Python\\Python313\\python.exe"'
        PIP = '"C:\\Users\\tuant\\AppData\\Local\\Programs\\Python\\Python313\\python.exe" -m pip'
        FLAKE8 = '"C:\\Users\\tuant\\AppData\\Local\\Programs\\Python\\Python313\\Scripts\\flake8.exe"'
        BANDIT = '"C:\\Users\\tuant\\AppData\\Local\\Programs\\Python\\Python313\\Scripts\\bandit.exe"'
        DOCKERHUB_USER = credentials('dockerhub-user')
        DOCKERHUB_PASS = credentials('dockerhub-pass')
        IMAGE_NAME = "tuahung248/hr-policy-assistant"
        VERSION = "${env.BUILD_NUMBER}"
    }

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '10'))
        ansiColor('xterm')
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
                    bat "${PYTHON} -m pytest --cov=."
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
                // Optionally, push results to SonarQube here if set up
            }
        }

        stage('Security Gate') {
            steps {
                dir('backend') {
                    bat "${PIP} install bandit"
                    bat "${BANDIT} -r . --format xml --output bandit-report.xml || exit 0"
                }
                // Archive bandit report
                archiveArtifacts artifacts: 'backend/bandit-report.xml', allowEmptyArchive: true
                // Fail build on high vulnerabilities
                script {
                    def xml = readFile('backend/bandit-report.xml')
                    if (xml.contains('severity="HIGH"')) {
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
                    // Remove old container if exists
                    bat 'docker rm -f hr-policy-assistant-staging || exit 0'
                    // Run new container on port 8000 for staging
                    bat 'docker run -d --name hr-policy-assistant-staging -p 8000:8000 %IMAGE_NAME%:latest'
                }
            }
        }

        stage('Release to Production') {
            steps {
                dir('backend') {
                    // Tag and push to DockerHub
                    bat 'docker login -u %DOCKERHUB_USER% -p %DOCKERHUB_PASS%'
                    bat 'docker push %IMAGE_NAME%:latest'
                    bat 'docker push %IMAGE_NAME%:%VERSION%'
                    // Remove old prod container if exists
                    bat 'docker rm -f hr-policy-assistant-prod || exit 0'
                    // Run prod container on different port
                    bat 'docker run -d --name hr-policy-assistant-prod -p 8001:8000 %IMAGE_NAME%:latest'
                }
            }
        }

        stage('Monitoring and Alerts') {
            steps {
                script {
                    // Simulate monitoring check: HTTP health probe and log response
                    def result = bat(script: 'curl -s -o nul -w "%{http_code}" http://localhost:8001/', returnStdout: true).trim()
                    if (result != '200') {
                        mail to: 'yourteam@deakin.edu.au',
                             subject: "Production App Health Check Failed",
                             body: "Health check failed with status: ${result}"
                        error "App is DOWN! Health check failed."
                    }
                }
            }
        }
    }

    post {
        success {
            echo "Pipeline completed successfully! All quality gates and deployment stages passed."
        }
        failure {
            echo "Pipeline failed. Please check above logs and reports."
            // Optionally, send failure notification
        }
        always {
            cleanWs()
        }
    }
}
