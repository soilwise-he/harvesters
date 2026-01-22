# Harvester tasks via Gitlab CI/CD

This folder contains a number of CI/CD tasks for Gitlab.
They are referenced from a central [.gitlab-ci.yml](../gitlab-ci.yaml) in root folder
In order to trigger a workflow, a variable 'PROJECT' needs to be available. 
You can specify the variable when triggering the pipeline manually.

For database connection details (and other relevant parameters, see the harvester readme), the CI/CD variables of Gitlab are used.
The dev branch uses different connection details then the main branch.

## RUN CI/CD at a schedule

Define a `Pipeline schedule` in Gitlab to trigger the task at a schedule, 
make sure to select the relevant branch and PROJECT variable.

