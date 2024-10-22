window "My First Window"
windowsize "300,500"
label "Welcome to Fluxel!"
entry user_name
button "Say Hello" "get entry name user_name"
button "Say Hello" "message "Hello, " + name + "!""
button "Quit" "window.quit()"
show window