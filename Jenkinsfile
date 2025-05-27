pipeline {
    agent any

    stages {
        stage('Check Python') {
            steps {
                bat '"C:\\Users\\tuant\\AppData\\Local\\Programs\\Python\\Python313\\python.exe" --version'
                bat '"C:\\Users\\tuant\\AppData\\Local\\Programs\\Python\\Python313\\python.exe" -m pip --version'
                bat 'echo %PATH%'
                bat 'docker --version'
                bat 'docker info'
            }
        }
        stage('Build') {
            steps {
                dir('backend') {
                    bat '"C:\\Users\\tuant\\AppData\\Local\\Programs\\Python\\Python313\\python.exe" -m pip install -r requirements.txt'
                }
            }
        }
        stage('Test') {
            steps {
                dir('backend') {
                    bat '"C:\\Users\\tuant\\AppData\\Local\\Programs\\Python\\Python313\\python.exe" -m pytest test_app.py'
                }
            }
        }
        stage('Code Quality') {
            steps {
                dir('backend') {
                    bat '"C:\\Users\\tuant\\AppData\\Local\\Programs\\Python\\Python313\\python.exe" -m pip install flake8'
                    bat '"C:\\Users\\tuant\\AppData\\Local\\Programs\\Python\\Python313\\Scripts\\flake8.exe" --ignore=E501,E302 main.py utils.py hr_policy_data.py'
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
