# Goal Tracker - Agile Development Process and DevOps (24MIS0318)

| Version | New feature | Port |
|---|---|---|
| v1 | Add Goal | 8081 |
| v2 | Update Goal | 8082 |
| v3 | View Progress | 8083 |

Folders: v1/ v2/ v3/ (app.py, templates/index.html, test_app.py, requirements.txt, Dockerfile), k8s/ (deployment-v1.yml, service-v1.yml, and the same for v2 and v3), Jenkinsfile.
The Jenkinsfile and Kubernetes deployments are configured to use the Docker Hub account `tanp77`.
The Jenkins agent must run as the Windows user `pondh` or have access to the kubeconfig at `C:\Users\pondh\.kube\config`.
Before running Jenkins, log in to Docker Hub as `tanp77` from the same Windows account that runs the Jenkins agent. The pipeline uses that account's Docker CLI credentials when pushing the images.

Each version stores its goals in its own SQLite database. For direct Flask runs, open three Command Prompt windows and start one version in each:

```cmd
cd /d "C:\Users\pondh\Downloads\AgileProject\goal-tracker\v1"
call venv\Scripts\activate
set PORT=8081
python app.py
```

Use the same commands in the other two windows, changing the folder to `v2` and `v3`, and setting `PORT` to `8082` and `8083`. Each version stores its database under its own `instance/` folder, so pressing Ctrl+C stops only that version; its saved goals remain when you start it again. Do not delete its `instance/` folder.

Kubernetes mounts a separate PersistentVolumeClaim for each version at `/data`, so goals remain available after a pod restart. After updating the code, rebuild and push the images, then apply the Kubernetes files from the project root with `kubectl apply -f k8s\`.
