# Group Management System
![Banner](readme/banner.png)

Form groups and submit project proposals for your software engineering group project, all in one platform.

## Features

📕 __Students__

- 🚩 Create groups

- ⚙ Manage group members
- ✉ Apply to join groups
- 📝 Edit & submit project proposals

📚 __Administrators__

- ⏰ Set deadlines
- ✏ Import students
- 🚧 Set group size limits
- 🔍 View reports (grouping/proposal status of students and groups)
- 🎟 Allocate groups for ungrouped students
- ⭕ Approve/Reject proposals
- 📦 Archive the current semester & start a new one

💡 __Everyone__

- 💬 Comment on the proposal
- ⭐ Add groups to favorite
- 👤 Edit bio
- 🔑 Change password

📋 __TODO__

- 🖼 Showcase project results
- 🗺 Explore projects of archived semesters
- 🔔 Receive & view notifications

## Important time frames

- 🚀 At the start of the semester

  This is the time for the administrators to set the deadlines and group size limits of the semester in the `Semester Tools`. Students can be imported by clicking the `Import Students` button and uploading a file in the same format as the [sample student list](docs/sample%20student%20list.csv). The initial passwords of the students can be downloaded by clicking the `Download Student Credentials` button. Students can change their passwords once they've logged in using the initial passwords.

- 📢 Before the grouping deadline

  This is the time for the students to form groups. A student can either choose to create a group or apply to a group. The grouping status of each student can be viewed by the administrators by downloading the `student report` on the `Reports` page.

- 💭 Before the proposal deadline (After the grouping deadline)

  This is the time for the students to work on and refine their project proposals. Once a group is satisfied with its proposal, the group owner can submit it. Administrators can allocate groups for the ungrouped students. They can also visit different groups and comment on their current proposals.

- 🎯 After the proposal deadline

  This is the time for the administrators to review the submitted proposals. For each submitted proposal, they can either accept it or reject it. If the proposal is rejected, the group will be given the chance to edit and resubmit the proposal without penalties. However, if a group did not submit their proposal, or they made a late submission, their late status will be shown on their group's page and also on the `group report` available to the administrators.
  
- 🏁 After the semester

  This is the time for the administrators to archive the semester in the `Semester Tools` and perhaps plan for the new semester.

## Deployment instruction

The project is docker ready, using [docker-compose](https://docs.docker.com/compose/) for deployment by default. 

Dockerfiles are located at `src/docker/`.

The project deployment is tested under Ubuntu 20.04, and the use of a Linux server is recommended. 

### Install docker on the server

Install docker on the production server by following the official guide [Get Docker](https://docs.docker.com/get-docker/).

### Method 1: Deploy with continuous integration (Recommended)

The project uses GitHub Actions for continuous integration

#### Add secrets

On the GitHub repository page, navigate to Settings > Secrets

Add the following secrets:

|name|content|example|
|---|---|---|
|ADMIN_USERNAME|admin user name, must be in email format|superuser@gms.com|
|ADMIN_PASSWORD|admin initial password|foo|
|MYSQL_DATABASE|database name|gms|
|MYSQL_USER|mysql username|gms|
|MYSQL_PASSWORD|mysql user password|buz|
|MYSQL_ROOT_PASSWORD|mysql root password|bar|
|JWT_PUBKEY|public key for JWT|-----BEGIN PUBLIC KEY-----<br>...<br>-----END PUBLIC KEY-----|
|JWT_KEY|private key for JWT|-----BEGIN RSA PRIVATE KEY-----<br>...<br>-----END RSA PRIVATE KEY-----|
|DOMAIN_CERT_FULLCHAIN|TLS certificate for the site|-----BEGIN CERTIFICATE-----<br>...<br>-----END CERTIFICATE-----|
|DOMAIN_CERT_KEY|TLS key file|-----BEGIN EC PARAMETERS-----<br>...<br>-----END EC PARAMETERS-----<br>-----BEGIN EC PRIVATE KEY-----<br>...<br>-----END EC PRIVATE KEY-----|
|SSH_KEY|private key of the remote host|-----BEGIN RSA PRIVATE KEY-----<br>...<br>-----END RSA PRIVATE KEY-----|
|SSH_USER_HOST|username and hostname for ssh connection|alice@gms.example.com|

#### Run CI job

Navigate to Actions > Workflows > CI, click run workflow. 

### Method 2: Deploy manually

#### Generate JWT keypair

Place the JWT keypair at `src/backend/config/jwt/` and overwrite the example file.

The default algorithm for the key is RS256, and can be generated by the following commands:

```sh
ssh-keygen -t rsa -b 4096 -m PEM -f jwt.key
# Don't add passphrase
openssl rsa -in jwt.key -pubout -outform PEM -out jwt.key.pub
```

For security reason, do NOT use the example keypair in the production environment.

#### Modify backend configuration

Backend configuration file: `src/backend/config/app_config.yml`

Please refer to the inline comment for explanations

##### Setup MySQL

In `src/docker/config/docker-compose.yml`:
* Set the value of `MYSQL_ROOT_PASSWORD` `MYSQL_USER` `MYSQL_PASSWORD` `MYSQL_DATABASE`


In `src/backend/config/app_config.yml`:
* Set the value of `mysql_host` to "mysql", which is the container name set in `docker-compose.yml`
* Set the value of `mysql_database`, `mysql_user`, `mysql_password` to the same value as the ones in `docker-compose.yml`


#### Prepare TLS certification for HTTPS

Place the following files:

* Public cert(NGINX fullchain): `src/docker/config/cert/fullchain.cer`
* Private key: `src/docker/config/cert/key.pem`

#### Modify nginx configuration (optional)

Configuration file: `src/docker/config/nginx.conf`

#### Compile the webpage

##### Install NodeJS

Follow the official guide [Download node](https://nodejs.org/en/download/)

##### Install yarn

Follow the official guide [Yarn installation](https://classic.yarnpkg.com/en/docs/install/#debian-stable)

##### Install node modules and build

With `src/web` as working directory:

```sh
yarn install
yarn build
```

The static web file should be outputted to `src/web/dist`

#### Deploy with docker-compose

##### Install docker(optional) and docker-compose

Install docker on the local machine by following the official guide [Get Docker](https://docs.docker.com/get-docker/).
Install docker-compose on the local machine by following the official guide [Install Compose](https://docs.docker.com/compose/install/)

##### Setup remote context for docker-compose

```sh
docker context create remote ‐‐docker "host=ssh://production_server"
```

Confirm settings by using `docker ‐‐context remote ps`

##### Run container on remote

Run in foreground
```sh
docker-compose --context remote up
```

Run with daemon

```sh
docker-compose --context remote up -d
```

To shut down the service
```sh
docker-compose --context remote down
```

##### Update containers

Rebuild all image

```sh
docker-compose --context remote build
```

Rebuild image of specific service

```sh
docker-compose --context remote build <service>
```

Rebuild and run

```sh
docker-compose --context remote up --force-recreate --build -d
```

Remove unused images

```sh
docker --context remote image prune -a
```

##### Notes on possible docker-compose problems

###### docker-compose not respect ~/.ssh/config

Use ssh-agent login as a workaround
```sh
# In case you get the error 'Could not open a connection to your authentication agent.'
eval "$(ssh-agent)"

ssh-add -k /path/to/server/keyfile
docker context create remote --docker "host=ssh://user@hostname:port"
```

###### ERROR: Context 'remote' not found

switch context back and forth:

```sh
docker use context remote
docker use context default
```

###### docker-compose over SSH raises ChannelException(2, 'Connect failed')

In `/etc/ssh/sshd_config` of the docker host, set `MaxSessions` to 30

###### docker insanely resource usage when publishing the port range

In `/etc/docker/daemon.json` of the docker host, add `"userland-proxy": false`

###### docker-compose raises ssh: /tmp/_MEImZgOCk/libcrypto.so.1.1: version `OPENSSL_1_1_1' not found

```shell
export COMPOSE_PARAMIKO_SSH=1
```

###### Deploy with docker-compose on a host without docker-cli

```shell
export COMPOSE_DOCKER_CLI_BUILD=0
```
