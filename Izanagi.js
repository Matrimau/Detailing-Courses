function showpage(name){
    document.getElementById('regi').style.display = 'none';
    document.getElementById('logi').style.display = 'none';
    document.getElementById('home').style.display = 'none';
    document.getElementById('about').style.display = 'none';
    document.getElementById(name).style.display = 'block';

    window.location.hash = name;
}

function seterror(id, error){
    let element = document.getElementById(id);
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
        seterror("pass", "Короткий пароль, нужно от 4 символов");
        returnval = false;
    }

    var pass2 = document.forms["reg"]["psw2"].value;
    if (pass2.length < 4){
        seterror("pass2", "Короткий пароль, нужно от 4 символов");
        returnval = false;
    }
    if (pass2 != pass){
        seterror("pass2", "Пароли не совпадают, так нельзя чувак");
        returnval = false;
    }

    /*if(returnval){
        document.getElementById('Nickna').innerHTML = nick;
        showpage('home')
    }*/

    if(returnval){
        fetch('http://26.96.157.124:5000/registration', {
            method: 'POST',
            headers: {'Content-type': 'application/json'},
            body: JSON.stringify({
                username: nick,
                password: pass
            })
        })
        .then(res => res.json())
        .then(data => {
            if(data.status === "ok"){
                document.getElementById('Nickna').innerHTML = nick;
                localStorage.setItem('token', data.token)
                showpage('home')
            } else {
                seterror("nick", data.error)
            }
        })
        .catch(error => {
            alert('Сервер временно недоступен, сорри бро');
            console.error(error)
        })
    }

    return false;
}

function validateLogin(){
    var returnval = true;
    var nick = document.forms["log"]["username"].value;
    if(nick.length < 4){
        seterror("log-nick", "Никнейм должен состоять из 4 или более символов");
        returnval = false;
    }
    var pass = document.forms["log"]["psw"].value;
    if(pass.length < 4){
        seterror("log-pass", "У тебя пароль короткий, от 4 символов");
        returnval = false;
    }

    /*if(returnval){
        document.getElementById('Nickna').innerHTML = nick;
        showpage('home')
    }*/
    
    if(returnval){
        fetch('http://26.96.157.124:5000/login', {
            method: 'POST',
            headers: {'Content-type': 'application/json'},
            body: JSON.stringify({
                username: nick,
                password: pass
            })
        })
        .then(res => res.json())
        .then(data => {
            if(data.status === 'ok'){
                document.getElementById('Nickna').innerHTML = nick;
                localStorage.setItem('token', data.token)
                showpage('home')
            }
            else {
                seterror(data.id, data.error)
            }
        })
        .catch(error => {
            alert('Сервер временно недоступен, сорри бро');
            console.error(error)
        })
    }

return false;
}