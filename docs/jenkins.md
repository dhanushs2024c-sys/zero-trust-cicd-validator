# Jenkins Pipeline Integration Guide

## Overview

The Zero-Trust CI/CD Pipeline Validator integrates into Jenkins pipelines as a mandatory pre-build stage. If validation fails, Jenkins aborts the pipeline, preventing subsequent compilation and deployment stages from executing.

---

## 1. Declarative Pipeline Example

A production-ready `Jenkinsfile` is provided in `integrations/jenkins/Jenkinsfile`:

```groovy
pipeline {
    agent any

    environment {
        ZT_CONFIG_DIR = "${WORKSPACE}/configs"
        PYTHONUNBUFFERED = "1"
    }

    stages {
        stage('Checkout') {
            steps {
                // Ensure full commit history is fetched for signature checking
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/main']],
                    extensions: [[$class: 'CloneOption', depth: 0, noTags: false, shallow: false]],
                    userRemoteConfigs: scm.userRemoteConfigs
                ])
            }
        }

        stage('Zero-Trust Validation Gate') {
            steps {
                echo '========================================================='
                echo 'STAGE 1: CRYPTOGRAPHIC PRE-BUILD VERIFICATION'
                echo '========================================================='
                sh '''
                    python3 -m pip install -q -r backend/requirements.txt
                    python3 -m validator.cli validate --path "${WORKSPACE}"
                '''
                // If python -m validator.cli exits with 1, Jenkins marks stage as FAILED
            }
        }

        stage('Build & Package') {
            // Jenkins will skip this stage entirely if Stage 1 fails
            steps {
                echo '========================================================='
                echo 'STAGE 2: BUILD AUTHORIZED BY ZERO-TRUST GATE'
                echo '========================================================='
                sh './build.sh'
            }
        }
    }

    post {
        failure {
            echo 'CRITICAL: Build aborted due to Zero-Trust security violation.'
        }
        success {
            echo 'Build completed successfully after full Zero-Trust verification.'
        }
    }
}
```

---

## 2. Pipeline Behavior on Security Failure

When a tampered dependency, unsigned commit, or compromised runner file is detected:
1. `zt-validator validate` outputs the failure reason and returns exit code `1`.
2. The `sh` step in Jenkins throws a script execution failure.
3. Jenkins marks the **Zero-Trust Validation Gate** stage as `FAILED` (red).
4. The **Build & Package** stage is never reached.
5. Post-failure alerts are triggered.
