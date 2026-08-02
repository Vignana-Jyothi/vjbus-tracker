# vj-servers
Code place for all Vignana Jyothi campus application servers (frontend &amp; backend)

# Folder Structure

Frontend (Workstation1)
  - fe1-server  : React application with Google/Github OAuth login
  - fe2-server  : Python application with EduPrime 

Backend  (Workstation2)
  - be1-server  : Express with Mongodb
  - be2-server  : Python (FastAPI) with MySQL
  - be3-server  : Python (Flask) with NoSQL

  - Databases
    - MongoDB
    - MySQL
    - SQLite

# Servers

## Google SSO Backend

## EduPrime SSO Backend
 Port 10.45.30.251:5001
 Speaks to  https://automation.vnrvjiet.ac.in/eduprime3sandbox/api/Auth/Validate
 APIs supported
 - post : /auth/eduprime 
    Request  {(username, password), (header: APIKey)} 
    Response {username, eduprimeToken}

## React & Express App
 Web Port : 3100

 Backend  : 5000
  post : /register

 Database : mongodb://10.45.30.252:27017

## Flutter Web App 
 Web port : 44183
 Speaks to backend: https://automation.vnrvjiet.ac.in/eduprime3sandbox/api/Auth/Validate

 ## HallBooking App
 Web port : 4000
 
 ## Minor SSO based Apps

 App1 : 3001  (frotend/frontend-python-flask/eduprime_sso_app1) 
 App2 : 3002  (frotend/frontend-python-flask/eduprime_sso_app2)

## Super App

Web port: 3003 (frontend/fe1)

# One time setup for every user on the server

Login to your user account. 
Run ssh-keygen to generate ssh-key
Save the key in https://github.com/settings/keys 

### Git initialisation 

  git config --global user.email "you@example.com"
  git config --global user.name "Your Name"


Merge remote changes & keep history    `git pull --no-rebase`
Rebase local commits on latest remote    `git pull --rebase`
Only update if no conflicts exist    `git pull --ff-only`
Discard local changes & force sync    `git reset --hard origin/main`

## Debugging

### NGINX

sudo systemctl restart nginx

sudo systemctl status nginx
sudo systemctl start nginx

sudo journalctl -xe
sudo tail -f /var/log/nginx/error.log


### Tools

#### Start a server instantly. 

python -m http.server 30015173


#### Useful git commands
git fetch origin
git pull --rebase origin main


#### Helpful utility commands
sudo rm -f /etc/nginx/.nginx.conf.swp
ps aux | grep nginx.conf
sudo kill -9 140019




BE-3:
one time: 
npm install express express-async-handler
to start : node server

FE-3:
one time :
npm install

to run : npm run dev

if any port is running on 3000 it fails as the backend allows only port 3000.

Super App Backend is Running on PORT 5000
and 
Eduprime Authentication is running on PORT 5001
and all the Other Child Apps are running on 6000 series(per application 10 ports)


Server1 : 103.248.208.119
Server2 : 10.45.8.187

| Application       | Frontend           | Backend           | Database        | Public URL |
|------------------|-------------------|------------------|----------------|----------------|
| SSO (Eduprime)  | N/A               |  5001  ✅      | MongoDB        |       N/a         |
| Campus          | 3000  ✅          |  5000  ✅        | PostgreSQL     |       campus     
| Complaints      | 3101              |  6101  ✅        | Cloud         |       complaints    | 
| DPD             | 3102              |  6102          | MySQL          |       bus         |
| ----            | 3103              |                |            |           | 
| BusTracker      | 3104              |  6104          | MySQL          |       bus         |
| UnDoubt         | 3108              |  6040          | Cloud          |       undoubt     |
| Wall            | 3105  ✅          |  N/A           | N/A            |       wall        |
| Navi            | 3107  ✅          |  N/A           | N/A            |       navi        |
| Activity        | 3106              |  6106          | MongoDB(local) |       activity    |
| EasyFind        | 3109 <br> 3110    |  6109          | MongoDB(local) |       easyfind   |
| Bandiwala       | 3111              | 6111           | MongoDB (ext)  |     bandiwala  |


## Github user management 

Remove old agents
ssh-add -D

Add new agent head_iie
ssh-add ~/.ssh/head_iie

git remote set-url origin git@github.com:head-iie-vnr/vj-servers.git


## Developer Tips

### use tmux

Open terminal 

- `tmux`
- `tmux set-option -g mouse on`


Rename window
```
Ctrl + B  ,  (comma)
```

Split the Terminal Inside tmux

- *Horizontal split:* Ctrl + B then "
- *Vertical split:* Ctrl + B then %
- *Switch between panes:* Ctrl + B then arrow keys
