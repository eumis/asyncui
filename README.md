# AsyncUI

[![CI](https://github.com/eumis/asyncui/actions/workflows/ci.yml/badge.svg?branch=dev)](https://github.com/eumis/asyncui/actions/workflows/ci.yml)

Library for asynchronous GUI programming.
Runs async event loop in a separate thread.

## Installation

```
pip install asyncui
```

## Usage

For complete examples see [demo](demo) folder.

### wxpython

```python
import asyncio
import asyncui
import wx

app = wx.App()
frame = wx.Frame(None, title="Async wxPython")
frame.Show()

with asyncui.run_loop():
    app.MainLoop()
```

### Tkinter Example

```python
import asyncio
import asyncui
import tkinter as tk

root = tk.Tk()
root.title("Async Tkinter")

with asyncui.run_loop():
    root.mainloop()
```
