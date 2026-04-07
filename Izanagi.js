function seterror(id, error){
    element = document.getElementById(id);
    element.getElementsByClassName('formerror')[0].innerHTML = error;
}

function validateForm(){
    var returnval=true;
    var nick = document.forms["reg"]["username"].value;
    if(nick.length < 4){
        seterror("nick", "Мало буковок чувак, 4 или больше надо");
        returnval = false;

    var pass = document.forms["reg"]["psw"].value;
    if (pass.length < 4){
        seterror("pass", "Короткий пароль, аккаунт спиздят быстро");
        returnval = false;
    }

    var pass2 = document.forms["reg"]["psw2"].value;
    if (pass2.length < 4){
        seterror("pass2", "Короткий пароль, аккаунт спиздят быстро");
        returnval = false;
    }

    var pass2 = document.forms["reg"]["psw2"].value;
    if (pass2 != pass){
        seterror("pass2", "Пароли не совпадают, нельзя так чувак");
        returnval = false;
    }
    
    }
    return returnval;
}