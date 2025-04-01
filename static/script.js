document.addEventListener("DOMContentLoaded", function() {
    loadUsers();

    document.getElementById("userForm").addEventListener("submit", function(event) {
        event.preventDefault();

        const name = document.getElementById("name").value;
        const role = document.getElementById("role").value;

        fetch("/add_user", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name: name, role: role })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadUsers();  // Recharger la liste des utilisateurs pour l'afficher
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

// Ajouter une salle & horaires
document.getElementById('addRoomForm').addEventListener('submit', function(event) {
    event.preventDefault();

    var roomName = document.getElementById('roomName').value;
    var startTime = document.getElementById('startTime').value;
    var endTime = document.getElementById('endTime').value;

    var data = {
        "room_name": roomName,
        "start_time": startTime,
        "end_time": endTime
    };

    fetch('/add_room', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            alert('Salle et horaires ajoutés avec succès!');
            location.reload();
        } else {
            alert('Erreur lors de l\'ajout.');
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        alert('Une erreur est survenue.');
    });
});

// Modifier les horaires d'accès d'une salle
document.getElementById('setHoraireForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Empêche l'envoi du formulaire

    var roomId = document.getElementById('roomSelect').value;
    var startTime = document.getElementById('startTime').value;
    var endTime = document.getElementById('endTime').value;

    var data = {
      "room_id": roomId,
      "start_time": startTime,
      "end_time": endTime
    };

    // Fetch de l'endpoint de l'API pour mettre à jour les horaires
    fetch('/set_horaire', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
      if (result.success) {
        alert('Horaire modifié avec succès !');
      } else {
        alert('Erreur lors de la modification des horaires');
      }
    })
    .catch(error => {
      console.error('Erreur:', error);
      alert('Une erreur est survenue.');
    });
});

// Récupérer et afficher les salles dans modification d'horaire
function loadRooms() {
    fetch('/rooms', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        const roomSelect = document.getElementById('roomSelect');
        
        roomSelect.innerHTML = "";

        data.forEach(room => {
            const option = document.createElement("option");
            option.value = room.id;  // On met l'ID comme valeur
            option.textContent = room.room_name;  // Le nom de la salle comme texte
            roomSelect.appendChild(option);
        });
    })
    .catch(error => {
        console.error('Erreur de chargement des salles:', error);
    });
}

window.onload = function() {
    loadRooms();
};
