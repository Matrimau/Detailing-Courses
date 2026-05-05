function showpage(name){
    document.getElementById('regi').style.display = 'none';
    document.getElementById('logi').style.display = 'none';
    document.getElementById(name).style.display = 'block';
}

function seterror(id, error){
    element = document.getElementById(id);
    element.getElementsByClassName('formerror')[0].innerHTML = error;
}

function validateForm(){
    var returnval=true;
    var nick = document.forms["reg"]["username"].value;
    if (nick.length < 4){
        seterror("nick", "Мало буковок чувак, 4 или больше надо");
        returnval = false;
    }
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

    if(returnval){
        fetch('http/localhost:5000/registration', {
            method: 'POST',
            headers: {'Content-type': 'application/json'},
            body: JSON.stringify({
                username: nick,
                password: pass
            })
        })
        .then(res => res.json())
        .then(data => console.log(data))
    }

    return returnval;
}

function validateLogin(){
    var returnval = true;
    var nick = document.forms["log"]["username"].value;
    if(nick.length < 4){
        seterror("log-nick", "Ты же блять делал аккаунт, 4 или больше буковок надо");
        returnval = false;
    }
    var pass = document.forms["log"]["psw"].value;
    if(pass.length < 4){
        seterror("log-pass", "Имбецил, пароль короткий у тебя, 4 или больше символов надо");
        returnval = false;
    }

    if(returnval){
        fetch('http/localhost:5000/login', {
            method: 'POST',
            headers: {'Content-type': 'application/json'},
            body: JSON.stringify({
                username: nick,
                password: pass
            })
        })
        .then(res => res.json())
        .then(data => console.log(data))
    }

return returnval;
}