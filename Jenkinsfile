pipeline {
    agent any

    stages {
        stage('Check Python') {
            steps {
                bat 'where python'
                bat 'where pip'
                bat 'python --version'
                bat 'pip --version'
                bat 'echo %PATH%'
            }
        }
        stage('Build') {
            steps {
                dir('backend') {
                    bat 'python -m pip install -r requirements.txt'
                }
            }
        }
        stage('Test') {
            steps {
                dir('backend') {
                    bat 'pytest test_app.py'
                }
            }
        }
        stage('Code Quality') {
            steps {
                dir('backend') {
                    bat 'pip install flake8'
                    bat 'flake8 main.py utils.py hr_policy_data.py'
                }
            }
        }
        stage('Docker Build') {
            steps {
                dir('backend') {
                    bat 'docker build -t hr-policy-assistant .'
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
