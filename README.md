# webinput

## What it is and what its role is

Basic pattern.

Imagine .bat or .sh script. Some commands ran. Then, the script implies some input from the user. It can call

```
value = input('Hey how\'s it going buddy')
```

This uses cli interface to request responses.

The webinput implements the same model, but the response is delivered through html form in browser, served from localhost. When response is submitted, webserver is being shut down, the webinput returns the response, and caller script continues.

So, it's a replacement for command-line `input()` function implemented in web form form served from localhost.

It means this module does not make sense as continuously running. It has start, and needs some definitions for it to start - structure of html form, or, in other words, some definitions of what is asked. Then it shows the form. And quits, with returned result. Clear start - show time - finish. No continuous run.

The runtime itself is quite simple. It's just a web form shown. So, there isn't much complexity in ui by default. However, more complicated widget types can add complexity without any limits.

## The concept

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
```

That's a much more specific and interesting thing to name.

Names I'd consider
webinput — my favorite

## Design principles

Independent self-contained module, reusable.

Clear definitions for input formats and output.

Uniform use pattern.

Should be possible to make distributable bundle with only python, without node installed.

However, node can be available as an alternative environment for development, if web form is implemented with frontend stack or more complicated js.

### Modular/layered system

We should prefer clear layered architecture with clear role of every layer.

The definitions for the form - what is asked - are done through `src/lib/qre` abstraction later. Currently, the user should import definitions for "question types" and build the structure of "html form" with it, and provide as input to webinput. Benefits - uniform absrtaction, expandable, with uniform way to specify preferred widgets, or adjustments to widgets, or other properties that control behavior. Also, supports nested structures with any depth of hierarchy. Downsides - the user must learn the contract. Possible alternative: let user provide specifications as json schema, and make it possible that internal structure is loaded from json schema. Advantages: the user does not have to learn internal qre contract. Downsides - json schema is still not very standardized thing, still no uniform way to provide all what is needed, no standard way to specify all possible question types, including hierarchical structures, no standard way to specify preferred widgets... It means, it still means user has to learn some contract -> not many benefits.

The rendering layer - should ideally be implemented in "skins" or "templater" implementations, so that the user can choose one of possible implementations - maybe something very basic in raw html, or something made with frontend, or alternative implementation...

 ## Key concerns/gotchas

### Duplicates of included submodules repeating same things already shipped with calling it app

As this is a self-contained module, it also includes webserve, and maybe py_js_bundler, and maybe vite and fonts, and other things already available in app that uses webserve - causing duplicates within same outer bigger repo.

### No way to provide "skin"

As this is an independent self-contained module, there isn't currently a way to specify consistent ui with outer project, same fonts, same indents, buttons, coloring scheme, etc...

### pywebview vs browser

Using browser or pywebview or any alternatives - all have downsides.

Browser: if it does not open - the app is simply not serving its function. It feels like it's not working - it's not doing anything, no window opens. If browser window does open - it's an awful side effect. Also, there is no clear way to close browser window when we no longer need it.

Pywebview: very unpleasant requirements to have its gui loop started from main thread, that is blocking. No clear timing, what should terminate first - the webserver or the ui window. Ideally, I'd make backend logic to rule the game, and terminate and return response when response is received. And ui window should follow same life span. However, pywebview is designed that the main gui window is closed first. Also, there is an implementation weirdness that pywebview is not being shut down when window is closed, and remains "hanging" on screen. I haven't found a solution yet. It only shuts down when all my script finishes. However, if I have it live only during some step when a response from user is needed - it means the window stays hanging for the remaining life of the caller script. Also, pywebview adds more dependencies... So, there are a lot of downsides. Not critical, but needs to be reviewed if it worth it.

I might consider other options and keep exploring. Maybe, Tauri... Not familiar with it and have not tried. Or, popular suggestion is electron, but I think bundling node with the app is overkill - too heavy dependency.
