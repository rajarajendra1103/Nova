# 🌟 Nova V1.6.1 / V2.0 Full-Stack Web Platform Specification
### *HTTP • Server • Backend (DB + Auth + Env) • Frontend UI*
**Core Philosophy:** *Short, Readable, Fluent — Better than Python & JavaScript (Max 8 chars per function)*

---

## 📑 Table of Contents
1. [Overview & Comparison Table](#-overview--comparison-table)
2. [1. HTTP Client Library (`import http`) — 40 Functions](#1-http-client-library-import-http--40-functions)
3. [2. Backend Server Library (`import server`) — 45 Functions](#2-backend-server-library-import-server--45-functions)
4. [3. Backend Data & Security (`import db`, `import auth`, `import env`) — 35 Functions](#3-backend-data--security-import-db-import-auth-import-env--35-functions)
5. [4. Frontend UI Library (`import ui`) — 40 Functions](#4-frontend-ui-library-import-ui--40-functions)
6. [Complete Full-Stack Application Example (Frontend + Backend)](#-complete-full-stack-application-example)
7. [Comprehensive Function Reference (160 Functions)](#-comprehensive-function-reference-160-functions)

---

## ⚡ Overview & Comparison Table

Nova V1.6 unifies the entire web stack (Client HTTP, REST API Servers, SQL/ORM Databases, JWT Auth, and Reactive Front UI) into one cohesive, concise language without node_modules, bundlers, or boilerplates.

| Feature | JavaScript / TypeScript | Python / Flask / FastAPI | **Nova V1.6 / V2.0** |
|---|---|---|---|
| **HTTP GET** | `fetch(url).then(r=>r.json())` | `requests.get(url).json()` | `http.get(url).json()` or `http.g(url)` |
| **HTTP POST JSON** | `fetch(url, {method:'POST', body:JSON.stringify(d)})` | `requests.post(url, json=d)` | `http.post(url, d)` or `http.postJ(url, d)` |
| **Create Server** | `const app = express(); app.use(express.json())` | `app = Flask(__name__)` | `app = server.new()` |
| **Route Definition** | `app.get('/users/:id', (req, res) => ...)` | `@app.route('/users/<id>')` | `app.get("/users/:id", (req, res) -> ...)` |
| **Route Grouping** | `const router = express.Router(); app.use('/api', router)` | `Blueprint('api', __name__, url_prefix='/api')` | `api = app.group("/api")` |
| **Database Query** | `SELECT * FROM users WHERE age > 18` / ORM | `User.objects.filter(age__gt=18)` | `db.findWhere("users", "age > 18")` |
| **Password Hash** | `await bcrypt.hash(pass, 10)` | `bcrypt.hashpw(pass.encode(), bcrypt.gensalt())` | `auth.hash(pass)` |
| **JWT Token** | `jwt.sign(payload, secret)` | `jwt.encode(payload, secret, algorithm="HS256")` | `auth.token(payload, secret)` |
| **Frontend UI** | `document.createElement('button')` / JSX | N/A (Jinja template) | `ui.btn("Save").onClick(...)` |
| **UI Styling** | `className="bg-blue-500 text-white p-4 rounded"` | CSS files | `box.bg("blue").color("white").pad(10).round(8)` |

---

## 1. HTTP Client Library (`import http`) — 40 Functions

Designed for zero-boilerplate API requests from both backend scripts and frontend UI logic.

### 1.1 Basic REST Methods
```nova
import http

# GET request
res = http.get("https://api.com/users")
show res.status     # 200
show res.text       # Raw string body
show res.json()     # Parsed map or list
show res.ok         # true (if status 200-299)

# GET with Query Parameters
res = http.get("https://api.com/users", {page: 1, limit: 10})
# Generated URL: https://api.com/users?page=1&limit=10

# POST with JSON payload
res = http.post("https://api.com/users", {name: "Ravi", age: 21})
show res.status     # 201

# Dedicated JSON POST
res = http.postJ("https://api.com/users", {name: "Ravi"})

# PUT (Full Update)
res = http.put("https://api.com/users/1", {name: "Ram", age: 22})

# DELETE
res = http.delete("https://api.com/users/1")

# PATCH (Partial Update)
res = http.patch("https://api.com/users/1", {age: 22})
```

### 1.2 Ultra-Short Aliases
```nova
res = http.g("https://api.com/users")          # Short for get
res = http.p("https://api.com/users", data)    # Short for post
res = http.pu("https://api.com/users/1", data) # Short for put
res = http.d("https://api.com/users/1")        # Short for delete
```

### 1.3 Headers, Timeouts, Retries & Status Inspection
```nova
# Custom Headers: http.get(url, params, headers, options)
headers = {auth: "Bearer secret_token_xyz", lang: "en"}
options = {timeout: 5000, retry: 3}
res = http.get("https://api.com/data", {}, headers, options)

# Status predicates
if res.ok:
    show "Success: {res.status}"
elsif res.is404():
    show "Resource not found"
elsif res.is500():
    show "Server internal error"
end

# Response Metadata
show res.time               # Round-trip latency in milliseconds
show res.url                # Final resolved URL (after redirects)
show res.headers            # Map of response headers
show res.header("content")  # Single header lookup
show res.bytes()            # Raw binary bytes
```

### 1.4 File Transfer & Async Parallel Requests
```nova
# File Download
http.download("https://site.com/report.pdf", "local_report.pdf")

# File Upload (Multipart Form)
http.upload("https://api.com/upload", "local_report.pdf")
http.uploadData("https://api.com/upload", {file: "local_report.pdf", user: "Ravi"})

# Async Parallel Requests
t1 = http.getAsync("https://api.com/users")
t2 = http.getAsync("https://api.com/posts")
users = t1.wait().json()
posts = t2.wait().json()

# Parallel Bulk GET
results = http.getAll(["https://api.com/u1", "https://api.com/u2", "https://api.com/u3"])
# returns [res1, res2, res3]
```

---

## 2. Backend Server Library (`import server`) — 45 Functions

A lightweight, expressive backend HTTP framework featuring fluent route declarations, nested route groups, automatic JSON serialization, middleware pipelines, and static asset delivery.

### 2.1 Basic Web Server & Routing
```nova
import server

app = server.new()

# Root Route
app.get("/", (req, res) -> {
    res.send("Hello from Nova Server!")
})

# Route with URL Parameter (:id)
app.get("/users/:id", (req, res) -> {
    res.send("User ID is {req.params.id}")
})

# Route with JSON Body
app.post("/users", (req, res) -> {
    user = req.body
    res.status(201).json({ok: true, user: user})
})

# Start listening
app.listen(3000)
show "Server listening on http://localhost:3000"
```

### 2.2 Route Methods & Grouping
```nova
# HTTP Verbs
app.get("/about", (req, res) -> res.send("About page"))
app.post("/login", (req, res) -> res.json({token: "xyz_token"}))
app.put("/users/:id", (req, res) -> res.send("Updated {req.params.id}"))
app.delete("/users/:id", (req, res) -> res.send("Deleted {req.params.id}"))
app.patch("/users/:id", (req, res) -> res.send("Patched {req.params.id}"))
app.all("/health", (req, res) -> res.send("OK"))

# Route Groups (Prefixes)
api = app.group("/api")

api.get("/users", (req, res) -> {
    res.json([{id: 1, name: "Ravi"}, {id: 2, name: "Ram"}])
}) # Handled at GET /api/users

api.get("/posts", (req, res) -> {
    res.json([{id: 101, title: "Nova V1.6"}])
}) # Handled at GET /api/posts
```

### 2.3 `Request` and `Response` Objects
```nova
app.get("/search", (req, res) -> {
    # Request Properties
    show req.url            # Full URL: /search?q=nova&page=1
    show req.path           # Path: /search
    show req.method         # "GET"
    show req.query.q        # Query parameter: "nova"
    show req.query.page     # Query parameter: "1"
    show req.headers        # All request headers
    show req.header("auth") # Single header
    show req.ip             # Remote client IP
    show req.cookies        # Parsed cookie map

    # Response Chaining
    res.status(200)
       .header("x-server", "nova")
       .cookie("session", "abc12345")
       .send("Search result for {req.query.q}")
})

app.get("/download", (req, res) -> {
    res.download("public/report.pdf")
})

app.get("/redirect", (req, res) -> {
    res.redirect("/about")
})
```

### 2.4 Middleware, CORS & Static Serving
```nova
# Global Logging Middleware
app.use((req, res, next) -> {
    show "[{req.method}] {req.path}"
    next()
})

# Route-Specific Auth Middleware
def checkAuth(req, res, next):
    if req.header("auth") == "":
        res.status(401).json({error: "Unauthorized"})
    else:
        next()
    end
end

app.use("/api", checkAuth)

# Built-in Parsers & Cross-Origin
app.json()                              # Auto-parse application/json bodies
app.cors()                              # Allow all origins
app.cors({origin: "https://myapp.com"}) # Restricted origin

# Static File Server
app.static("public")                    # Serves public/* at root (e.g. /index.html)
app.static("public", "/static")         # Serves public/* under /static/*
```

---

## 3. Backend Data & Security (`import db`, `import auth`, `import env`) — 35 Functions

An integrated database abstraction, cryptographic security toolkit, and environment configuration manager.

### 3.1 Database Management (`import db`)
Supports SQLite, MySQL, and PostgreSQL connection strings with native map-based query builders.

```nova
import db

# Connect
db.connect("myapp.db")                               # Local SQLite
# db.connect("postgres://user:pass@localhost/mydb")  # PostgreSQL

# Schema Creation
db.create("users", {id: "int primary", name: "text", age: "int"})

# Insert Records
id1 = db.insert("users", {name: "Ravi", age: 21})
id2 = db.insert("users", {name: "Ram", age: 20})
id3 = db.insert("users", {name: "Anita", age: 17})

# Querying
allUsers  = db.find("users")                       # [{id:1, name:"Ravi", age:21}, ...]
userOne   = db.findOne("users", {id: 1})           # Single map or none
adults    = db.findWhere("users", "age >= 18")     # Filter by SQL condition

# Native Nova Query Filtering & Sorting
users     = db.find("users")
adults    = [take u each u in users if u.age >= 18]
sortedAsc = db.sort("users", "age")                # Sort by age ASC
sortedDsc = db.dsort("users", "age")               # Sort by age DESC (Nova dsort)

# Updates & Deletions
db.update("users", {id: 1}, {age: 22})
db.updateWhere("users", "age < 18", {status: "minor"})

db.delete("users", {id: 2})
db.deleteWhere("users", "age < 18")

# Utility Methods
count = db.count("users")
exists = db.has("users", {name: "Ravi"})
db.clear("users")                                  # Delete all rows
db.drop("users")                                   # Drop entire table
rawRows = db.query("SELECT name, age FROM users WHERE age > 20")
```

### 3.2 Authentication & Cryptography (`import auth`)
```nova
import auth

# Password Hashing & Verification
passHash = auth.hash("mySecurePassword123")
show passHash                                    # Safe salted hash string

isValid = auth.check("mySecurePassword123", passHash)
show isValid                                     # true

# JWT Tokens
payload = {id: 1, name: "Ravi", role: "admin"}
token = auth.token(payload, "my_jwt_secret_key")
show token

# Token Verification
verifiedData = auth.verify(token, "my_jwt_secret_key")
if verifiedData != none:
    show "Welcome {verifiedData.name} ({verifiedData.role})"
else:
    show "Invalid or expired token"
end
```

### 3.3 Environment Variables (`import env`)
```nova
import env

port = env.get("PORT", "3000")                   # Get with default
dbUrl = env.get("DATABASE_URL")                  # Get variable

env.set("APP_ENV", "production")                 # Set variable
show env.has("APP_ENV")                          # true
allConfigs = env.all()                           # Map of all environment variables
```

---

## 4. Frontend UI Library (`import ui`) — 40 Functions

Nova UI enables building complete reactive user interfaces directly in Nova code with intuitive component factories, fluent style chaining, and direct reactive state binding.

### 4.1 UI Page & Elements
```nova
import ui

page = ui.page("User Management Portal")

# Basic Elements
headerTitle = ui.title("Welcome to Nova UI")       # <h1>
subHeading  = ui.subTitle("Manage your team")     # <h2>
label       = ui.text("Enter username below:")     # <p> / <span>
nameInput   = ui.input("Username placeholder")    # <input>
submitBtn   = ui.btn("Save User")                  # <button>
avatarImg   = ui.img("assets/avatar.png")          # <img>
docsLink    = ui.link("Nova Docs", "https://nova.lang") # <a>

# Attach elements to page
page.add(headerTitle)
page.add(subHeading)
page.add(label)
page.add(nameInput)
page.add(submitBtn)
```

### 4.2 Layouts & Fluent Styling
Nova UI provides layout primitives (`ui.row()`, `ui.col()`, `ui.box()`, `ui.stack()`) with chainable style methods.

```nova
# Horizontal Layout (Row)
actionRow = ui.row()
actionRow.add(ui.input("Search..."))
actionRow.add(ui.btn("Search"))
page.add(actionRow)

# Vertical Layout (Col)
profileCol = ui.col()
profileCol.add(ui.img("avatar.png"))
profileCol.add(ui.title("Ravi Kumar"))
profileCol.add(ui.text("Software Engineer"))
page.add(profileCol)

# Styled Container (Fluent Box)
card = ui.box()
card.bg("#1e293b")              # Background color
    .color("#ffffff")           # Text color
    .pad(20)                    # Padding: 20px
    .margin(15)                 # Margin: 15px
    .round(12)                  # Border radius: 12px
    .w(350)                     # Width: 350px
    .h(200)                     # Height: 200px
    .center()                   # Center align contents
    .add(ui.title("Card Header"))
    .add(ui.text("Card body description text"))

page.add(card)
```

### 4.3 Interactive Events & Forms
```nova
# Realtime Input Binding
emailInput = ui.input("Enter email")
emailInput.onChange((val) -> {
    show "User typed: {val}"
})

# Button Click Event
saveBtn = ui.btn("Submit Form")
saveBtn.onClick(() -> {
    show "Saving email: {emailInput.value}"
})

# Complete Form with Submit Handler
userForm = ui.form()
userForm.add(ui.input("Full Name").id("name"))
userForm.add(ui.input("Email Address").id("email"))
userForm.add(ui.btn("Register").type("submit"))

userForm.onSubmit((formData) -> {
    show "Form submitted with data:"
    show formData.name
    show formData.email
    # Directly send to backend via HTTP:
    http.post("/api/users", formData)
})

page.add(userForm)
```

### 4.4 Reactive Lists & Native Comprehensions
```nova
users = [{name: "Ravi", role: "Dev"}, {name: "Ram", role: "Design"}, {name: "Anita", role: "Lead"}]

# Method 1: Iterative List Building
userList = ui.list()
each u in users:
    userList.add(ui.text("{u.name} ({u.role})"))
end
page.add(userList)

# Method 2: Native Nova Comprehension
compList = ui.list([take ui.text("{u.name} - {u.role}") each u in users])
page.add(compList)

# Render Page
page.show()    # Opens/renders UI in browser window
page.render()  # Alias for show
```

---

## 🚀 Complete Full-Stack Application Example

A complete end-to-end CRUD application implemented in Nova V1.6 featuring a backend API server with SQLite and an interactive frontend UI client.

### Backend: `server.nova`
```nova
import server
import db

# 1. Initialize Server & Middleware
app = server.new()
app.json()
app.cors()
app.static("public")

# 2. Initialize Database
db.connect("users_app.db")
db.create("users", {id: "int primary", name: "text", email: "text"})

# 3. Define REST API Routes
app.get("/api/users", (req, res) -> {
    users = db.find("users")
    res.json(users)
})

app.get("/api/users/:id", (req, res) -> {
    id = int(req.params.id)
    user = db.findOne("users", {id: id})
    if user != none:
        res.json(user)
    else:
        res.status(404).json({error: "User not found"})
    end
})

app.post("/api/users", (req, res) -> {
    data = req.body
    newId = db.insert("users", {name: data.name, email: data.email})
    res.status(201).json({id: newId, name: data.name, email: data.email})
})

app.delete("/api/users/:id", (req, res) -> {
    id = int(req.params.id)
    db.delete("users", {id: id})
    res.json({ok: true, deleted: id})
})

# 4. Start Server
app.listen(3000)
show "API Server listening on http://localhost:3000"
```

### Frontend: `app_ui.nova`
```nova
import ui
import http

# 1. Setup UI Page
page = ui.page("Team Directory")

header = ui.title("Team Directory Manager")
page.add(header)

# 2. Input Controls
nameIn  = ui.input("Full Name").id("name")
emailIn = ui.input("Email Address").id("email")
addBtn  = ui.btn("Add Member")

inputRow = ui.row().add(nameIn).add(emailIn).add(addBtn)
page.add(inputRow)

# 3. Dynamic Users Display Column
userContainer = ui.col()
page.add(userContainer)

# 4. Data Fetching & Rendering Logic
def refreshUsers():
    res = http.get("http://localhost:3000/api/users")
    if res.ok:
        userContainer.clear()
        userList = res.json()
        each u in userList:
            userCard = ui.box().bg("#334155").color("#ffffff").pad(10).margin(5).round(6)
            userCard.add(ui.text("#{u.id} - {u.name} ({u.email})"))
            
            delBtn = ui.btn("Delete")
            delBtn.onClick(() -> {
                http.delete("http://localhost:3000/api/users/{u.id}")
                refreshUsers()
            })
            
            userCard.add(delBtn)
            userContainer.add(userCard)
        end
    end
end

# 5. Handle Add Button Click
addBtn.onClick(() -> {
    if nameIn.value != "" and emailIn.value != "":
        http.post("http://localhost:3000/api/users", {
            name: nameIn.value,
            email: emailIn.value
        })
        nameIn.value = ""
        emailIn.value = ""
        refreshUsers()
    end
})

# 6. Initial Load & Render
refreshUsers()
page.show()
```

---

## 📚 Comprehensive Function Reference (160 Functions)

### 1. HTTP Module (`import http`) — 40 Functions
| Function / Property | Parameters | Description |
|---|---|---|
| `http.get(url, [params], [headers], [opts])` | `url, map, map, map` | Perform HTTP GET request |
| `http.post(url, data, [headers], [opts])` | `url, map/str, map, map` | Perform HTTP POST request |
| `http.postJ(url, data, [headers], [opts])` | `url, map, map, map` | Explicit JSON POST request |
| `http.put(url, data, [headers], [opts])` | `url, map/str, map, map` | Perform HTTP PUT request |
| `http.delete(url, [headers], [opts])` | `url, map, map` | Perform HTTP DELETE request |
| `http.patch(url, data, [headers], [opts])` | `url, map/str, map, map` | Perform HTTP PATCH request |
| `http.g(url)` | `url` | Short alias for `http.get` |
| `http.p(url, data)` | `url, data` | Short alias for `http.post` |
| `http.pu(url, data)` | `url, data` | Short alias for `http.put` |
| `http.d(url)` | `url` | Short alias for `http.delete` |
| `http.download(url, localPath)` | `url, path` | Stream download to local file |
| `http.upload(url, localPath)` | `url, path` | Upload file as multipart/form-data |
| `http.uploadData(url, map)` | `url, map` | Upload files with attached fields |
| `http.getAsync(url)` | `url` | Non-blocking async GET task |
| `http.getAll(urlList)` | `list` | Parallel GET for multiple URLs |
| `res.status` | property | HTTP status code integer (e.g. 200, 404) |
| `res.text` | property | Response body as UTF-8 string |
| `res.json()` | method | Parse body as Nova map or list |
| `res.bytes()` | method | Raw binary response bytes |
| `res.ok` | property | `true` if status is in range 200-299 |
| `res.isOk()` | method | Status code predicate (200-299) |
| `res.is404()` | method | Returns `true` if status is 404 |
| `res.is500()` | method | Returns `true` if status is 500 |
| `res.headers` | property | Map of all response headers |
| `res.header(name)` | `str` | Case-insensitive single header lookup |
| `res.time` | property | Latency of request in milliseconds |
| `res.url` | property | Final resolved URL |

---

### 2. Server Module (`import server`) — 45 Functions
| Function / Property | Parameters | Description |
|---|---|---|
| `server.new()` | none | Create a new Nova server instance |
| `app.get(path, handler)` | `path, fn` | Register GET route handler |
| `app.post(path, handler)` | `path, fn` | Register POST route handler |
| `app.put(path, handler)` | `path, fn` | Register PUT route handler |
| `app.delete(path, handler)` | `path, fn` | Register DELETE route handler |
| `app.patch(path, handler)` | `path, fn` | Register PATCH route handler |
| `app.all(path, handler)` | `path, fn` | Register handler for all HTTP methods |
| `app.group(prefix)` | `str` | Create sub-router with URL prefix |
| `app.use([path], handler)` | `[str], fn` | Add middleware to request pipeline |
| `app.listen(port)` | `int` | Start HTTP server listening on port |
| `app.l(port)` | `int` | Short alias for `listen` |
| `app.json()` | none | Enable automatic JSON body parsing |
| `app.cors([opts])` | `[map]` | Enable CORS headers |
| `app.static(folder, [prefix])` | `str, [str]` | Serve static directory |
| `req.url` | property | Full request URL with query string |
| `req.path` | property | Path portion of URL |
| `req.method` | property | HTTP method string (GET, POST, etc.) |
| `req.params` | property | Route parameters map (e.g. `:id`) |
| `req.query` | property | Parsed query string parameters map |
| `req.body` | property | Parsed JSON body map/list |
| `req.text` | property | Raw request body string |
| `req.form` | property | Parsed multipart/form data map |
| `req.headers` | property | Request headers map |
| `req.header(name)` | `str` | Lookup single request header |
| `req.ip` | property | Client IP address string |
| `req.cookies` | property | Parsed cookies map |
| `res.send(data)` | `any` | Send text response |
| `res.json(data)` | `any` | Send JSON response with header |
| `res.status(code)` | `int` | Set HTTP status code (chainable) |
| `res.header(k, v)` | `str, str` | Set response header (chainable) |
| `res.cookie(k, v)` | `str, str` | Set Set-Cookie header |
| `res.redirect(url)` | `str` | Send 302 redirect response |
| `res.file(path)` | `str` | Send local file as response |
| `res.download(path)` | `str` | Send file as attachment download |
| `res.type(mime)` | `str` | Set Content-Type by name/extension |

---

### 3. Backend Data, Auth & Env (`db`, `auth`, `env`) — 35 Functions
| Module | Function | Parameters | Description |
|---|---|---|---|
| `db` | `connect(uri)` | `str` | Connect to SQLite/MySQL/PostgreSQL |
| `db` | `create(table, schema)` | `str, map` | Create table with typed fields |
| `db` | `table(table, schema)` | `str, map` | Alias for `create` |
| `db` | `insert(table, data)` | `str, map` | Insert record; returns inserted ID |
| `db` | `find(table)` | `str` | Fetch all records as list of maps |
| `db` | `findOne(table, where)` | `str, map` | Fetch single matching record |
| `db` | `findWhere(table, cond)`| `str, str` | Fetch records matching SQL condition |
| `db` | `filter(table, expr)` | `str, expr` | Query records with Nova filter |
| `db` | `sort(table, field)` | `str, str` | Fetch records sorted ascending |
| `db` | `dsort(table, field)` | `str, str` | Fetch records sorted descending |
| `db` | `update(table, where, data)` | `str, map, map` | Update matching record(s) |
| `db` | `updateWhere(table, cond, data)` | `str, str, map` | Update records matching condition |
| `db` | `delete(table, where)` | `str, map` | Delete record(s) matching map |
| `db` | `deleteWhere(table, cond)` | `str, str` | Delete records matching condition |
| `db` | `count(table)` | `str` | Count rows in table |
| `db` | `has(table, where)` | `str, map` | Check if matching row exists |
| `db` | `clear(table)` | `str` | Truncate/delete all rows in table |
| `db` | `drop(table)` | `str` | Drop table entirely |
| `db` | `query(sql)` | `str` | Execute raw SQL query |
| `auth` | `hash(password)` | `str` | Generate secure password hash |
| `auth` | `check(password, hash)` | `str, str` | Verify password against hash |
| `auth` | `token(payload, secret)` | `map, str` | Generate signed JWT token |
| `auth` | `verify(token, secret)` | `str, str` | Verify JWT; returns payload map or none |
| `env` | `get(key, [default])` | `str, [str]` | Retrieve environment variable |
| `env` | `set(key, value)` | `str, str` | Set environment variable |
| `env` | `has(key)` | `str` | Check if environment variable exists |
| `env` | `all()` | none | Return all env variables as map |

---

### 4. Frontend UI Module (`import ui`) — 40 Functions
| Function / Method | Parameters | Description |
|---|---|---|
| `ui.page(title)` | `str` | Create top-level UI Page container |
| `ui.box()` | none | Create styled Box (`<div>`) container |
| `ui.text(content)` | `str` | Create Text label component |
| `ui.title(content)` | `str` | Create primary Title heading (`<h1>`) |
| `ui.subTitle(content)` | `str` | Create Subtitle heading (`<h2>`) |
| `ui.input(placeholder)`| `str` | Create interactive Text Input |
| `ui.btn(label)` | `str` | Create clickable Button component |
| `ui.img(src)` | `str` | Create Image component |
| `ui.link(text, url)` | `str, str` | Create Hyperlink anchor |
| `ui.row()` | none | Horizontal flex layout container |
| `ui.col()` | none | Vertical flex layout container |
| `ui.stack()` | none | Layered overlapping stack container |
| `ui.form()` | none | Form container with submit interception |
| `ui.list([items])` | `[list]` | Dynamic list component |
| `el.add(child)` | `component` | Append child element (chainable) |
| `el.bg(color)` | `str` | Set background color (chainable) |
| `el.color(color)` | `str` | Set text/foreground color (chainable) |
| `el.pad(px)` | `int` | Set internal padding in pixels |
| `el.margin(px)` | `int` | Set external margin in pixels |
| `el.round(px)` | `int` | Set border radius in pixels |
| `el.w(px)` | `int` | Set component width in pixels |
| `el.h(px)` | `int` | Set component height in pixels |
| `el.center()` | none | Center align child contents |
| `el.id(idStr)` | `str` | Set element identifier |
| `el.value` | property | Get/set current input value |
| `el.clear()` | none | Remove all child elements |
| `el.onClick(fn)` | `fn` | Attach click event handler |
| `el.onChange(fn)` | `fn` | Attach input change event handler |
| `el.onSubmit(fn)` | `fn` | Attach form submit event handler |
| `page.show()` | none | Render and display UI |
| `page.render()` | none | Alias for `show()` |

---
*Nova V1.6 Full Stack Web Platform — Built for high-speed, expressive, and concise engineering.*
