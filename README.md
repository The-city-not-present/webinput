# webinput
The conceptual API is something like:

```
answer = webinput.ask(...)
```

and internally:

```
application
    │
    │ ask(...)
    ▼
┌───────────────┐
│ webinput      │
│               │
│ start server  │
│ generate HTML │
│ open browser  │
│ wait          │
│ receive POST  │
│ validate      │
│ stop server   │
└───────┬───────┘
        │
        ▼
     answer
````

That's a much more specific and interesting thing to name.

Names I'd consider
webinput — my favorite
