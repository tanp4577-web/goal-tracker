# Goal Tracker - Agile Development Process and DevOps (24MIS0318)

| Version | New feature | Port |
|---|---|---|
| v1 | Add Goal | 8081 |
| v2 | Update Goal | 8082 |
| v3 | View Progress | 8083 |

Folders: v1/ v2/ v3/ (app.py, templates/index.html, test_app.py, requirements.txt, Dockerfile), k8s/ (deployment-v1.yml, service-v1.yml, and the same for v2 and v3), Jenkinsfile.
The Jenkinsfile and Kubernetes deployments are configured to use the Docker Hub account `tanp77`.
The Jenkins agent must run as the Windows user `pondh` or have access to the kubeconfig at `C:\Users\pondh\.kube\config`.
In Jenkins, configure a Username with password credential with ID `dockerhub-push`, username `tanp77`, and a Docker Hub access token with Read & Write permission.
