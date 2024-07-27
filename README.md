# Build and deploy

Command to build the application. PLease remeber to change the project name and application name

```
gcloud builds submit --tag gcr.io/wayne-430722/wayne-vl-analyst  --project=wayne-430722
```

Command to deploy the application

```
gcloud run deploy --image gcr.io/wayne-430722/wayne-vl-analyst --platform managed  --project=wayne-430722 --allow-unauthenticated
```
