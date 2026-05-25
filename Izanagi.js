function showpage(name){
    ['regi', 'logi', 'home', 'about', 'dashboard', 'userpage'].forEach(id =>{
        document.getElementById(id).style.display = "none";
    });
    document.getElementById(name).style.display = "block";
    window.location.hash = name;

    if (name === 'dashboard') loadDashboard();
    if (name === 'userpage') loadUserPage();
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
                document.getElementById('UserNickna').innerHTML = nick;
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
                document.getElementById('UserNickna').innerHTML = nick;
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

const fallbackStats = {
    totalUsers: 42,
    hardcore: 5,
    normal: 12,
    chill: 25,
    monthlyLabels: ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн'],
    monthlyValues: [3, 7, 5, 12, 8, 7]
};

let barChartInstance = null;
let pieChartInstance = null;

function loadDashboard() {
    renderDashboard(fallbackStats);

    const token = localStorage.getItem('token');
    const controller = new AbortController();

    setTimeout(() => controller.abort(), 3000);

    fetch('http://26.96.157.124:5000/dashboard', {
        headers: {'Authorization': 'Bearer' + token}
    })
    .then(res => {
        if (!res.ok) throw new Error('Сервер не отвечает, бро');
        return res.json();
    })
    .then(data => renderDashboard(data))
    .catch(() => {
        console.warn('Бэкенд временно недоступен, это зашлушка');
        renderDashboard(fallbackStats);
    })
}

function renderDashboard(data) {
    document.getElementById('statTotal').textContent = data.totalUsers;
    document.getElementById('statHard').textContent = data.hardcore;
    document.getElementById('statNorm').textContent = data.normal;
    document.getElementById('statChill').textContent = data.chill;

    if (barChartInstance) barChartInstance.destroy();
    if (pieChartInstance) pieChartInstance.destroy();

    barChartInstance = new Chart(document.getElementById('barChart'), {
        type: 'bar',
        data: {
            labels: data.monthlyLabels,
            datasets: [{
                label: 'Новые чуваки/чувихи',
                data: data.monthlyValues,
                backgroundColor: 'rgb(133, 114, 255)',
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false }},
            scales: {
                y: { ticks: {color: '#fff'}, grid: {color :'rgba(255, 255, 255, 0.73)'}},
                x: { ticks: { color: '#fff' }, grid: { color: 'rgba(255, 255, 255, 0.73)' } }
            }
        }
    });
    pieChartInstance = new Chart(document.getElementById('pieChart'), {
        type: 'doughnut',
        data: {
            labels: ['Шиз', 'Нормис', 'Чилл'],
            datasets: [{
                data: [data.hardcore, data.normal, data.chill],
                backgroundColor: ['#ff4d4d', '#f7a94f', '#4fcf70'],
                borderWidth: 0
            }]
        },
        options: {
            plugins: {
                legend: {labels: {color: '#fff', font: {size: 14}}}
            }
        }
    })
}

function loadUserPage() {
    const token = localStorage.getItem('token');

    if (!token) {
        showpage('logi');
        return;
    }
    fetch('http://26.96.157.124:5000/user', {
        headers: { 'Authorization': 'Bearer ' + token }
    })
    .then(res => {
        if (res.status === 401) {
            showpage('logi');
            throw new Error('Сорри, токен недействителен');
        }
        return res.json();
    })
    .then(data => {
        document.getElementById('UserNickna').innerHTML = data.username;
        document.getElementById('UserRegDate').innerHTML = data.data.created_at;
        document.getElementById('UserCourse').innerHTML = data.course ?? 'увы не выбран';
    })
    .catch(err => console.error(err));
}

function refreshToken() {
    const token = localStorage.getItem('token');

    fetch('http://26.96.157.124:5000/refresh-token', {
        method: 'POST',
        headers: {'Authorization': 'Bearer' + token}
    })
    .then(res => res.json())
    .then(data => {
        if (data.token) {
            localStorage.setItem('token', data.tolen);
            alert('Поздравляю, ты обновил токен');
        }
    })
    .catch(() => alert('Сорри, не получилось обновить токен'))
}