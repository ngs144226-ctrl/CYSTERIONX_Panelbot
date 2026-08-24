const tg = window.Telegram.WebApp;

tg.ready();

let user = tg.initDataUnsafe.user;

if(user){
    document.getElementById("user").innerHTML =
    "Welcome " + user.first_name;
}
else{
    document.getElementById("user").innerHTML =
    "Open from Telegram";
}

function openServices(){
    alert("Services Section");
}
