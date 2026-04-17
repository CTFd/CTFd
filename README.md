# ![image](CTFd/themes/core/assets/img/ctf101.png)

# CTF 101 - Play/CSAW365/CTF

## Info

This is a local fork of CTFd (v.3.8.3) used to host a CTFd instance for old csawCTF challenges (this was known as csaw365; I'm branding it as ctf101 - Play). 

### Expectations

1. There will be people coming from [ctf101.org](https://ctf101.org). There's a non-zero amount of traffic going to ctf101.org every day. Therefore, I want to prepare for ~100 users of concurrency. 
2. Theme must stay consistent between ctf101.org and Play.
3. Accessible at all times. **0 auth needed for challenges** (very idealistic hoping people don't destroy the challenge infra, but hope there'll be countermeasures in challenges). If people want to make an account to save their progress, the option will be there.
4. Challenges - The challenges themselves will be hosted on a different repository. This is only the web-frontend.

### Custom Implementations

1. **postgreSQL** - I used postgreSQL instead of the default mariaDB it came with. I was concerned about scalability so I chose to plug in postgres. Untested lol.
2. **custom theme** - The theme was something I made. To set up development for the theme, run the local Flask debug server and use Vite to watch the `themes/core/` folder. There's an `npm` ecosystem in there to help you out. Changes made to `/core/**` will be built automatically onsave.
    ``` bash
    pip install -r development.txt
    python3 serve.py
    ```

    ```bash
    npm install
    npm run dev
    ```
3. **custom nginx config** - I wanted the ability to run multiple frontends to potentially serve a lot of people. Since I was given 1 IP to work with, I load-balance across individual containers. To start the servers with 3 replicas, run the following.
    ```bash
    docker compose up --scale ctfd=3
    ```

    Using `docker stats` and `hey` to test the nginx load-balancing, it reached around 120mb-memory/container, ~98% CPU usage.
    ```bash
    hey -m GET -n 5000 http://localhost/
    ```
    For response data, checkout [results](/tests/5000_getreq_3replica.csv)

## Run

### Requirements

1. `docker compose` - pretty [easy](https://docs.docker.com/compose/)

To start the application, clone the repository.

```bash
git clone
```

Run application with docker compose.

```bash
docker compose up
# By default, this will start 1 instance of the frontend. See Custom Implementations for scaling.
```

## In development

1. **About page** - Good first PR if anyone wants to help. Write some content about CSAW and history to put in it. Then, create a route + navlink.
2. **Sign up banner** - Banner across top of the screen to motivate more sign ups for accounts. _Still up in the air about it because it might cause people to think an account is needed to play._