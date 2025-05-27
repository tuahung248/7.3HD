pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                dir('backend') {
                    bat '"C:\\Users\\tuant\\AppData\\Local\\Programs\\Python\\Python313\\python.exe" -m pip install -r requirements.txt'
                    bat 'docker build -t hr-policy-assistant .'
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
        stage('Security') {
            steps {
                dir('backend') {
                    bat '"C:\\Users\\tuant\\AppData\\Local\\Programs\\Python\\Python313\\python.exe" -m pip install bandit'
                    bat '"C:\\Users\\tuant\\AppData\\Local\\Programs\\Python\\Python313\\Scripts\\bandit.exe" -r . --skip B101'
                }
            }
        }
        stage('Deploy') {
            steps {
                dir('backend') {
                    bat 'docker rm -f hr-policy-assistant-test || exit 0'
                    bat 'docker run -d --name hr-policy-assistant-test -p 8000:8000 hr-policy-assistant'
                }
            }
        }
        stage('Release') {
            steps {
                dir('backend') {
                    bat 'docker tag hr-policy-assistant hr-policy-assistant:prod'
                    bat 'docker rm -f hr-policy-assistant-prod || exit 0'
                    bat 'docker run -d --name hr-policy-assistant-prod -p 8001:8000 hr-policy-assistant:prod'
                }
            }
        }
        stage('Monitoring') {
            steps {
                bat 'curl http://localhost:8001/docs || echo "App is down!"'
                // Or use PowerShell for more advanced checks and logs
            }
        }
    }
    post {
        always {
            echo 'Pipeline finished!'
        }
    }
}
