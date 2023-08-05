Command line tool for http://lmgtfy.com/
===
[![Pypi Version](https://pypip.in/v/lmgtfy/badge.png)](https://crate.io/package/lmgtfy)  
[![Downloads](https://pypip.in/d/lmgtfy/badge.png)](https://crate.io/package/lmgtfy)  
[![Build Status](https://travis-ci.org/decached/lmgtfy.png?branch=master)](https://travis-ci.org/decached/lmgtfy)

Features
---
Get original as well as shortened lmgtfy url for your query from command line

Dependencies
---

- Requests `$ pip install requests`
- Xclip `$ apt-get install xclip`

Installation
---
`$ pip install lmgtfy`

Pass a query string to lmgtfy from command line as follows

```
$ lmgtfy hello world 
Lmgtfy url: http://lmgtfy.com/?q=hello+world
Short url : http://is.gd/Hf48UY
```

by [@decached](http://github.com/decached) based on [lmgtfy-gem](https://github.com/prathamesh-sonpatki/lmgtfy-gem)
