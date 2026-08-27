# Nova Programming Language - V1.4 Core Features - Full Doc
### Class, Advanced Data Collection, Enum, Throw/Error, Interpolation

---
## 1. CLASS - Full - V1.4

### Basic Class
```nova
class Person:
    name = "Ravi"
    age = 21

    init(n, a): # constructor
        name = n
        age = a
    end

    def greet():
        show "Hi, I am {name}" # interpolation
    end

    def getAge():
        return age
    end
end

p = Person("Ravi", 21)
p.greet() # Hi, I am Ravi
show p.name # Ravi
```

### Class with Private/Public
```nova
class Bank:
    public balance = 0
    private pin = 1234 # private - only inside class

    def deposit(amount):
        balance += amount
    end

    def showBalance():
        show balance
    end

    private def checkPin(p):
        return p == pin
    end
end
```

### Inheritance - extends
```nova
class Animal:
    def sound():
        show "Some sound"
    end
end

class Dog extends Animal:
    def sound(): # override
        show "Bark"
    end

    def run():
        show "Dog runs"
    end
end

d = Dog()
d.sound() # Bark
d.run()
```

### Super - parent call
```nova
class Cat extends Animal:
    def sound():
        super.sound() # call parent sound
        show "Meow"
    end
end
```

### Static + Get/Set
```nova
class Math:
    static pi = 3.14

    static def square(n):
        return n * n
    end

    get name(): # getter
        return "Ravi"
    end

    set name(v): # setter
        name = v
    end
end

show Math.pi # 3.14
show Math.square(5) # 25
```

### Class Features - All V1.4
```nova
# init, def, public, private, static, extends, super, get, set
# this keyword
class A:
    x = 10
    def showX():
        show this.x # this = current object
    end
end
```

---
## 2. ADVANCED METHODS OF DATA COLLECTION - List, Set, Map, Tuple - V1.4

### List Advanced - 20 Methods - V1.4
```nova
nums = [3,1,2,2]

# Advanced filter/map with take/from/each - YOUR syntax
[take x*2 each x in nums] # [6,2,4,4]
[take x each x in nums if x > 2] # [3]
[take x*2 each x in nums if x > 1] # with both

# Chaining
nums.filter(x > 1).map(x * 2).sort() # chain

# Advanced methods
nums.unique() # [3,1,2] - remove dup
nums.freq() # {3:1,1:1,2:2} - frequency map
nums.group(x -> x%2) # {1:[3,1],0:[2,2]} - group by even/odd
nums.sum() # 8
nums.avg() # 2
nums.max() # 3
nums.min() # 1
nums.prod() # 12
nums.flat() # [[1,2],[3]] -> [1,2,3]
nums.flatMap(x -> [x, x*2]) # [3,6,1,2,2,4,2,4]
nums.chunk(2) # [[3,1],[2,2]] - chunk size 2
nums.window(2) # [[3,1],[1,2],[2,2]] - sliding window
nums.zip([4,5,6,7]) # [[3,4],[1,5],[2,6],[2,7]]
nums.pair() # [[3,1],[1,2],[2,2]] - pairs
nums.hasAll([1,2]) # true
nums.hasAny([5,3]) # true
nums.countIf(x > 1) # 3 - count with condition
nums.find(x > 1) # 3 - first find
nums.findLast(x > 1) # 2 - last find
nums.findIndex(x > 1) # 0
nums.findAll(x > 1) # [3,2,2]
nums.every(x > 0) # true if all >0
nums.some(x > 2) # true if some >2
```

### Set Advanced - 15 Methods - V1.4
```nova
s1 = {1,2,3}
s2 = {3,4,5}

# Your operators
s1.U(s2) # {1,2,3,4,5}
s1 | s2 # same
s1.N(s2) # {3}
s1 & s2 # same
s1 - s2 # {1,2}
s1.diff(s2) # {1,2,4,5}
s1 ^ s2 # same

# Advanced
s1.isSub(s2) # false - is subset
s1.isSuper({1,2}) # true - is superset
s1.isDisjoint({4,5}) # true if no common
s1.power() # {{},{1},{2},{3},{1,2}...} - all subsets
s1.cart(s2) # {(1,3),(1,4)...} - cartesian product
s1.filter(x > 1) # {2,3}
s1.map(x*2) # {2,4,6}
{take x*2 each x in s1} # {2,4,6} - set comprehension
{take x each x in s1 if x > 1} # {2,3}
s1.sum() # 6
s1.toListS() # [1,2,3] sorted list from set
```

### Map Advanced - 20 Methods - V1.4
```nova
m = {name:"Ravi", age:21, city:"Hyd"}

# Advanced get/set with path
m.get("name") # Ravi
m.getPath("a.b.c") # nested get
m.set("age",22) # set
m.setPath("a.b.c",10) # nested set

# Advanced methods
m.keys() # [name,age,city]
m.values() # [Ravi,21,Hyd]
m.items() # [[name,Ravi],[age,21]...]
m.has("name") # true
m.hasValue("Ravi") # true
m.size # 3
m.isEmpty() # false
m.merge({phone:"123"}) # {name:Ravi,age:21,city:Hyd,phone:123}
m.mergeAll([{a:1},{b:2}])
m.filter((k,v) -> v > 20) # filter by value
m.map((k,v) -> v*2) # map values
m.mapKeys(k -> k.upper()) # [NAME,AGE,CITY]
m.mapValues(v -> v*2)
m.groupBy((k,v) -> type(v)) # group by type
m.invert() # {Ravi:name,21:age}
m.pick(["name","age"]) # {name:Ravi,age:21} - pick keys
m.omit(["age"]) # {name:Ravi,city:Hyd} - remove keys
m.toList() # [{key:name,val:Ravi}...]
m.fromList([["name","Ravi"]]) # {name:Ravi}
m.copy()
m.clear()
m.equals({name:"Ravi",age:21,city:"Hyd"}) # true
m.toStr() # "{name:Ravi,age:21}"
m.freq() # if values repeat - frequency
m.flat() # flatten nested map {a:{b:1}} -> {a.b:1}
```

### Tuple Advanced - 10 Methods - V1.4
```nova
t = (1,2,3)

t.size # 3
t.first() # 1
t.last() # 3
t.at(1) # 2
t.has(2) # true
t.index(2) # 1
t.toList() # [1,2,3]
t.toSet() # {1,2,3}
t.sum() # 6
t.max() # 3
t.min() # 1
t.slice(1,2) # (2,3)
(t1 + t2) # concat tuples
t1 * 2 # (1,2,3,1,2,3)
```

---
## 3. ENUM - V1.4 - Your Request

### Basic Enum
```nova
enum Color:
    RED
    GREEN
    BLUE
end

c = Color.RED
show c # RED

if c == Color.RED:
    show "Stop"
end

choose c:
    when Color.RED: show "Stop"
    when Color.GREEN: show "Go"
    when Color.BLUE: show "Wait"
end
```

### Enum with Values
```nova
enum Status:
    OK = 200
    NOT_FOUND = 404
    ERROR = 500
end

show Status.OK # 200
show Status.OK.value # 200
show Status.OK.name # "OK"

enum Role:
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"
end

# Enum with methods
enum Planet:
    MERCURY = 1
    VENUS = 2
    EARTH = 3

    def isEarth():
        return this == Planet.EARTH
    end
end

p = Planet.EARTH
show p.isEarth() # true
```

### Enum Advanced
```nova
enum Day:
    MON
    TUE
    WED
    THU
    FRI
    SAT
    SUN

    def isWeekend():
        return this == Day.SAT or this == Day.SUN
    end
end

# Enum iteration
each d in Day.values(): # [MON,TUE,WED,THU,FRI,SAT,SUN]
    show d
end

Day.count() # 7
Day.has("MON") # true
Day.fromName("MON") # Day.MON
Day.fromValue(0) # Day.MON - index
```

---
## 4. THROW / ERROR - Try Catch Finally Throw - V1.4

### Basic Throw
```nova
def checkAge(age):
    if age < 18:
        throw "Age must be 18+"
    end
    show "OK"
end

try:
    checkAge(15)
catch e:
    show e # Age must be 18+
end
```

### Error Object
```nova
class Error:
    msg = ""
    code = 0
    init(m,c):
        msg = m
        code = c
    end
end

def divide(a,b):
    if b == 0:
        throw Error("Cannot divide by zero", 1001)
    end
    return a / b
end

try:
    show divide(10,0)
catch e:
    show e.msg # Cannot divide by zero
    show e.code # 1001
end
```

### Try Catch Finally - Full
```nova
try:
    f = open("data.txt")
    show f.read()
catch e:
    show "File error: {e}"
finally:
    f.close() # always run
    show "Done"
end

# Multiple catch
try:
    riskyCode()
catch FileError as fe:
    show "File error"
catch NetworkError as ne:
    show "Network error"
catch e:
    show "Other error: {e}"
end

# Throw types
throw "Simple string error"
throw 404 # number error
throw {code:404, msg:"Not found"} # map error
throw Error("Custom", 500) # error object
```

### Built-in Errors
```nova
# Nova built-in error types
FileNotFoundError
PermissionError
ValueError
TypeError
IndexError
KeyError
ZeroDivError
NetworkError
```

### Assert - for checking
```nova
assert age > 18, "Age must be 18+" # throw if false
assert hasFile("data.txt"), "File missing"
```

---
## 5. INTERPOLATION - V1.4 - String {var}

### Basic Interpolation - {}
```nova
name = "Ravi"
age = 21

show "Hi, I am {name}" # Hi, I am Ravi
show "I am {age} years old" # I am 21 years old
show "I am {name}, age {age}" # I am Ravi, age 21

# Expression inside {}
a = 10
b = 20
show "Sum = {a + b}" # Sum = 30
show "Max = {max(a,b)}" # Max = 20

# Map access
m = {name:"Ravi"}
show "Name {m.name}" # Name Ravi

# List access
nums = [1,2,3]
show "First {nums[0]}" # First 1

# Function call inside {}
def getName():
    return "Ravi"
end
show "Name {getName()}" # Name Ravi
```

### Advanced Interpolation
```nova
# Format
price = 19.5
show "Price ${price}" # Price $19.5
show "Price {price} USD" # Price 19.5 USD

# Multi-line interpolation
msg = "
Name: {name}
Age: {age}
City: {city}
"

# Interpolation in file path
fileName = "data"
open("{fileName}.txt").read() # open data.txt

# Interpolation with calculation
show "Next year {age + 1}" # Next year 22
show "Double {age * 2}" # Double 42

# No interpolation with single quotes - raw
show '{name}' # {name} - not interpolated - raw string
show "{name}" # Ravi - interpolated - double quotes interpolate
```

### Interpolation vs Concatenation - Why Better
```nova
# Old way - concatenation - hard
show "Hi " + name + " age " + age # hard

# Nova way - interpolation - easy
show "Hi {name} age {age}" # easy - readable

# Python way: f"Hi {name}"
# Nova way: "Hi {name}" - no f needed - auto interpolation with ""
```

---
## 6. V1.4 Complete Example - All Features Together
```nova
enum Role:
    ADMIN
    USER
end

class User:
    name = ""
    role = Role.USER

    init(n,r):
        name = n
        role = r
    end

    def greet():
        show "Hi {name}, role {role}"
        if role == Role.ADMIN:
            show "You are admin"
        else:
            show "You are user"
        end
    end

    def check():
        try:
            if name == "":
                throw "Name empty"
            end
            show "OK {name}"
        catch e:
            show "Error {e}"
        end
    end
end

# Advanced collection with take/each
users = [{name:"Ravi",age:21},{name:"Ram",age:17}]
adults = [take u each u in users if u.age > 18] # [{name:Ravi,age:21}]
names = [take u.name each u in users] # [Ravi,Ram]

each u in users:
    user = User(u.name, Role.USER)
    user.greet()
    user.check()
end
```

---
# End of V1.4 Doc
