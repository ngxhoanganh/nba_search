//links
//http://eloquentjavascript.net/09_regexp.html
//https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Regular_Expressions


var messages = [], //array that hold the record of each string in chat
lastUserMessage = "", //keeps track of the most recent input string from the user
botMessage = "", //var keeps track of what the chatbot is going to say
botName = 'Chatbot', //name of the chatbot
talking = true; //when false the speach function doesn't work

window.alert = function(){};
        var defaultCSS = document.getElementById('bootstrap-css');
        function changeCSS(css){
            if(css) $('head > link').filter(':first').replaceWith('<link rel="stylesheet" href="'+ css +'" type="text/css" />'); 
            else $('head > link').filter(':first').replaceWith(defaultCSS); 
        }

// Function to handle bot response 
async function chatbotResponse() {
  talking = true;
  botMessage = "I'm confused"; // Default message

  const payload = new FormData();
  payload.append('msg', lastUserMessage);

  try {
    const res = await fetch('/bot-msg', {
      method: 'POST',
      body: payload
    });

    const data = await res.json(); // Parse JSON response
    botMessage = data || "I'm confused"; // Use the response directly
  } catch (error) {
    console.error('Error fetching bot response:', error);
    botMessage = "Sorry, something went wrong.";
  }
}

// Auto-scroll and update based on https://stackoverflow.com/a/39729993

async function newmsg() {
  const data = $("#btn-input").val();

  // Append user message
  $(".msg_container_base").append(`
    <div class="row msg_container base_sent">
      <div class="messages msg_sent">
        <p>${data}</p>
      </div>
    </div>
  `);

  clearInput();
  lastUserMessage = String(data);

  // Fetch bot response
  await chatbotResponse();

  // Append bot message
  $(".msg_container_base").append(`
    <div class="row msg_container base_receive">
      <div class="messages msg_receive">
        <p>${botMessage}</p>
        <time>${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</time>
      </div>
    </div>
  `);

  // Scroll to the bottom
  $(".msg_container_base").stop().animate({ scrollTop: $(".msg_container_base")[0].scrollHeight }, 1000);
}

$("#submit").click(async function() {
    newmsg();
});

function clearInput() {
    $("#myForm :input").each(function() {
        $(this).val(''); // Clears form
    });
}

$("#myForm").submit(function() {
    return false; // Prevents redirection
});

// Function to convert text to speech
//https://developers.google.com/web/updates/2014/01/Web-apps-that-talk-Introduction-to-the-Speech-Synthesis-API
function Speech(say) {
  if ('speechSynthesis' in window && talking) {
    var utterance = new SpeechSynthesisUtterance(say);
    speechSynthesis.speak(utterance);
  }
}

//runs the keypress() function when a key is pressed
document.onkeypress = keyPress;
//if the key pressed is 'enter' runs the function newEntry()
function keyPress(e) {
  var x = e || window.event;
  var key = (x.keyCode || x.which);
  if (key == 13 || key == 3) {
    e.preventDefault(); // ⬅️ chặn submit mặc định
    newmsg();
  }
}
// Xử lý nút quick reply
$(document).on("click", ".quick-reply-btn", function() {
  console.log("Nút quick reply được nhấn:", $(this).data("message"));
  let message = $(this).data("message");
  if (message) {
    $("#btn-input").val(message);
    newmsg(); // Gọi trực tiếp newmsg thay vì submit form
  } else {
    console.error("Không tìm thấy data-message trên nút quick reply");
  }
});