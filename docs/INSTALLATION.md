# CoreGraph: The Ultimate Step-by-Step Setup and Installation Guide

Welcome to the CoreGraph Titan. This document is the ultimate, comprehensive, step-by-step manual designed specifically for a third party (someone who has never seen this project before) to set up, run, and understand the entire system from scratch.

By the end of this guide, you will have a fully functional, production-ready environment running on your local machine. You will learn how to install and configure:
1. **Git**: To download the source code.
2. **Docker Desktop**: To run our isolated, secure application containers.
3. **PostgreSQL**: Our permanent, highly secure relational database.
4. **Redis**: Our lightning-fast in-memory cache for real-time tracking.
5. **DBeaver**: A powerful visual database tool to interact with your data.

This guide is written in plain, easy-to-understand English. Follow every step carefully, and you will have the 3.81 million node engine running perfectly.

---

## Table of Contents
1. [Understanding the Ecosystem](#chapter-1-understanding-the-ecosystem)
2. [Hardware Prerequisites](#chapter-2-hardware-prerequisites)
3. [Installing Git](#chapter-3-installing-git)
4. [Installing Docker Desktop](#chapter-4-installing-docker-desktop)
5. [Installing DBeaver](#chapter-5-installing-dbeaver)
6. [Downloading the Project](#chapter-6-downloading-the-project)
7. [Starting the System (Docker Compose)](#chapter-7-starting-the-system)
8. [Verifying the Installation](#chapter-8-verifying-the-installation)
9. [Setting up DBeaver (Visual Database Access)](#chapter-9-setting-up-dbeaver)
10. [Exploring the Database](#chapter-10-exploring-the-database)
11. [Accessing the HUD (Visual Map)](#chapter-11-accessing-the-hud)
12. [Shutting Down the System](#chapter-12-shutting-down-the-system)
13. [Extensive Troubleshooting Guide](#chapter-13-extensive-troubleshooting-guide)

---

## Chapter 1: Understanding the Ecosystem

Before installing anything, it is very important to understand *what* we are installing and *why*. CoreGraph is not just a single program you double-click; it is an ecosystem of powerful tools working together.

### What is Docker?
Imagine you write a piece of software on your computer, and it works perfectly. But when you send it to your friend, it breaks because they have a different version of Windows, or they are missing a specific file. 
**Docker** solves this. It packs the application and everything it needs to run into a tiny, virtual box called a **Container**. This container will run exactly the same way on your computer, your friend's computer, or a massive server.

### What is PostgreSQL?
PostgreSQL (often called Postgres) is an incredibly powerful, open-source database. Think of it as a massive, hyper-organized filing cabinet. We use Postgres to permanently store our 3.81 million nodes. If the power goes out, Postgres ensures that absolutely no data is lost.

### What is Redis?
While Postgres is safe and permanent, it can sometimes be a little slow for real-time graphics. **Redis** is an "in-memory" database. It is like the short-term memory of the system. It holds the live coordinates of the nodes so the visual screen can update instantly without waiting for the filing cabinet (Postgres).

### What is DBeaver?
Databases like Postgres do not have a graphical interface built-in. If you want to see the data, you normally have to type complex code into a black screen. **DBeaver** is a visual tool (a Database GUI) that lets you click, view, and manage your database using a friendly, spreadsheet-like interface.

---

## Chapter 2: Hardware Prerequisites

Because CoreGraph is a massive engine designed for millions of data points, your computer needs to meet certain requirements to run it smoothly.

### Minimum Requirements:
- **Processor (CPU)**: Any modern 4-core processor (Intel Core i5 or AMD Ryzen 5).
- **Memory (RAM)**: 8 Gigabytes of RAM minimum (16GB is highly recommended).
- **Storage**: At least 10 Gigabytes of free hard drive space (SSD is highly recommended over an older HDD).
- **Operating System**: Windows 10/11 (Pro or Home), macOS (Intel or Apple Silicon), or Linux (Ubuntu/Debian).

### Recommended Requirements (For 144Hz Experience):
- **Processor (CPU)**: 8+ Core Processor (Intel Core i9 or AMD Ryzen 9).
- **Memory (RAM)**: 32 Gigabytes of RAM.
- **Graphics (GPU)**: A dedicated graphics card (like an NVIDIA RTX 3060 or better) to render the web visuals smoothly.

---

## Chapter 3: Installing Git

Git is a tool that allows you to download (or "clone") the exact code from our online repository to your computer.

### For Windows Users:
1. Open your web browser and go to: `https://git-scm.com/download/win`
2. Click on "64-bit Git for Windows Setup".
3. Once the `.exe` file downloads, double-click it to start the installer.
4. The installer has many screens. You do not need to change anything. Just keep clicking the **"Next"** button until the installation is complete.
5. Click **"Finish"**.

### For macOS Users:
1. Open the "Terminal" application (you can find it using Spotlight search).
2. Type `git --version` and press Enter.
3. If Git is not installed, your Mac will automatically ask if you want to install the "Command Line Developer Tools". Click **"Install"** and follow the prompts.

### Verifying Git Installation:
1. Open your Command Prompt (Windows) or Terminal (Mac).
2. Type `git --version` and press Enter.
3. You should see a message like `git version 2.40.0.windows.1`. If you see this, Git is installed perfectly!

---

## Chapter 4: Installing Docker Desktop

Docker is the most critical piece of software. It will act as the host for our databases and the CoreGraph application.

### Important Note for Windows Users (WSL 2):
Docker on Windows requires a feature called **WSL 2** (Windows Subsystem for Linux). Docker will usually install this for you, but if it asks you to update or install WSL 2 during the setup, always click **Yes** or follow the link it provides.

### Step-by-Step Installation:
1. Open your web browser and go to: `https://www.docker.com/products/docker-desktop/`
2. Click the large blue button that says **"Download for Windows"** (or Mac if you are on an Apple computer).
3. Once the installer (`Docker Desktop Installer.exe`) is downloaded, double-click it.
4. A window will appear asking if you want to use WSL 2 instead of Hyper-V. **Leave this checked (enabled)**. It is much faster.
5. Click **"Ok"** to begin the installation. It may take a few minutes.
6. Once it finishes, click **"Close and Restart"**. Your computer will reboot.
7. After your computer turns back on, Docker Desktop should launch automatically. You will see a small "Whale" icon in the bottom-right corner of your screen (near the clock).
8. A window will pop up asking you to accept the Docker Subscription Service Agreement. Click **"Accept"**.
9. You do not need to sign in or create an account. You can click **"Continue without signing in"** or "Skip".

### Verifying Docker Installation:
1. Open your Command Prompt or Terminal.
2. Type `docker --version` and press Enter.
3. You should see something like `Docker version 24.0.2, build cb74dfc`.
4. Next, type `docker-compose --version`. You should see `Docker Compose version v2.18.1`. 
If you see both of these, Docker is perfectly ready!

---

## Chapter 5: Installing DBeaver

Now we will install the visual tool that will allow us to look inside our Postgres database.

1. Open your web browser and go to: `https://dbeaver.io/download/`
2. Look for the section titled **"DBeaver Community Edition"** (this version is completely free).
3. Click on the **"Windows (installer)"** link (or the Mac/Linux link depending on your computer).
4. Once the file downloads, double-click it to start the installer.
5. Choose **"English"** and click **"OK"**.
6. Click **"Next"**, then **"I Agree"** to the license.
7. Choose **"For anyone who uses this computer"** and click **"Next"**.
8. Keep all the default checkboxes selected and click **"Next"**, then **"Install"**.
9. Once it finishes, check the box that says **"Create Desktop Shortcut"** and click **"Finish"**.

You now have DBeaver installed! We will use it later in Chapter 9.

---

## Chapter 6: Downloading the Project

Now that we have all the required software, we need to download the actual CoreGraph code.

1. Open your Command Prompt (Windows) or Terminal (Mac).
2. We want to navigate to a folder where we will store the project. For example, your Documents folder. Type:
   ```bash
   cd Documents
   ```
3. Now, we will use Git to download the code. Type this command and press Enter:
   ```bash
   git clone https://github.com/your-username/COREGRAPH.git
   ```
   *(Note: If you have the code locally already in a ZIP file, simply extract it to a folder named COREGRAPH).*
4. Move into the newly created folder by typing:
   ```bash
   cd COREGRAPH
   ```
5. You are now inside the project directory! You can type `dir` (on Windows) or `ls` (on Mac) to see the files. You should see files like `README.md`, `Dockerfile`, and `docker-compose.yml`.

---

## Chapter 7: Starting the System (Docker Compose)

This is where the magic happens. We have a file called `docker-compose.yml` that acts as a blueprint. When we give this blueprint to Docker, it automatically does all the hard work: it downloads Postgres, downloads Redis, builds our CoreGraph engine, and networks them all together safely.

1. Ensure your Command Prompt is currently inside the `COREGRAPH` folder.
2. Type the following command and press Enter:
   ```bash
   docker-compose up -d --build
   ```

### What is happening right now?
The screen will start filling with downloading bars and text. This is completely normal! Here is what Docker is doing in the background:
- **Pulling Postgres**: It is reaching out to the official Docker servers to download the perfectly secure version of PostgreSQL.
- **Pulling Redis**: It is downloading the fast, in-memory cache system.
- **Building CoreGraph**: It is looking at our `Dockerfile` and building the 155MB Distroless application from scratch. It is installing Python, downloading our code, and packing it tightly.
- **Creating the Network**: It is creating an "Air-Gapped" internal network called `coregraph_mesh`. It places the database, the cache, and the engine onto this private network so they can talk to each other, but the outside world cannot reach them.
- **Starting Up**: Finally, it turns them all on. The `-d` in our command stands for "Detached", which means it runs them quietly in the background so you can keep using your terminal window.

This process might take 2 to 5 minutes depending on your internet speed. Wait until you see green `Started` messages for all three containers.

---

## Chapter 8: Verifying the Installation

We need to make sure all three parts of the system are actually running successfully without errors.

1. In your terminal, type:
   ```bash
   docker ps
   ```
   You should see a list that looks like this:
   ```text
   CONTAINER ID   IMAGE                           COMMAND                  STATUS         PORTS                    NAMES
   abc123def456   coregraph-engine:final-hardened "python master_orch..."  Up 2 minutes   0.0.0.0:8000->8000/tcp   ingestion_phalanx
   def456ghi789   postgres:15-alpine              "docker-entrypoint.s…"   Up 2 minutes   5432/tcp                 coregraph_db
   ghi789jkl012   redis:7-alpine                  "docker-entrypoint.s…"   Up 2 minutes   6379/tcp                 coregraph_cache
   ```
   If you see all three listed as `Up`, the system is running perfectly!

2. **Checking the Logs (Optional but helpful):**
   If you want to see what the CoreGraph engine is actually thinking and doing, you can read its live logs. Type:
   ```bash
   docker logs ingestion_phalanx -f
   ```
   You will see the system booting up, connecting to the database, and starting the 144Hz HUD. To exit the logs, press `Ctrl + C` on your keyboard.

---

## Chapter 9: Setting up DBeaver (Visual Database Access)

The CoreGraph engine is running and saving data into PostgreSQL. Let's connect to PostgreSQL using the visual tool we installed earlier (DBeaver) so we can look at the raw data with our own eyes.

1. Open the **DBeaver** application from your Start Menu or Desktop.
2. If a popup asks if you want to create a sample database, click **"No"**.
3. In the very top-left corner of the window, click on the icon that looks like a plug with a plus sign (it is called **"New Database Connection"**).
4. A large menu of database types will appear. Click on the icon for **PostgreSQL** (it looks like a blue elephant).
5. Click **Next**.
6. You will now see the "Connection Settings" window. Fill in these exact details:
   - **Host**: `localhost`
   - **Port**: `5432` (This should be filled in by default)
   - **Database**: `coregraph_vault`
   - **Username**: `coregraph_admin`
   - **Password**: `coregraph_secret123`
7. At the bottom left of this window, click the **"Test Connection"** button.
   - *Important Note*: Because this is your first time using DBeaver, a small window might pop up saying "Driver files are missing." This is totally normal! Just click the **"Download"** button. DBeaver will automatically download the tiny piece of software it needs to talk to Postgres.
8. After it downloads (or immediately if you already have the driver), a box will pop up saying "Connected!". It will show the version of PostgreSQL. Click **OK**.
9. Finally, click the **"Finish"** button at the bottom right.

You are now connected! Look at the left side of your DBeaver window. You will see a panel called **"Database Navigator"**. You will see your new connection named `postgres - localhost` (or something similar). 

---

## Chapter 10: Exploring the Database

Let's navigate through DBeaver to actually find the 3.81 million nodes that CoreGraph is managing.

1. In the **Database Navigator** on the left side of DBeaver, click the tiny arrow `>` next to your connection to expand it.
2. Click the arrow `>` next to **Databases**.
3. Click the arrow `>` next to **coregraph_vault** (This is our specific database).
4. Click the arrow `>` next to **Schemas**.
5. Click the arrow `>` next to **public** (This is where user tables are stored).
6. Click the arrow `>` next to **Tables**.

You will now see a list of the tables the CoreGraph engine has created! For example, you might see tables like `nodes`, `edges`, or `telemetry_logs`.

### Viewing the Data:
1. Double-click on the `nodes` table.
2. A new window will open in the middle of your screen. Look for the tabs at the top of this middle window (Properties, Data, ER Diagram).
3. Click on the **"Data"** tab.
4. You are now looking at a spreadsheet view of your database! You will see rows upon rows of data representing the CoreGraph nodes. You can scroll through them, sort them, or filter them just like an Excel spreadsheet.

### Writing Custom SQL (For Advanced Users):
If you want to run custom queries:
1. At the top of DBeaver, click the **"SQL Editor"** button (it looks like a small scroll with a magnifying glass).
2. A blank text area will open. Type:
   ```sql
   SELECT COUNT(*) FROM nodes;
   ```
3. Press `Ctrl + Enter` (or click the orange Play button on the left).
4. At the bottom of the screen, it will show you the exact number of nodes currently in the database!

---

## Chapter 11: Accessing the HUD (Visual Map)

Looking at spreadsheets in DBeaver is great for engineers, but CoreGraph is designed to be a visual masterpiece. We need to see the 144Hz WebGL rendering of the data.

Because our `docker-compose.yml` file forwarded port `8000` to your local computer, accessing the visual dashboard is incredibly simple.

1. Open your favorite modern web browser (Google Chrome, Microsoft Edge, Mozilla Firefox, or Safari).
2. Click on the address bar at the top.
3. Type in the following exact address and press Enter:
   ```text
   http://localhost:8000
   ```

### What to expect on the screen:
- You will see a dark, sleek, premium user interface.
- In the center of the screen, you will see thousands of glowing points of light. These are your nodes.
- You will see lines connecting them, representing the relationships.
- On the side panels, you will see real-time metrics showing the "Ingestion Rate" (how fast data is coming in), the "Vitality Status" (the health of the system), and the "System Heat" (how hard the mathematical engines are working).
- The map is completely interactive! You can click and drag to pan around the universe, use your scroll wheel to zoom in to specific clusters, and hover over individual nodes to see their specific properties.
- The screen is updating using Binary Delta-Encoding, which means it is rendering at 144 frames per second. It should feel incredibly liquid and smooth, with absolutely zero stuttering or lag.

---

## Chapter 12: Shutting Down the System

When you are finished using CoreGraph, it is important to shut it down properly so it does not continue using your computer's RAM and CPU in the background.

1. Open your Command Prompt or Terminal.
2. Make sure you are still inside the `COREGRAPH` folder.
3. Type the following command and press Enter:
   ```bash
   docker-compose down
   ```

### What is happening right now?
Docker is safely sending a "Stop" signal to the CoreGraph engine, telling it to finish any math it is doing. It then sends a stop signal to Redis and PostgreSQL. Postgres ensures that the WAL (Write-Ahead Logs) are safely written to the hard drive so zero data is lost.
Finally, Docker destroys the temporary internal network.

**Important Note about Data:**
Even though the containers are shut down and destroyed, **your data is perfectly safe**. Docker keeps the database files stored in a special invisible folder on your hard drive called a "Volume". The next time you type `docker-compose up -d`, the database will reconnect to this volume, and all your millions of nodes will still be there exactly as you left them!

---

## Chapter 13: Extensive Troubleshooting Guide

Sometimes things go wrong. Computers are complex. Here are the most common issues you might face and exactly how to solve them.

### Problem 1: "Ports are not available: listen tcp 0.0.0.0:5432"
**The Cause:** This error happens when you type `docker-compose up -d`. It means another program on your computer is already using port 5432. 99% of the time, this is because you installed PostgreSQL directly onto your Windows/Mac computer in the past, and it is running in the background.
**The Solution:**
1. Open the `docker-compose.yml` file in any text editor (like Notepad).
2. Look for the `db:` section. If it has a line that says `ports: - "5432:5432"`, change it to `ports: - "5433:5432"`.
3. Save the file and run `docker-compose up -d` again. 
4. *Note: If you do this, when you connect via DBeaver (Chapter 9), you must type `5433` into the port box instead of `5432`.*

### Problem 2: "Docker Daemon is not running" or "Cannot connect to the Docker daemon"
**The Cause:** Docker Desktop is closed, or it crashed. The terminal command cannot talk to Docker because Docker is asleep.
**The Solution:**
1. Open your Start Menu or Applications folder.
2. Search for "Docker Desktop" and click it.
3. Wait 30 seconds for the application to fully load. You should see a green bar that says "Engine Running" in the bottom left of the Docker window.
4. Try your terminal command again.

### Problem 3: The `docker-compose up --build` command freezes or fails during the `npm install` or `pip install` step.
**The Cause:** This is almost always caused by a slow or unstable internet connection. The build process needs to download hundreds of megabytes of libraries from the internet. If your Wi-Fi drops for even a second, the build might fail.
**The Solution:**
1. In your terminal, hold the `Ctrl` key and press `C` to cancel the frozen process.
2. Type `docker-compose build --no-cache` and press Enter. This forces Docker to try downloading everything fresh from the beginning.
3. Make sure you have a strong internet connection.
4. Once the build finishes successfully, run `docker-compose up -d` as normal.

### Problem 4: DBeaver says "Connection Refused" or "FATAL: password authentication failed"
**The Cause:** You either typed the password wrong, or you are connecting to the wrong database.
**The Solution:**
1. Double-check your spelling! The username MUST be exactly `coregraph_admin` and the password MUST be exactly `coregraph_secret123`.
2. Ensure you selected "PostgreSQL" and not "MySQL" when creating the connection.
3. Ensure Docker is actually running. Type `docker ps` in your terminal to verify that `coregraph_db` is currently listed as "Up". If the database is off, DBeaver cannot connect to it.

### Problem 5: I go to `http://localhost:8000` but my browser says "This site can’t be reached".
**The Cause:** The CoreGraph Engine container is either not running, or it crashed immediately after starting.
**The Solution:**
1. Type `docker ps` in your terminal. Look for `ingestion_phalanx`. Is it there? If not, it crashed.
2. Type `docker ps -a` (this shows crashed containers too). Look for `ingestion_phalanx`.
3. Type `docker logs ingestion_phalanx`. This will print out exactly why it crashed. It might say something like "Cannot connect to database" (which means Postgres took too long to start) or "Out of Memory".
4. If it was just a temporary glitch, you can type `docker-compose restart` to force all three containers to reboot and try again.

### Problem 6: The system is using too much RAM and my computer is lagging.
**The Cause:** CoreGraph is designed to be extremely memory efficient (155MB residency), but PostgreSQL can use a lot of RAM if it is given permission.
**The Solution:**
1. Open Docker Desktop.
2. Click the **Gear Icon (Settings)** in the top right.
3. Click on **Resources** on the left menu.
4. Lower the **Memory Limit** slider to something like 4GB or 6GB.
5. Click **Apply & Restart**. Docker will now strictly limit how much RAM the entire ecosystem is allowed to use, saving your computer from lagging.

---

## Conclusion
Congratulations! You have successfully installed, configured, verified, and interacted with a production-grade, distributed OSINT platform. By understanding Docker, PostgreSQL, Redis, and DBeaver, you now possess the core skills required to manage enterprise-level infrastructure.

Welcome to the CoreGraph Titan.
