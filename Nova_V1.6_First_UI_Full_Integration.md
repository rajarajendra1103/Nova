# 🚀 Nova V1.6.1 Master Platform Specification & UI Integration
### *Core OOP • 505+ Stdlib Functions • Full-Stack Web • 80 Reactive UI Functions*

**Philosophy:** *Short, Readable, Fluent — Better than Python & JavaScript (Max 8 characters per function, zero boilerplate).*

---

## 📑 Table of Contents
1. [Platform Architecture & Total Metrics](#-platform-architecture--total-metrics)
2. [Language Syntax & Core Engine (V1.0 – V1.4)](#-language-syntax--core-engine-v10--v14)
3. [Standard Library — 8 Modules / 505+ Functions (V1.5)](#-standard-library--8-modules--505-functions-v15)
4. [Full-Stack Web & Backend Platform (V1.6)](#-full-stack-web--backend-platform-v16)
5. [V1.6.1 First UI Library — 80 Functions (Web, Desktop, Apps)](#-v161-first-ui-library--80-functions-web-desktop-apps)
6. [5 Real-World UI Example Applications](#-5-real-world-ui-example-applications)
7. [V1.7 Game Engine Roadmap (40 Functions Preview)](#-v17-game-engine-roadmap-40-functions-preview)

---

## 📊 Platform Architecture & Total Metrics

Nova V1.6.1 delivers a unified ecosystem for scripting, enterprise backend services, and front-end desktop/web applications:

| Layer / Module | Functions / Keywords | Purpose & Highlights |
| :--- | :---: | :--- |
| **V1.0 - V1.4 Core** | 35+ Keywords | Classes, Enums, Lambdas (`x -> x*2`), Comprehensions (`take each in if`), `throw/try/catch/finally`, String Interpolation |
| **V1.5 Stdlib: Math** | 63 Functions | `root`, `power`, `clamp`, `lerp`, `isPrime`, `gcd`, `fact`, `sin`, `log10` |
| **V1.5 Stdlib: String** | 65 Functions | `upper`, `lower`, `trim`, `padL`, `padR`, `split`, `join`, `wordC`, `starts`, `ends` |
| **V1.5 Stdlib: List** | 68 Functions | `unique`, `freq`, `group`, `chunk`, `window`, `zip`, `find`, `every`, `some`, `flat` |
| **V1.5 Stdlib: Set** | 62 Functions | `U`, `N`, `diff`, `cart`, `power`, `isSub`, `isSuper`, `isDisjoint`, `toList` |
| **V1.5 Stdlib: File & OS** | 65 Functions | `readA`, `writeA`, `cd`, `pwd`, `pathJoin`, `exists`, `walk`, fluent `open()` |
| **V1.5 Stdlib: Random** | 60 Functions | `int`, `floatR`, `pick`, `pickN`, `str`, `otp`, `uuid`, `dice`, `coin`, `pass` |
| **V1.5 Stdlib: Time** | 62 Functions | `now`, `date`, `stamp`, `addDay`, `diffHour`, `format`, `age`, `isLeap` |
| **V1.5 Stdlib: JSON** | 60 Functions | `text`, `map`, `getPath`, `setPath`, `flat`, `unflat`, `pretty`, `diff`, `patch` |
| **V1.6 Backend: HTTP** | 40 Functions | `get`, `post`, `postJ`, `put`, `delete`, `download`, `upload`, `getAsync` |
| **V1.6 Backend: Server** | 45 Functions | `server.new()`, `app.get`, `app.post`, `app.group`, `app.json()`, `app.cors()` |
| **V1.6 Backend: DB, Auth, Env** | 35 Functions | `db.create`, `db.insert`, `db.find`, `auth.hash`, `auth.token`, `env.get` |
| **V1.6.1 First UI Library** | 80 Functions | `ui.app`, `ui.card`, `ui.btnP`, `ui.input`, `ui.row`, `ui.col`, `ui.grid`, styles |
| **TOTAL FUNCTIONS** | **745+ Functions** | **Zero External Dependencies • Self-Contained Interpreter** |

---

## ⚡ Language Syntax & Core Engine (V1.0 – V1.4)

### 1. Variables, Types & Immutability
```nova
name: string = "Nova"
age: int = 21
const PI = 3.14159265
```

### 2. OOP & Inheritance
```nova
class Animal:
    public name = ""
    init(name):
        this.name = name
    end
    def sound():
        give "Generic sound"
    end
end

class Dog extends Animal:
    def sound():
        give "{this.name} says: Woof!"
    end
end

d = Dog("Buddy")
show d.sound()  # Buddy says: Woof!
```

### 3. Native Comprehensions & Arrow Functions
```nova
numbers = [1, 2, 3, 4, 5, 6]

# List comprehension
doubled = [take n * 2 each n in numbers if n > 2] # [6, 8, 10, 12]

# Set comprehension
evens = {take n each n in numbers if n % 2 == 0}   # {2, 4, 6}

# Lambdas
evens_only = numbers.filter(x -> x % 2 == 0)
```

---

## 🛠️ Standard Library (505+ Functions)

```nova
import math
import string
import list
import set
import file
import random
import time
import json

show math.root(256)                   # 16.0
show string.padL("42", 6, "0")         # 000042
show list.chunk([1, 2, 3, 4, 5], 2)    # [[1, 2], [3, 4], [5]]
show set.cart({1, 2}, {"a", "b"})     # [(1, a), (1, b), (2, a), (2, b)]
show random.otp(6)                     # 849201
show time.addDay(time.now(), 7)        # 7 days forward
show json.flat({a: {b: 10}})           # {a.b: 10}
```

---

## 🌐 Full-Stack Web & Backend Platform (V1.6)

### High-Speed SQLite ORM & Query Builder
```nova
import db

db.connect("app.db")
db.create("users", {id: "int primary", name: "text", role: "text"})
id1 = db.insert("users", {name: "Ravi", role: "admin"})
u1  = db.findOne("users", {id: id1})
show u1.name  # Ravi
```

### REST API Server with Routing Groups & Middleware
```nova
import server
import auth

app = server.new()
app.json().cors()

api = app.group("/api")
api.get("/users/:id", (req, res) -> {
    user = db.findOne("users", {id: req.params.id})
    res.json(user)
})

app.listen(3000)
```

---

## 🎨 V1.6.1 First UI Library — 80 Functions (Web, Desktop, Apps)

The UI module (`import ui`) provides an ultra-fluent, declarative component hierarchy compiling to responsive HTML5 & CSS3 with zero external tools.

### 1. App / Window (13 Functions)
| Function | Signature | Description |
| :--- | :--- | :--- |
| `ui.app` | `ui.app(title, w, h)` | Create main application / window (default: 800x600) |
| `ui.new` | `ui.new(title)` | Short alias for `ui.app` |
| `ui.window` | `ui.window(title, w, h)`| Desktop window constructor |
| `ui.page` | `ui.page(title)` | Web page container constructor |
| `app.size` | `app.size(w, h)` | Set window dimensions |
| `app.w` | `app.w(width)` | Set window width in pixels |
| `app.h` | `app.h(height)` | Set window height in pixels |
| `app.title` | `app.title(str)` | Update window header title |
| `app.bg` | `app.bg(color)` | Set window background color |
| `app.full` | `app.full()` | Fullscreen layout (100vw, 100vh) |
| `app.center` | `app.center()` | Center container on screen |
| `app.show` | `app.show()` | Compile & render UI tree to HTML document |
| `app.onResize`| `app.onResize(fn)` | Window resize event listener |

### 2. Basic Elements (16 Functions)
| Function | Signature | Description |
| :--- | :--- | :--- |
| `ui.text` | `ui.text("Hello")` | Inline span text |
| `ui.title` | `ui.title("Header")` | Heading 1 (`<h1>`) |
| `ui.subTitle`| `ui.subTitle("Sub")` | Heading 2 (`<h2>`) |
| `ui.para` | `ui.para("...")` | Paragraph (`<p>`) |
| `ui.bold` | `ui.bold("Bold")` | Bold text (`<b>`) |
| `ui.italic` | `ui.italic("Italic")` | Italic text (`<i>`) |
| `ui.link` | `ui.link("Text", "url")` | Hyperlink (`<a href>`) |
| `ui.img` | `ui.img("src", w, h)` | Image with optional dimensions |
| `ui.line` | `ui.line()` | Horizontal divider rule (`<hr>`) |
| `ui.space` | `ui.space(20)` | Vertical spacing block |
| `ui.box` | `ui.box()` | Generic container (`<div>`) |
| `ui.card` | `ui.card()` | Card with dark elevation & drop shadow |
| `ui.badge` | `ui.badge("NEW")` | Colored status badge |
| `ui.icon` | `ui.icon("home")` | Icon identifier tag |
| `ui.code` | `ui.code("x = 10")` | Formatted code block (`<pre><code>`) |
| `ui.alert` | `ui.alert("Warning")`| Accent alert banner |

### 3. Input Elements (11 Functions)
| Function | Signature | Description |
| :--- | :--- | :--- |
| `ui.input` | `ui.input("Placeholder")` | Text input |
| `ui.inputP` | `ui.inputP("Password")` | Password masked input |
| `ui.inputN` | `ui.inputN("Age")` | Numeric input |
| `ui.inputE` | `ui.inputE("Email")` | Email validated input |
| `ui.textArea`| `ui.textArea("Bio")` | Multi-line textarea |
| `ui.check` | `ui.check("Agree")` | Checkbox toggle with label |
| `ui.radio` | `ui.radio("Option")` | Radio button with label |
| `ui.select` | `ui.select(options, def)`| Select dropdown menu |
| `ui.slider` | `ui.slider(min, max, def)`| Range slider component |
| `inp.value` | `inp.value` (get/set) | Live input value |
| `inp.id` | `inp.id("field_id")` | Form element identifier |

### 4. Buttons (8 Functions)
| Function | Signature | Description |
| :--- | :--- | :--- |
| `ui.btn` | `ui.btn("Action")` | Standard neutral button |
| `ui.btnP` | `ui.btnP("Primary")` | Accent primary blue button |
| `ui.btnS` | `ui.btnS("Small")` | Compact small button |
| `ui.btnL` | `ui.btnL("Large")` | Prominent large button |
| `ui.btnD` | `ui.btnD("Disabled")`| Disabled button state |
| `ui.btnI` | `ui.btnI("Save", "icon")`| Icon + text button |
| `ui.btnLink` | `ui.btnLink("Go", "url")`| Link styled as a button |
| `ui.btnClose`| `ui.btnClose()` | Circular close button (&times;) |

### 5. Layout Containers (11 Functions)
| Function | Signature | Description |
| :--- | :--- | :--- |
| `ui.row` | `ui.row()` | Flex horizontal row container |
| `ui.col` | `ui.col()` | Flex vertical column container |
| `ui.grid` | `ui.grid(rows, cols)` | CSS Grid matrix container |
| `ui.stack` | `ui.stack()` | Z-index layered stack |
| `ui.center` | `ui.center()` | Centered content container |
| `ui.scroll` | `ui.scroll()` | Scrollable overflow container |
| `ui.form` | `ui.form()` | Interactive form wrapper |
| `ui.list` | `ui.list([items])` | Dynamic list from comprehension |
| `ui.table` | `ui.table()` | Data table (`.head()`, `.row()`) |
| `grid.add` | `grid.add(el, r, c)` | Position element at grid coordinate |
| `el.clear` | `el.clear()` | Remove all children from container |

### 6. Fluent Styles (30 Chainable Methods)
All style methods return `this` for chaining:
```nova
card = ui.card().bg("#1e293b").color("#ffffff").pad(20).margin(10).round(12).w(400).center()
```
- **Colors**: `.bg(color)`, `.color(color)`
- **Sizing**: `.w(px)`, `.h(px)`, `.size(w, h)`, `.wFull()`, `.hFull()`, `.wHalf()`, `.sizeFull()`, `.fontSize(px)`
- **Spacing**: `.pad(all)`, `.pad(v, h)`, `.padL(px)`, `.padR(px)`, `.padT(px)`, `.padB(px)`, `.margin(px)`, `.marginC()`
- **Borders**: `.border(w, color)`, `.borderC(color)`, `.borderW(px)`, `.round(px)`, `.roundFull()`, `.roundT(px)`
- **Display & Alignment**: `.show()`, `.hide()`, `.flex()`, `.center()`, `.left()`, `.right()`, `.top()`, `.bottom()`, `.pos(x, y)`, `.posA()`, `.posR()`
- **Typography**: `.bold()`, `.font("Inter")`, `.align("center")`
- **Tree Chaining**: `.addTo(parent)`

### 7. Events (9 Functions)
- `.onClick(() -> ...)`
- `.onChange((val) -> ...)`
- `.onEnter((val) -> ...)`
- `.onFocus(() -> ...)`
- `.onBlur(() -> ...)`
- `.onSubmit((data) -> ...)`
- `.onHover(() -> ...)`
- `.onLeave(() -> ...)`
- `ui.key("enter").onPress(() -> ...)`

---

## 📱 5 Real-World UI Example Applications

### 1. `login.nova` (Authentication Portal)
```nova
import ui

app = ui.app("Nova Auth Portal", 450, 400).bg("#0f172a")
card = ui.card().w(380).pad(24).round(12).bg("#1e293b").center()

card.add(ui.title("Welcome Back").center().color("#38bdf8").fontSize(26))
card.add(ui.para("Sign in to your account").center().color("#94a3b8").fontSize(14))
card.add(ui.space(12))

userInput = ui.input("Username or Email").wFull().margin(8).id("user")
passInput = ui.inputP("Password").wFull().margin(8).id("pass")
loginBtn  = ui.btnP("Sign In").wFull().margin(12).round(8).fontSize(16)

loginBtn.onClick(() -> show "Login user:", userInput.value)

card.add(userInput)
card.add(passInput)
card.add(loginBtn)

app.add(card)
app.show()
```

### 2. `todo.nova` (Reactive Task Manager)
```nova
import ui

app = ui.app("Nova Todo Pro", 600, 700).bg("#0f172a")
card = ui.card().w(520).pad(20).round(10).bg("#1e293b").center()

tasks = ["Complete Nova V1.6.1 UI", "Write integration documentation", "Deploy release bundle"]
listBox = ui.col().margin(10)

each t in tasks:
    itemCard = ui.box().bg("#334155").pad(10).round(6).wFull()
    itemCard.add(ui.row().add(ui.check(t)).add(ui.btnS("Delete").bg("#ef4444")))
    listBox.add(itemCard)
end

card.add(ui.title("Task Manager").color("#60a5fa"))
card.add(listBox)
app.add(card)
app.show()
```

### 3. `dashboard.nova` (Executive Analytics)
```nova
import ui

app = ui.app("Nova Cloud Dashboard", 900, 750).bg("#0f172a")
col = ui.col().w(840).center()

# Metric cards
metrics = ui.row()
metrics.add(ui.card().w(260).pad(16).bg("#1e293b").add(ui.para("USERS")).add(ui.title("128,450").color("#ffffff")))
metrics.add(ui.card().w(260).pad(16).bg("#1e293b").add(ui.para("REQUESTS")).add(ui.title("4.8M / day").color("#ffffff")))
metrics.add(ui.card().w(260).pad(16).bg("#1e293b").add(ui.para("CPU LOAD")).add(ui.title("24.5%").color("#ffffff")))
col.add(metrics)

# Table
table = ui.table()
table.head(["Service Name", "Latency", "Region", "Status"])
table.row(["auth-service-us", "12ms", "us-east-1", "HEALTHY"])
table.row(["api-gateway-eu", "24ms", "eu-central-1", "HEALTHY"])
col.add(ui.card().w(840).pad(16).bg("#1e293b").add(table))

app.add(col)
app.show()
```

### 4. `form.nova` (Registration Form)
```nova
import ui

app = ui.app("Nova Member Registration", 550, 680).bg("#0f172a")
formCard = ui.card().w(480).pad(24).round(12).bg("#1e293b").center()

f = ui.form()
f.add(ui.input("Full Name").wFull().margin(6).id("name"))
f.add(ui.inputE("name@example.com").wFull().margin(6).id("email"))
f.add(ui.inputN("Age (18+)").wFull().margin(6).id("age"))
f.add(ui.select(["Software Engineer", "Product Manager", "DevOps"], "Software Engineer").wFull().margin(6).id("role"))
f.add(ui.check("I agree to the Terms & Privacy Policy").margin(8).id("terms"))
f.add(ui.btnP("Submit Registration").wFull().margin(12))

f.onSubmit((data) -> show "Submitted:", data)
formCard.add(f)
app.add(formCard)
app.show()
```

### 5. `layout.nova` (Layout Showcase)
```nova
import ui

app = ui.app("Nova Layout Showcase", 900, 850).bg("#0f172a")
container = ui.col().w(840).center().pad(16)

# Grid Demo
grid = ui.grid(2, 2).wFull()
grid.add(ui.card().bg("#1e293b").pad(16).add(ui.title("Cell (1,1)").fontSize(18)))
grid.add(ui.card().bg("#1e293b").pad(16).add(ui.title("Cell (1,2)").fontSize(18)))
grid.add(ui.card().bg("#1e293b").pad(16).add(ui.title("Cell (2,1)").fontSize(18)))
grid.add(ui.card().bg("#1e293b").pad(16).add(ui.title("Cell (2,2)").fontSize(18)))
container.add(grid)

# Scroll Demo
scroll = ui.scroll().h(120).bg("#1e293b").pad(12).wFull()
each i in [1, 2, 3, 4, 5]:
    scroll.add(ui.box().bg("#334155").pad(8).round(4).margin(4).add(ui.text("Log item #{i}")))
end
container.add(scroll)

app.add(container)
app.show()
```

---

## 🕹️ V1.7 Game Engine Roadmap (40 Functions Preview)

The upcoming **Nova V1.7** release will introduce the dedicated `game` library (`import game`) for 2D/3D graphics, physics simulations, particle engines, sound effects, and gamepads.

> **Design Principle:**
> `import ui` handles menus, HUD overlays, dialogs, and settings.
> `import game` handles render loops, physics, sprite sheets, 3D meshes, and input controllers.

### Planned Game API Preview (40 Functions):
1. **Window & Loop (8)**: `game.win(title, w, h)`, `game.loop(fps, (dt) -> ...)`, `game.stop()`, `game.fps()`, `game.dt()`, `game.clear()`, `game.bg(c)`, `game.full()`
2. **2D Sprites & Drawing (10)**: `game.sprite(img, x, y)`, `game.rect(x, y, w, h)`, `game.circle(x, y, r)`, `game.line(x1, y1, x2, y2)`, `game.draw(sprite)`, `game.tint(color)`, `game.scale(s)`, `game.rotate(deg)`, `game.flipX()`, `game.flipY()`
3. **3D Models & Camera (6)**: `game.model(path)`, `game.cam(x, y, z)`, `game.light(type, pos)`, `game.mesh(geom)`, `game.material(tex)`, `game.lookAt(target)`
4. **Physics & Collision (8)**: `game.body(sprite, "dynamic")`, `game.gravity(gx, gy)`, `game.collide(b1, b2)`, `game.vel(vx, vy)`, `game.acc(ax, ay)`, `game.mass(m)`, `game.bounce(e)`, `game.raycast(from, to)`
5. **Controllers & Input (8)**: `game.joy()`, `game.btn("A")`, `game.btn("B")`, `game.keyDown(key)`, `game.keyPress(key)`, `game.mousePos()`, `game.mouseDown()`, `game.vibrate(ms)`

---

## 🏁 Verification & Test Execution

Run the complete Nova test suite and UI example applications:

```powershell
# Run 5 UI Applications
python nova_interpreter.py login.nova
python nova_interpreter.py todo.nova
python nova_interpreter.py dashboard.nova
python nova_interpreter.py form.nova
python nova_interpreter.py layout.nova

# Run Full Test Suites
python nova_interpreter.py test_v16_web.nova
python nova_interpreter.py test_v15_stdlib.nova
python nova_interpreter.py test_v14.nova
python nova_interpreter.py test.nova
```
