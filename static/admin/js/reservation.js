document.addEventListener("DOMContentLoaded", function () {
    const employee = document.getElementById("id_employee");
    const menu = document.getElementById("id_menu");
    if (!employee || !menu) return;employee.addEventListener("change", function () {menu.innerHTML = ""; 
        if (!employee.value) return;
        fetch("/admin/accounts/reservation/get-menu/?employee=" + employee.value).then(response => 
            response.json()).then(data => {console.log(data);menu.innerHTML = "";data.forEach(item =>
                 {const option = document.createElement("option"); option.value = item.id;
                    option.text = item.text; menu.appendChild(option);});});});});