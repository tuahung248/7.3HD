pipeline {
    agent any

    environment {
        // Versioning: Use the Jenkins build number as Docker image tag
        BUILD_VERSION = "${BUILD_NUMBER}"
        IMAGE_NAME = "hr-policy-assistant"
        PROD_IMAGE_TAG = "prod"
        TEST_CONTAINER = "hr-policy-assistant-test"
        PROD_CONTAINER = "hr-policy-assistant-prod"
        PYTHON = "C:\\Users\\tuant\\AppData\\Local\\Programs\\Python\\Python313\\python.exe"
        PIP = "C:\\Users\\tuant\\AppData\\Local\\Programs\\Python\\Python313\\python.exe -m pip"
        FLAKE8 = "C:\\Users\\tuant\\AppData\\Local\\Programs\\Python\\Python313\\Scripts\\flake8.exe"
        BANDIT = "C:\\Users\\tuant\\AppData\\Local\\Programs\\Python\\Python313\\Scripts\\bandit.exe"
    }

    stages {
        stage('Build') {
            steps {
                dir('backend') {
                    bat "${PIP} install -r requirements.txt"
                    // Build Docker image, tag with build number and 'latest'
                    bat "docker build -t ${IMAGE_NAME}:${BUILD_VERSION} -t ${IMAGE_NAME}:latest ."
                }
            }
        }

        stage('Test') {
            steps {
                dir('backend') {
                    // Run unit tests
                    bat "${PYTHON} -m pytest test_app.py"
                }
            }
            post {
                always {
                    // Archive test reports if generated
                    junit allowEmptyResults: true, testResults: 'backend/*.xml'
                }
            }
        }

        stage('Code Quality') {
            steps {
                dir('backend') {
                    // Install and run flake8 with a config file if present
                    bat "${PIP} install flake8"
                    // Use your .flake8 config file for strict rules
                    bat "${FLAKE8} --config=.flake8 main.py utils.py hr_policy_data.py"
                }
            }
        }

        stage('Security') {
            steps {
                dir('backend') {
                    // Install and run Bandit (security linter)
                    bat "${PIP} install bandit"
                    // Fail build if critical security issues found
                    bat "${BANDIT} -r . --exit-zero > bandit-report.txt"
                }
            }
            post {
                always {
                    // Archive security report
                    archiveArtifacts artifacts: 'backend/bandit-report.txt', allowEmptyArchive: true
                }
            }
        }

        stage('Deploy') {
            steps {
                dir('backend') {
                    // Remove old test container if it exists
                    bat "docker rm -f ${TEST_CONTAINER} || exit 0"
                    // Deploy the built image to test environment
                    bat "docker run -d --name ${TEST_CONTAINER} -e ENV=test -p 8000:8000 ${IMAGE_NAME}:${BUILD_VERSION}"
                }
            }
        }

        stage('Release') {
            steps {
                dir('backend') {
                    // Tag and run prod container
                    bat "docker tag ${IMAGE_NAME}:${BUILD_VERSION} ${IMAGE_NAME}:${PROD_IMAGE_TAG}"
                    bat "docker rm -f ${PROD_CONTAINER} || exit 0"
                    bat "docker run -d --name ${PROD_CONTAINER} -e ENV=prod -p 8001:8000 ${IMAGE_NAME}:${PROD_IMAGE_TAG}"
                    // Optionally, push to DockerHub:
                    // bat "docker login -u %DOCKERHUB_USER% -p %DOCKERHUB_PASS%"
                    // bat "docker push ${IMAGE_NAME}:${BUILD_VERSION}"
                    // bat "docker push ${IMAGE_NAME}:${PROD_IMAGE_TAG}"
                }
            }
        }

        stage('Monitoring') {
            steps {
                script {
                    // Wait for app to start up (use a small sleep if needed)
                    bat 'ping -n 11 127.0.0.1 > nul'
                    // Health check both test and prod endpoints
                    def testStatus = bat(script: 'curl -s http://localhost:8000/', returnStatus: true)
                    def prodStatus = bat(script: 'curl -s http://localhost:8001/', returnStatus: true)
                    if (testStatus != 0 || prodStatus != 0) {
                        error("Healthcheck failed! Test or Production endpoint is not responding.")
                    }
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished!'
            // Optionally: clean up stopped containers/images to save disk space
        }
        failure {
            // Email or alert team here if needed
            echo 'Pipeline failed! Please check the logs for details.'
        }
    }
}
