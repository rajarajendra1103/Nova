# NOVA LANGUAGE V1.0 - OFFICIAL KEYWORDS DOC
# Basic Version - All Lower Case

## 1. TYPES - 9 keywords
| Keyword | Use | Example |
| int | integer | age: int = 21 |
| float | decimal | price: float = 10.5 |
| string | text | name: string = "Ravi" |
| bool | true/false | active: bool = true |
| list | list | a = [1,2,3] |
| set | set | s = {1,2,3} |
| map | key:value | m = {name: "Ravi"} |
| tuple | immutable list | t = (1,2,3) |
| const | immutable var | const pi = 3.14 |

## 2. VALUES - 3 keywords
| true | bool true | active = true |
| false | bool false | active = false |
| none | empty/null | data = none |

## 3. BRACKETS - Auto Detection
| [] | list | a = [1,2,3] |
| {} | set | s = {1,2,3} |
| {k:v} | map | m = {age: 21} |
| () | tuple | t = (1,2,3) |

## 4. METHODS / CONVERSIONS - 18 keywords
|.list | to list | input().list |
|.set | to set | input().set |
|.tuple | to tuple | input().tuple |
|.string | to string | x.string |
|.int | to int | x.int |
|.float | to float | x.float |
|.bool | to bool | x.bool |
|.map(key) | get keys from list | k.map(key) |
|.map(value) | get values from list | l.map(value) |
|.size | length | a.size |
|.get | get by index | a.get(0) |
|.add | add item | a.add(5) |
|.remove | remove item | a.remove(5) |
|.has | contains check | a.has(5) |
|.upper | upper case | s.upper() |
|.lower | lower case | s.lower() |
|.trim | trim spaces | s.trim() |
|.split | split | s.split(",") |
|.replace | replace | s.replace("a","b") |

## 5. SLICING - 3 keywords
| to | range to | [1 to 5], [2 to], [to 3] |
| stp | step | [0 to 5 stp 2] |
| [::-1] | reverse | a[::-1] or [to stp -1] |

Final Slices:
[2 to] = 2 to end
[to 3] = start to 3
[to] = full copy
[1 to 3] = 1 to 3
[0 to 5 stp 2] = step 2
[::-1] = reverse
[to stp -1] = reverse

## 6. OPERATORS - 17 keywords
| + - * / | basic math | a + b |
| // | floor division | 10 // 3 = 3 |
| % | remainder | 10 % 3 = 1 |
| ** | power | 2 ** 3 = 8 |
| = | assign | a = 5 |
| += -= *= /= //= %= | shortcut assign | a += 5 |
| ==!= > < >= <= | compare | if a == b: |
| and or not | logic | if a and b: |

## 7. CONTROL FLOW - 15 keywords
| if | if condition | if age > 18: |
| elsif | else if | elsif age > 13: |
| else | else | else: |
| end | end block | end |
| choose | switch start | choose day: |
| when | switch case | when "mon": |
| otherwise | switch default | otherwise: |
| from | for loop start | from 1 to 5 in i: |
| to | for loop to | from 1 to 5 |
| in | for loop in | in i: / each x in list: |
| each | for-each loop | each x in list: |
| keep | while loop | keep i < 5: |
| try | try block | try: |
| catch | catch error | catch e: |
| finally | finally block | finally: |
| breck | break loop | breck |
| skip | continue loop | skip |
| continu | continue alias | continu |

## 8. FUNCTIONS - 3 keywords
| func | define function | func add: int (a: int): |
| give | return value | give a + b |
| swap | swap values | swap(a <> b) |
| <> | swap operator inside swap | swap(a <> b) |

## 9. IO - 2 keywords
| show | print output | show "hi" |
| input | take input | input("enter").int |

## 10. IMPORT - 2 keywords
| import | import module | import math |
| from | from import | from math import sqrt |

## 11. COMMENTS - 1 keyword
| # | comment | # this is comment |

TOTAL KEYWORDS: 74