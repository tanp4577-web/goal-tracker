pipeline {
    agent any

    environment {
        DOCKERHUB_USER = 'tanp77'
        IMAGE_NAME     = 'goal-tracker'
        KUBECONFIG     = 'C:\\Users\\pondh\\.kube\\config'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code from SCM...'
                checkout scm
                echo "BUILD_NUMBER : ${env.BUILD_NUMBER}"
                echo "JOB_NAME     : ${env.JOB_NAME}"
                echo "WORKSPACE    : ${env.WORKSPACE}"
            }
        }

        stage('Install Dependencies') {
            steps {
                script {
                    for (v in ['v1', 'v2', 'v3']) {
                        dir(v) {
                            bat 'python -m venv venv'
                            bat 'call venv\\Scripts\\activate && python -m pip install --upgrade pip && pip install -r requirements.txt pytest'
                        }
                    }
                }
            }
        }

        stage('Run Unit Tests') {
            steps {
                script {
                    for (v in ['v1', 'v2', 'v3']) {
                        dir(v) {
                            bat 'call venv\\Scripts\\activate && pytest -v --junitxml=test-results.xml'
                        }
                    }
                }
            }
        }

        stage('Build Docker Images') {
            steps {
                script {
                    for (v in ['v1', 'v2', 'v3']) {
                        bat "docker build -t %DOCKERHUB_USER%/%IMAGE_NAME%:${v} ${v}"
                    }
                }
            }
        }

        stage('Push to DockerHub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-push',
                                                  usernameVariable: 'DH_USER',
                                                  passwordVariable: 'DH_PASS')]) {
                    bat 'echo %DH_PASS%| docker login -u %DH_USER% --password-stdin'
                    script {
                        for (v in ['v1', 'v2', 'v3']) {
                            bat "docker push %DOCKERHUB_USER%/%IMAGE_NAME%:${v}"
                        }
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                bat 'kubectl apply -f k8s/'
                bat 'kubectl get deployments'
                bat 'kubectl get services'
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'v*/test-results.xml', fingerprint: true, allowEmptyArchive: true
        }
        success {
            echo 'Done! Open http://localhost:8081 (v1), http://localhost:8082 (v2), http://localhost:8083 (v3)'
        }
    }
}
