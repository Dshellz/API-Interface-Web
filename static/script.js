document.addEventListener("DOMContentLoaded", function() {
    loadUsers();

    document.getElementById("userForm").addEventListener("submit", function(event) {
        event.preventDefault();

        const name = document.getElementById("name").value;
        const role = document.getElementById("role").value;

        fetch("http://127.0.0.1:5000/add_user", {
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
                userList.appendChild(li);
            });
        });
}
document.getElementById('deleteUserForm').addEventListener('submit', function (event) {
    event.preventDefault(); // Empêche le rechargement de la page

    
    const userName = document.getElementById('userName').value; // Récup le nom de l'utilisateur

    // Envoi de la requête DELETE
    fetch(`/delete_user/${userName}`, {
        method: 'DELETE',
    })
    .then(response => response.json()) // Parse la réponse en JSON
    .then(data => {
        // Afficher un message de succès ou d'erreur
        alert('Utilisateur supprimé avec succès!');
        location.reload(); // Recharger la page pour voir les changements
    })
    .catch(error => {
        console.error('Erreur:', error);
    });
});