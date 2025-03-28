document.addEventListener("DOMContentLoaded", function() {
    loadUsers();

    document.getElementById("userForm").addEventListener("submit", function(event) {
        event.preventDefault();

        const name = document.getElementById("name").value;
        const role = document.getElementById("role").value;

        fetch("https://api-interface-web.onrender.com//add_user", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name: name, role: role })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadUsers();  // Recharger la liste des utilisateurs
            }
        });

        document.getElementById("name").value = "";
        document.getElementById("role").value = "";
    });
});

function loadUsers() {
    fetch("/users")
        .then(response => response.json())
        .then(users => {
            const userList = document.getElementById("userList");
            userList.innerHTML = "";
            users.forEach(user => {
                const li = document.createElement("li");
                li.textContent = `${user.name} - ${user.role}`;
                const deleteButton = document.createElement("button");
                deleteButton.textContent = "Supprimer";
                deleteButton.onclick = function() {
                    deleteUser(user.name);
                };

                li.appendChild(deleteButton)
                userList.appendChild(li);
            });
        });
}

function deleteUser(userName) {
    fetch(`/delete_user/${userName}`, {
        method: 'DELETE',
    })
    .then(response => response.json()) // Parse la réponse en JSON
    .then(data => {
        if (data.success) {
            alert('Utilisateur supprimé avec succès !');
            loadUsers();} // Recharger la page pour voir les changements
        else {
            alert("Erreur"); 
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
    });
}