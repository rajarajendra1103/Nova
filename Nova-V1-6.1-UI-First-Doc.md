# Nova V1.6 First - UI Library - Full Doc - For Apps, Desktop, Web
### Short Readable - Better Than HTML/CSS/JS - One UI for All Platforms

## Import
```nova
import ui
```

---
## 1. App / Window - Create App - 5 Functions
```nova
app = ui.app("My App", 800, 600) # title, width, height - works web + desktop + mobile
app = ui.new("My App") # short alias
app = ui.app("My App") # default size 800x600
app = ui.window("My App", 800, 600) # same as app

app.size(800,600) # set size width height
app.w(800) # width only
app.h(600) # height only
app.title("New Title") # set title
app.bg("white") # background color
app.full() # fullscreen
app.center() # center window
app.show() # show app
app.hide() # hide app
app.close() # close app
```

---
## 2. Basic Elements - 15 Functions - Like HTML but Short
```nova
ui.text("Hello World") # span - normal text
ui.title("Big Title") # h1 - big title
ui.subTitle("Small Title") # h2 - subtitle
ui.para("This is paragraph...") # p - paragraph
ui.bold("Bold Text") # b - bold
ui.italic("Italic") # i - italic
ui.link("Google", "https://google.com") # a - link text + url
ui.img("logo.png") # img - image from path
ui.img("logo.png", 100, 100) # img with width height
ui.line() # hr - horizontal line
ui.space() # blank space - br
ui.space(20) # space with height 20
ui.box() # div - container box
ui.card() # card with shadow - div with style
ui.badge("New") # small badge
ui.icon("home") # icon - home, search, user etc
ui.code("print('hi')") # code block
ui.alert("Hi") # alert popup
```

---
## 3. Input Elements - 10 Functions - For Forms
```nova
ui.input("Enter name") # text input - placeholder
ui.inputP("Password") # password input
ui.inputN("Age") # number input
ui.inputE("Email") # email input
ui.textArea("Message") # textarea - big text area
ui.check("I agree") # checkbox - label
ui.radio("Male") # radio button
ui.select(["Male","Female","Other"]) # select dropdown - list
ui.select(["Red","Green","Blue"], "Red") # select with default
ui.slider(0,100) # slider min 0 max 100
ui.slider(0,100,50) # slider with default 50

# Get / Set Value
inp = ui.input("Name")
show inp.value # get value
inp.value = "Ravi" # set value
inp.value = "" # clear
inp.placeholder = "New placeholder" # set placeholder
```

---
## 4. Button - 8 Functions
```nova
ui.btn("Click Me") # normal button
ui.btnP("Primary") # primary button - blue
ui.btnS("Small") # small button
ui.btnL("Large") # large button
ui.btnD("Disabled") # disabled button
ui.btnI("Home", "home") # button with icon - text + icon name
ui.btnLink("Click", "https://google.com") # button as link
ui.btnClose() # X close button

# Click Event
btn = ui.btn("Click")
btn.onClick(() -> {
    show "Clicked"
})

btn.onClick((e) -> {
    show "Clicked {e}"
})

# Short chain
ui.btn("Click").onClick(() -> show "Hi").addTo(app)
```

---
## 5. Layout - Row Col Box Grid - 10 Functions - Most Important
```nova
# Row - Horizontal layout - side by side
row = ui.row()
row.add(ui.text("Left"))
row.add(ui.text("Right"))
app.add(row)

# Row short chain
ui.row().add(ui.text("A")).add(ui.text("B")).addTo(app)

# Col - Vertical layout - top to bottom
col = ui.col()
col.add(ui.title("Top"))
col.add(ui.text("Bottom"))
app.add(col)

# Box - Container div - with style
box = ui.box()
box.add(ui.text("Inside box"))
app.add(box)

# Card - Box with shadow + round
card = ui.card()
card.add(ui.title("Card Title"))
card.add(ui.text("Card content"))
app.add(card)

# Grid - 2D grid layout - rows x cols
grid = ui.grid(2,3) # 2 rows 3 cols
grid.add(ui.text("1"), 0,0) # add at row 0 col 0
grid.add(ui.text("2"), 0,1) # row 0 col 1
grid.add(ui.text("3"), 0,2) # row 0 col 2
grid.add(ui.text("4"), 1,0) # row 1 col 0
app.add(grid)

# Stack - Stack items - z-index
stack = ui.stack()
stack.add(ui.box().bg("red").w(100).h(100))
stack.add(ui.box().bg("blue").w(50).h(50))
app.add(stack)

# Center - Center container
center = ui.center()
center.add(ui.text("Centered"))
app.add(center)

# Scroll - Scrollable container
scroll = ui.scroll()
scroll.add(ui.text("Long content..."))
scroll.h(200) # height 200 with scroll
app.add(scroll)
```

---
## 6. Style - 30 Functions - Chain - Short Readable
```nova
box = ui.box()

# Background / Color
box.bg("blue") # background blue - name
box.bg("#ff0000") # background hex
box.bg("rgb(255,0,0)") # rgb
box.color("white") # text color white
box.colorR("red") # short alias - color red
box.colorB("blue") # color blue

# Size - Width Height
box.w(200) # width 200px
box.h(100) # height 100px
box.size(200,100) # width 200 height 100
box.wFull() # width 100%
box.hFull() # height 100vh
box.wHalf() # width 50%
box.sizeFull() # width 100% height 100%

# Padding
box.pad(10) # padding 10 all sides
box.padL(10) # padding left 10
box.padR(10) # padding right 10
box.padT(10) # padding top 10
box.padB(10) # padding bottom 10
box.pad(10,20) # padding vertical 10 horizontal 20

# Margin
box.margin(10) # margin 10 all sides
box.marginL(10) # margin left
box.marginR(10) # margin right
box.marginT(10) # margin top
box.marginB(10) # margin bottom
box.marginC() # margin auto center - center box

# Border
box.border(1) # border 1px solid black
box.border(1, "red") # border 1px red
box.borderC("red") # border color red
box.borderW(2) # border width 2
box.round(10) # border radius 10
box.roundFull() # border radius 50% - circle
box.roundT(10) # radius top only

# Display / Position
box.show() # display block
box.hide() # display none
box.flex() # display flex
box.center() # center content + self - text-align center + margin auto
box.left() # align left
box.right() # align right
box.top() # align top
box.bottom() # align bottom
box.pos(10,20) # position absolute x=10 y=20
box.posA(10,20) # position absolute
box.posR() # position relative

# Text style
box.bold() # font bold
box.size(16) # font size 16px - overload but context
box.fontSize(16) # font size 16px
box.font("Arial") # font family
box.align("center") # text align center

# Chain - All in 1 line - Short
ui.box().bg("blue").color("white").pad(10).round(10).w(200).h(100).center().add(ui.text("Hi")).addTo(app)
```

---
## 7. Events - 10 Functions - onClick onChange onSubmit
```nova
# Button click
btn = ui.btn("Click")
btn.onClick(() -> {
    show "Btn clicked"
})

# Input change
inp = ui.input("Name")
inp.onChange((val) -> {
    show "Typed {val} - val is new value"
})

# Input enter key pressed
inp.onEnter((val) -> {
    show "Enter pressed value {val}"
})

# Input focus / blur
inp.onFocus(() -> show "Focus")
inp.onBlur(() -> show "Blur")

# Form submit
form = ui.form()
nameIn = ui.input("Name").id("name")
emailIn = ui.input("Email").id("email")
form.add(nameIn)
form.add(emailIn)
form.add(ui.btn("Submit"))

form.onSubmit((data) -> {
    show data # {name:"Ravi", email:"..."}
})

# Box hover
box = ui.box().bg("blue").w(100).h(100)
box.onHover(() -> {
    box.bg("red")
})
box.onLeave(() -> {
    box.bg("blue")
})

# Click on box
box.onClick(() -> show "Box clicked")

# Key press - global
ui.key("enter").onPress(() -> show "Enter pressed")
ui.key("escape").onPress(() -> show "Escape")

# Resize
app.onResize((w,h) -> show "Resize {w} {h}")
```

---
## 8. List / Form / Table - 10 Functions
```nova
# List - auto render list - vertical
list = ui.list()
list.add(ui.text("Item 1"))
list.add(ui.text("Item 2"))
app.add(list)

# List from array with take each - YOUR Nova syntax
users = ["Ravi","Ram","Sita"]
list = ui.list([take ui.text(u) each u in users])
app.add(list)

# Or each loop
list = ui.list()
each u in users:
    list.add(ui.text(u))
end
app.add(list)

# Form - container for inputs
form = ui.form()
form.add(ui.input("Name").id("name"))
form.add(ui.input("Email").id("email"))
form.add(ui.btnP("Submit"))
app.add(form)

form.onSubmit((data) -> {
    show "Form {data.name} {data.email}"
})

# Table - simple table
table = ui.table()
table.head(["Name","Age","City"]) # header
table.row(["Ravi",21,"Araku"]) # row
table.row(["Ram",20,"Vizag"])
table.row(["Sita",22,"Hyd"])
app.add(table)

# Table from list
users = [{name:"Ravi",age:21},{name:"Ram",age:20}]
table = ui.table(["Name","Age"]) # header
each u in users:
    table.row([u.name, u.age])
end
app.add(table)
```

---
## 9. Full Examples - 3 Real Apps - Ready to Run

### Example 1 - Login Page - 15 lines
```nova
import ui

app = ui.app("Login", 400, 300).center().bg("#f0f0f0")

card = ui.card().w(300).pad(20).round(10).center().marginT(50)
card.add(ui.title("Login").center())
card.add(ui.input("Username").id("user").wFull().marginB(10))
card.add(ui.inputP("Password").id("pass").wFull().marginB(10))
card.add(ui.btnP("Login").wFull().onClick(() -> {
    show "Login clicked"
}))

app.add(card)
app.show()
```

### Example 2 - Todo List - 30 lines - With take each
```nova
import ui

app = ui.app("Todo", 500, 600)

app.add(ui.title("My Todos").center())

row = ui.row().center().pad(10)
inp = ui.input("Enter todo").w(300)
addBtn = ui.btnP("Add")
row.add(inp).add(addBtn)
app.add(row)

listBox = ui.col().pad(10)
app.add(listBox)

todos = ["Buy milk", "Code Nova", "Learn UI"]

def render():
    listBox.clear()
    each t in todos:
        r = ui.row().pad(5).bg("#f9f9f9").round(5).marginB(5)
        r.add(ui.text(t).w(400))
        delBtn = ui.btnS("X").bg("red").color("white").onClick(() -> {
            todos.remove(t)
            render()
        })
        r.add(delBtn)
        listBox.add(r)
    end
end

addBtn.onClick(() -> {
    if inp.value != "":
        todos.add(inp.value)
        inp.value = ""
        render()
    end
})

render()
app.show()
```

### Example 3 - Dashboard - Row Col Card - 25 lines
```nova
import ui

app = ui.app("Dashboard", 800, 600).bg("#f5f5f5")

# Header
header = ui.row().bg("blue").color("white").pad(10).wFull()
header.add(ui.title("Dashboard").color("white"))
header.add(ui.space())
header.add(ui.btn("Logout").bg("white").color("blue"))
app.add(header)

# Stats row - 3 cards
statsRow = ui.row().pad(10)
statsRow.add(ui.card().w(200).pad(15).margin(10).add(ui.title("100")).add(ui.text("Users")))
statsRow.add(ui.card().w(200).pad(15).margin(10).add(ui.title("50")).add(ui.text("Posts")))
statsRow.add(ui.card().w(200).pad(15).margin(10).add(ui.title("200")).add(ui.text("Views")))
app.add(statsRow)

# Content row - table + form
contentRow = ui.row().pad(10)
table = ui.table(["Name","Age"]).w(400)
table.row(["Ravi",21])
table.row(["Ram",20])
contentRow.add(table)

form = ui.card().w(300).pad(15).marginL(20)
form.add(ui.subTitle("Add User"))
form.add(ui.input("Name").wFull().marginB(10))
form.add(ui.inputN("Age").wFull().marginB(10))
form.add(ui.btnP("Add").wFull())
contentRow.add(form)

app.add(contentRow)
app.show()
```

---
## Summary - UI Library - 80 Functions

| Category | Functions - Short |
| :--- | :--- |
| App | app(), new(), window(), size(), w(), h(), title(), bg(), full(), center(), show(), hide(), close() |
| Basic | text(), title(), subTitle(), para(), bold(), italic(), link(), img(), line(), space(), box(), card(), badge(), icon(), code(), alert() |
| Input | input(), inputP(), inputN(), inputE(), textArea(), check(), radio(), select(), slider() |
| Button | btn(), btnP(), btnS(), btnL(), btnD(), btnI(), btnLink(), btnClose() |
| Layout | row(), col(), box(), card(), grid(), stack(), center(), scroll(), form(), list(), table() |
| Style | bg(), color(), w(), h(), size(), wFull(), hFull(), pad(), padL/R/T/B, margin(), marginL/R/T/B, border(), borderC(), round(), roundFull(), show(), hide(), flex(), center(), left(), right(), pos(), bold(), fontSize(), align() |
| Events | onClick(), onChange(), onEnter(), onFocus(), onBlur(), onSubmit(), onHover(), onLeave(), key(), onResize() |

---
# End of UI First Doc
