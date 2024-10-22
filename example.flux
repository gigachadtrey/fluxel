var name = "Trey"
var favColor = "green"

typewriter "Hello!" 2
silentWait 2
typewriteask "How is your day?"
remember day
typewriter "You're having a " + day + " day? OK." 3
typewriteask "Whats your favorite color?" 3
remember userColor
typewriter "My favorite color is " + favColor + " and your favorite color is " + userColor + "!" 3
typewriteask "My name is, " + name + ". Whats you're name?" 4
remember userName
typewriter " " + userName + "? Thats a nice name." 2
typewriter "See you later!" 3
