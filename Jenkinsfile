pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                dir('backend') {
                    sh 'pip install -r requirements.txt'
                }
            }
        }
        stage('Test') {
            steps {
                dir('backend') {
                    sh 'pytest test_app.py'
                }
            }
        }
        stage('Code Quality') {
            steps {
                dir('backend') {
                    sh 'pip install flake8'
                    sh 'flake8 main.py utils.py hr_policy_data.py'
                }
            }
        }
        stage('Docker Build') {
            steps {
                dir('backend') {
                    sh 'docker build -t hr-policy-assistant .'
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished!'
        }
    }
}
