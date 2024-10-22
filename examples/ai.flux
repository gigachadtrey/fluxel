window "Chat with Gemini"
windowsize "400,500"

var API_KEY = "AIzaSyBtaKEQYOgKNLHoKbnh_TUTA6oyQSJvlpg"
configure_gemini API_KEY

label "Chat History:"
var chat_history = text

label "Your message:"
var user_input = entry

button "Send" "send_message" objectLocation = 150, 450

var send_message = "
get entry message user_input
generate_content message
append_text chat_history 'You: ' + message
append_text chat_history 'Gemini: ' + gemini_response
"

show window
