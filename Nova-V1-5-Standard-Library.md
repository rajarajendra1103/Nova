# Nova Programming Language - V1.5 Standard Library - Full Doc
### Total 8 Libraries - 505 Functions - Short Readable - Better Than Python

---
## Nova Core Syntax - V1.5
```nova
# Variables
a = 10
name = "Ravi"

# Show - print
show "Hello Nova"

# Control Flow - No Python 'for' - Use from / each / keep
from 1 to 5 in i:
    show i
end

each x in [1,2,3]:
    show x
end

keep i < 5:
    i += 1
end

if age > 18:
    show "adult"
elsif age > 13:
    show "teen"
else:
    show "kid"
end

choose day:
    when "mon": show "Monday"
    when "fri": show "Friday"
    otherwise: show "Other"
end

try:
    throw "error"
catch e:
    show e
finally:
    show "done"
end

# Comprehension with take + each/from
[take x*2 each x in [1,2,3]] # [2,4,6]
[take x each x in nums if x > 2]
{take x each x in {1,2,3}} # for set

# File + cd
cd "folder"
cd ".."
goBack # alias for cd ".."
f = open("data.txt")
show f.read()
f.close()
show open("data.txt").read() # direct - no variable

# Data Types
list = [1,2,3]
tuple = (1,2,3)
set = {1,2,3}
map = {name: "Ravi", age: 21}
```

---
## 1. MATH - 63 Functions + Constants - import math

### Constants - 8
```nova
math.pi      # 3.14159
math.e       # 2.71828
math.tau     # 6.28318 = 2*pi
math.inf     # infinity
math.ninf    # -infinity
math.nan     # not a number
math.phi     # 1.618 golden ratio
math.deg     # 57.29 = 180/pi
```

### Basic - 10
```nova
math.root(16)      # 4 - sqrt
math.power(2,3)    # 8 - 2^3
math.abs(-5)       # 5
math.floor(3.7)    # 3
math.ceil(3.2)     # 4
math.round(3.6)    # 4
math.max(1,5,3)    # 5
math.min(1,5,3)    # 1
math.sum([1,2,3])  # 6
math.prod([2,3,4]) # 24
```

### Trigonometry - 12
```nova
math.sin(1)
math.cos(1)
math.tan(1)
math.asin(1)
math.acos(1)
math.atan(1)
math.atan2(1,1)
math.sinh(1)
math.cosh(1)
math.tanh(1)
math.toRad(180) # deg to rad
math.toDeg(3.14) # rad to deg
```

### Log/Exp - 8
```nova
math.exp(2)
math.log(10)       # ln
math.log10(100)    # 2
math.log2(8)       # 3
math.logBase(8,2)  # 3
math.exp2(3)       # 8
math.expm1(1)
math.log1p(1)
```

### More - 15
```nova
math.mod(10,3)     # 1
math.gcd(12,8)     # 4
math.lcm(4,6)      # 12
math.fact(5)       # 120
math.perm(5,2)     # 20
math.comb(5,2)     # 10
math.isEven(4)     # true
math.isOdd(3)      # true
math.isPrime(7)    # true
math.prime(10)     # [2,3,5,7]
math.clamp(15,1,10) # 10
math.lerp(0,10,0.5) # 5
math.sign(-5)      # -1
math.dist([0,0],[3,4]) # 5
math.hypot(3,4)    # 5
```

### Advanced - 10
```nova
math.cbrt(8)       # 2
math.nroot(16,4)   # 2
math.trunc(3.9)    # 3
math.frac(3.7)     # 0.7
math.toInt(3.9)    # 3
math.toFloat(3)    # 3.0
math.near(0.1+0.2,0.3) # true
math.range(1,5)    # [1,2,3,4,5]
math.range2(1,10,2) # [1,3,5,7,9]
math.rand()        # 0.0-1.0
```

---
## 2. STRING - 65 Functions

### Constants - 5
```nova
string.empty
string.space
string.digits
string.letters
string.lower
string.upper
```

### Case - 8
```nova
"hi".upper()   # HI
"HI".lower()   # hi
"hi there".title() # Hi There
"hi".cap()     # Hi
"hi".swap()    # hI
"Hi".isUpper() # false
"hi".isLower() # true
"HI".isTitle() # false
```

### Trim/Search - 14
```nova
" hi ".trim()      # hi
" hi ".trimL()     # "hi "
" hi ".trimR()     # " hi"
" hi ".trimAll()   # hi no spaces inside too
"__hi__".trimC("_") # hi - trim char
" hi ".len()       # 4
"hello".has("ell") # true
"hello".at(1)      # e
"hello".index("l") # 2
"hello".lastI("l") # 3
"hello".count("l") # 2
"hello".starts("he") # true
"hello".ends("lo") # true
"hello".isEmpty() # false
```

### Type Check - 4
```nova
"123".isDigit()   # true
"abc".isLetter()  # true
"a1".isAlNum()    # true
" ".isSpace()     # true
```

### Modify - 16
```nova
"a,b,c".split(",") # [a,b,c]
["a","b"].join(",") # a,b
"hi".repeat(3)     # hihihi
"Ravi".replace("a","o") # Rovi
"hello".replaceA("l","x") # hexxo - replace all
"hello".slice(1,3) # el
"hello".sliceFrom(2) # llo
"hello".sliceTo(3) # hel
"hello".reverse() # olleh
"hello".padL(10)  # "     hello"
"hello".padR(10)  # "hello     "
"hello".pad(10,"-") # --hello---
"hello".first()   # h
"hello".last()    # o
"hello".take(2)   # he
"hello".drop(2)   # llo
```

### More - 18
```nova
"hello".takeL(2) # lo - take last 2
"hello".dropL(2) # hel - drop last 2
"hello world".words() # [hello, world]
"hello world".wordC() # 2 - word count
"hello".codeAt(0) # 104
string.fromCode(104) # h
"hi".toBytes() # [104,105]
string.fromBytes([104,105]) # hi
"hello".toList() # [h,e,l,l,o]
"hello".equals("hello") # true
"Hello".equalsI("hello") # true ignore case
"hello".len() # 5
"hello".size # 5
"hi".isEmpty() # false
string.same("a","a") # true
"ab".add("c") # abc - add
"ab".addAt(1,"x") # axb
```

---
## 3. LIST - 68 Functions

### Create - 6
```nova
list.empty() # []
list.range(1,5) # [1,2,3,4,5]
list.range2(1,10,2) # [1,3,5,7,9]
list.repeat(0,5) # [0,0,0,0,0]
list.repeatI("hi",3) # [hi,hi,hi]
list.fromSet({1,2}) # [1,2]
```

### Basic - 12
```nova
nums = [3,1,2]
nums.size # 3
len(nums) # 3
nums.isEmpty() # false
nums.has(2) # true
nums.index(2) # 1
nums.lastI(2) # last index
nums.count(2) # count 2s
nums.first() # 3
nums.last() # 2
nums.at(1) # 1
nums.atL(1) # last 1 = 2
```

### Add/Remove - 12
```nova
nums.add(5) # add end
nums.addAt(1,10) # at index 1
nums.addList([4,5]) # add all
nums.remove(2) # remove value
nums.removeAt(1) # remove at
nums.removeF() # remove first
nums.removeL() # remove last
nums.removeAll(2) # remove all 2
nums.clear() # []
nums.pop() # remove last return it
nums.popAt(1) # remove at 1 return
nums.set(1,99) # set index 1 to 99
```

### Sort - 8
```nova
nums.sort() # [1,2,3] ascending mutate
nums.dsort() # [3,2,1] descending mutate - your keyword
nums.sorted() # new list ascending
nums.dsorted() # new list descending
nums.reverse() # reverse mutate
nums.reversed() # new reverse
nums.shuffle() # shuffle mutate
nums.shuffled() # new shuffle
```

### Transform - 14
```nova
nums.filter(x > 2) # [3]
nums.map(x * 2) # [6,2,4]
nums.mapI((x,i) -> x+i) # with index
[take x*2 each x in nums] # comprehension
[take x each x in nums if x > 2]
nums.keep(x > 1) # alias filter
nums.change(x*2) # alias map
nums.flat() # [[1,2],[3]] -> [1,2,3]
nums.flatMap(x -> [x,x*2])
nums.slice(1,3)
nums.sliceFrom(2)
nums.sliceTo(3)
nums.take(2) # first 2
nums.drop(2) # skip first 2
```

### Math/Check - 10
```nova
nums.sum() # 6
nums.prod() # 6
nums.max() # 3
nums.min() # 1
nums.avg() # 2
nums.hasAll([1,2]) # true
nums.hasAny([5,1]) # true
nums.unique() # remove dup
nums.freq() # {1:1,2:2}
nums.group(x -> x%2) # group by
```

### Join - 6
```nova
nums.join(",") # "3,1,2"
nums.toSet() # {3,1,2}
nums.toMap() # {0:3,1:1...}
nums.toStr() # "[3,1,2]"
nums.copy() # copy
list.same([1,2],[1,2]) # true
```

---
## 4. SET - 62 Functions - Your U N diff ^ | & -

### Operators - Your Design - 7
```nova
s1 = {1,2,3}
s2 = {3,4,5}
s1.U(s2)   # {1,2,3,4,5} - union - U
s1 | s2    # same - | union
s1.N(s2)   # {3} - intersection - N
s1 & s2    # same - & intersection
s1 - s2    # {1,2} - difference - -
s1.diff(s2) # {1,2,4,5} - symmetric diff
s1 ^ s2    # same - ^ symmetric diff
```

### Basic - 12
```nova
s1.size # 3
len(s1) # 3
s1.isEmpty() # false
s1.has(2) # true
s1.hasAll({1,2}) # true
s1.hasAny({5,2}) # true
s1.add(5)
s1.addAll({4,5})
s1.remove(2)
s1.removeAll({1,2})
s1.clear() # {}
s1.pop() # random pop
```

### Check - 14
```nova
s1.isSub({1,2,3,4}) # true - subset
s1.isSuper({1,2}) # true - superset
s1.isEqual({1,2,3}) # true
s1.isDisjoint({4,5}) # true if no common
s1.copy()
s1.toList() # [1,2,3]
s1.toListS() # [1,2,3] sorted
s1.sorted() # sorted new
s1.dsorted() # desc new
s1.filter(x > 1) # {2,3}
s1.map(x * 2) # {2,4,6}
s1.take(2) # {1,2}
s1.drop(1) # {2,3}
s1.slice(1,2)
```

### Math - 6
```nova
s1.sum() # 6
s1.max() # 3
s1.min() # 1
s1.avg() # 2
s1.same({1,2,3}) # true
s1.count(2) # 1
```

### Advanced - 23
```nova
s1.unionAll([{1},{2}])
s1.interAll([{1,2},{2,3}])
s1.diffAll([{1},{2}])
s1.power() # power set
s1.cart(s2) # cartesian product
s1.first()
s1.last()
s1.toStr() # "{1,2,3}"
s1.join(",") # "1,2,3"
s1.unique() # already unique
set.empty() # {}
set.range(1,5) # {1,2,3,4,5}
set.range2(1,10,2) # {1,3,5,7,9}
set.fromList([1,2,2,3]) # {1,2,3}
set.same(s1,s2)
s1.keep(x > 1) # filter alias
s1.change(x*2) # map alias
{take x each x in s1} # set comprehension
{take x each x in s1 if x > 1}
s1.copy()
s1.clear()
```

---
## 5. FILE + OS - 65 Functions - With cd

### Path cd - 8
```nova
cd "folder" # go folder
cd ".." # back
cd "/" # root
goBack # alias cd ".."
os.pwd() # current path
os.pathJoin("a","b") # a/b
os.pathBase("/a/b.txt") # b.txt
os.pathDir("/a/b.txt") # /a
```

### Open/Read/Write - 12
```nova
f = open("a.txt") # read mode
f = open("a.txt","write") # write delete old
f = open("a.txt","add") # append mode
f.read() # all
f.readLine() # one line
f.readLines() # [lines]
f.readBytes() # bytes
f.write("hi") # write
f.writeLine("hi") # write + \n
f.writeBytes([104,105])
f.close()
```

### Direct - 8
```nova
show open("a.txt").read() # direct - your idea
open("a.txt","write").write("hi").close() # chain
file.readA("a.txt") # read all direct
file.readL("a.txt",2) # line 2
file.writeA("a.txt","hi") # write all
file.add("a.txt","hi") # append
file.copy("a.txt","b.txt")
file.move("a.txt","b.txt")
```

### OS Check - 12
```nova
os.exists("a.txt")
os.isFile("a.txt")
os.isDir("folder")
os.size("a.txt") # bytes
os.time("a.txt") # modified time
os.create("a.txt") # create empty
os.remove("a.txt")
os.rename("a.txt","b.txt")
os.list() # list in cd
os.list("folder")
os.listAll() # with hidden
os.listDirs() # only dirs
```

### Dir - 10
```nova
os.makeDir("new")
os.makeDirs("a/b/c")
os.removeDir("folder") # empty
os.removeDirs("a/b") # recursive
os.isEmptyDir("folder")
os.copyDir("a","b")
os.moveDir("a","b")
os.dirSize("folder")
os.walk("folder") # all files recursive
os.walkFiles("folder")
```

### More - 15
```nova
file.hasText("a.txt","hi")
file.lineC("a.txt") # line count
file.wordC("a.txt") # word count
file.isEmpty("a.txt")
file.clear("a.txt")
os.tempFile()
os.tempDir()
os.homeDir()
os.absPath("a.txt")
os.relPath("/a/b")
os.sameFile("a.txt","b.txt")
os.canRead("a.txt")
os.canWrite("a.txt")
os.hide("a.txt")
os.unhide("a.txt")
```

---
## 6. RANDOM - 60 Functions

### Basic - 10
```nova
random.int(1,10) # 1-10
random.float() # 0.0-1.0
random.floatR(1,5) # 1.0-5.0
random.bool() # true/false
random.pick([1,2,3]) # one
random.pickN([1,2,3,4],2) # 2 no repeat - alias sample
random.pickR([1,2,3],2) # 2 can repeat
random.shuffle([1,2,3]) # mutate
random.shuffled([1,2,3]) # new
random.sample([1,2,3,4],2) # alias pickN
```

### String - 8
```nova
random.letter() # a-z
random.upperL() # A-Z - short
random.digit() # 0-9
random.char() # random char
random.str(5) # random string len 5
random.strUpper(5) # upper string
random.strNum(5) # number string
random.word() # random word
```

### More - 12
```nova
random.seed(10)
random.seedTime()
random.range(1,5) # pick from range
random.range2(1,10,2) # step range
random.bin() # 0 or 1
random.binA(5) # [0,1,0,1,1] - bin array
random.boolA(5) # [true,false...]
random.intA(5,1,10) # 5 ints
random.floatA(5) # 5 floats
random.color() # "#a3f4b2"
random.colorRGB() # [255,100,50]
random.uuid() # uuid
```

### Dist - 10
```nova
random.normal()
random.normalR(0,10)
random.gauss() # alias normal
random.uniform(1,10)
random.exp() # exponential
random.choice([1,2,3]) # alias pick
random.choices([1,2,3],2) # alias pickR
random.weight([1,2,3],[10,1,1]) # weighted pick
random.shuffleS([1,2,3],10) # shuffle with seed
random.clamp() # alias?
```

### Game - 10
```nova
random.dice() # 1-6
random.dice2() # 2 dice sum
random.coin() # head/tail
random.card() # "A heart"
random.cardN() # 1-13
random.suit() # heart/spade
random.lottery(1,50,6) # 6 nums
random.otp(6) # "483921"
random.pass(8) # password len 8
random.bin() # 0/1
```

### Extra - 10
```nova
random.time() # random time
random.date() # random date
random.day() # mon-sun
random.month()
random.year(2000,2026)
random.name()
random.firstN() # first name
random.lastN() # last name
random.email()
random.phone()
```

---
## 7. TIME - 62 Functions

### Now - 10
```nova
time.now()
time.date() # 2026-08-21
time.time() # 14:30:10
time.dateTime() # 2026-08-21 14:30:10
time.year() # 2026
time.month() # 8
time.day() # 21
time.hour() # 14
time.min() # 30
time.sec() # 10
time.milli() # ms
```

### Create - 10
```nova
time.make(2026,8,21)
time.makeT(14,30,10)
time.makeDT(2026,8,21,14,30,10)
time.fromStr("2026-08-21")
time.fromStamp(1234567890)
time.stamp() # sec now
time.stampM() # milli
time.today()
time.tomorrow()
time.yesterday()
```

### Add/Sub - 10
```nova
time.addDay(5)
time.addMonth(2)
time.addYear(1)
time.addHour(2)
time.addMin(30)
time.addSec(10)
time.subDay(5)
time.subMonth(2)
time.subYear(1)
time.diffDay("2026-08-21","2026-08-25") # 4
```

### Diff/Compare - 8
```nova
time.diffHour(t1,t2)
time.diffMin(t1,t2)
time.diffSec(t1,t2)
time.isBefore(t1,t2)
time.isAfter(t1,t2)
time.isSame(t1,t2)
time.isLeap(2024)
time.daysInMonth(2026,2) # 28
```

### Format - 8
```nova
time.format("YYYY-MM-DD")
time.formatT("HH:mm")
time.formatD("DD/MM/YYYY")
time.format12() # 2:30 PM
time.format24() # 14:30
time.weekDay() # mon
time.weekNum() # 1-7
time.monthName() # August
```

### Sleep - 8
```nova
time.sleep(1) # sec
time.sleepM(100) # milli
time.sleepU(1000) # micro
time.wait(1) # alias sleep
time.waitUntil("14:30")
time.timer() # start
time.timerEnd() # end return elapsed
time.elapsed()
```

### More - 8
```nova
time.zone()
time.zoneName() # IST
time.utc()
time.utcNow()
time.toUTC(t)
time.toLocal(t)
time.age("2000-01-01") # 26
time.isWeekend()
```

---
## 8. JSON - 60 Functions

### Basic - 10
```nova
data = {name:"Ravi", age:21}
json.text(data) # map to text
json.map(text) # text to map
json.read("a.json") # file to map
json.write("a.json",data) # map to file
json.pretty(data) # pretty text
json.prettyW("a.json",data) # pretty write
json.minify(text) # remove spaces
json.isValid(text) # true if valid
json.isEmpty(data)
json.size(data) # 3
```

### Keys/Values - 10
```nova
json.has(data,"name")
json.keys(data) # [name,age]
json.values(data) # [Ravi,21]
json.hasValue(data,"Ravi")
json.get(data,"name") # Ravi
json.getOr(data,"x","default")
json.getPath(data,"a.b.c")
json.set(data,"age",22)
json.setPath(data,"a.b.c",10)
json.remove(data,"age")
```

### Modify - 10
```nova
json.add(data,"phone","123")
json.addIfNot(data,"age",21)
json.merge(d1,d2)
json.mergeAll([d1,d2,d3])
json.copy(data)
json.copyD(data) # deep copy
json.clear(data)
json.equals(d1,d2)
json.same(d1,d2)
json.clone(data)
```

### List of JSON - 10
```nova
listData = [{a:1},{a:2}]
json.listText(listData)
json.listMap(text)
json.listRead("a.json")
json.listWrite("a.json",listData)
json.listHas(listData,"a")
json.listGet(listData,0)
json.listFilter(listData, age > 20)
json.listMapE(listData, age*2)
json.listKeys(listData)
json.listVals(listData,"age")
```

### Advanced - 10
```nova
json.toList(data) # [{key:name,val:Ravi}...]
json.fromList([[name,Ravi]])
json.flat({a:{b:1}}) # {a.b:1}
json.unflat({"a.b":1}) # {a:{b:1}}
json.paths(data) # all paths
json.type(data,"name") # string/int/map/list
json.isMap(data)
json.isList(data)
json.isStr(data)
json.toStr(data) # alias text
```

### File Extra - 10
```nova
json.addF("a.json",{d:4}) # append
json.readLines("a.json")
json.writeLines("a.json",[d1,d2])
json.lineC("a.json")
json.hasFile("a.json")
json.fileSize("a.json")
json.backup("a.json")
json.restore("a.json")
json.diff(d1,d2) # what changed
json.patch(d1,diff)
```

---
## Final V1.5 Summary
- 8 Libraries
- 505+ Functions
- All short readable: root, power, pick, trim, sort, dsort, U, N, diff, |, &, -, ^, text, map
- Control flow: from to in, each in, keep, breck, skip
- Comprehension: [take x each x in nums if cond]
- Set operators: U = union = | , N = intersection = & , - = difference, diff/^ = symmetric diff
- File: cd + open + read + write + close + direct open().read() - no variable needed

# End of Nova V1.5 Doc
