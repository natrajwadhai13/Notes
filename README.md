### 🔁 Que 1) What is the difference between Continuous Integration, Continuous Delivery, and Continuous Deployment? Can you explain with an example from your past project?
### ✅ **Answer**
**Continuous Integration (CI)** is the process where developers frequently merge code changes into the main branch. This triggers automated builds and tests to ensure nothing is broken.

**Continuous Delivery (CD)** extends CI by making sure that the code is always in a deployable state. After passing tests, it is pushed to staging or pre-prod automatically, but manual approval is required for production.

**Continuous Deployment** goes a step further — even the production deployment is automated, with no manual approval.

**In my current company**, we use GitLab CI/CD pipelines. Developers push code to feature branches, and a pipeline is triggered automatically for build, test, and deploy. We follow a multi-stage environment strategy:

Code is deployed to Test1, then Test2 using Ansible.

Once verified, we promote it to Production.

This ensures smooth CI/CD flow and stable releases.

---

### 🔁 Que 2) Can you explain how you have written or used a GitLab CI/CD pipeline file (.gitlab-ci.yml)? Mention any important stages, variables, or jobs used.
### ✅ **Answer**
Yes, I’ve worked on writing and maintaining .gitlab-ci.yml files to automate build, test, and deployment workflows.

Here's a high-level structure of what we use:

```yaml

stages:
  - build
  - test
  - deploy

variables:
  APP_NAME: my-node-app
  DEPLOY_ENV: staging

build_job:
  stage: build
  script:
    - echo "Building $APP_NAME"
    - npm install
    - npm run build

test_job:
  stage: test
  script:
    - npm test

deploy_job:
  stage: deploy
  only:
    - master
  script:
    - ansible-playbook deploy.yml -i inventory/$DEPLOY_ENV

```
---

### 🔁 Que-3 Can you explain how Ansible is used in your pipeline for deployment?

What kind of playbooks did you write or use?

What was being deployed — Docker containers, packages, Node apps, etc.?

How was inventory handled?

### ✅ **Answer**
How We Use Ansible for Deployment

In my company, I manage deployment automation for more than **18+ applications** using **Ansible**.

We follow a clear structure:

 1. **Inventory File:**
We maintain a dynamic or static inventory file where we define:

* Application name as groups (e.g., `[webapp1]`, `[dbapp1]`)
* Server IPs or hostnames
* Role tags like `web`, `app`, or `db`

 **Example:**
 
 ```ini
[web]
192.168.10.5 ansible_user=ubuntu

 [db]
192.168.10.6 ansible_user=ubuntu
```

2. **Playbooks:**
 For each application, we create separate playbooks that define tasks like:

 * Pulling code from Git repo
 * Installing dependencies
 * Managing Docker containers (if used)
 * Copying environment variables
 * Restarting services (like `nginx`, `pm2`, `node`, etc.)

 **Example snippet:**

 ```yaml
 - name: Deploy web app
   hosts: web
   tasks:
     - name: Clone repo
       git:
         repo: 'https://gitlab.com/myorg/myapp.git'
         dest: /var/www/myapp
     - name: Install npm packages
       command: npm install
       args:
         chdir: /var/www/myapp
 ```

 3. **Integration with GitLab CI/CD:**

 * The `deploy` stage of the pipeline runs this playbook using:

   ```bash
   ansible-playbook -i inventory/staging.ini deploy.yml
   ```
 * We pass environment variables from GitLab to Ansible using `extra_vars`.

---

### 💡 Extra Points to Mention (if interviewer goes deeper)

* Handled **idempotency** with Ansible modules (`copy`, `service`, `template`)
* Used **Ansible Vault** to store secrets
* Organized roles using `ansible-galaxy init`
* Used dynamic inventories for AWS (optional if applicable)
---
**Kubernetes**
### 🔁 **Que 4 **Can you explain the basic components of a Kubernetes cluster (Control Plane & Node)? Also, describe a scenario where you deployed an app on Kubernetes — how did you write your manifest or Helm chart?

### ✅ **Answer**
