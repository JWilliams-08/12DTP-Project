/* This script gets the players for a selected team when the user selects a team from the dropdown. */
async function loadPlayers() {
    const team = document.getElementById('team').value;
    const playerSelect = document.getElementById('player');

    if (!team) {
        playerSelect.innerHTML = '';
        return;
    }

playerSelect.innerHTML = '<option>Loading...</option>'; // <-- this is probably line 12
    playerSelect.innerHTML = '<option>Loading...</option>';

    const response = await fetch(`/get_players/${team}`);
    const data = await response.json();

    playerSelect.innerHTML = '';
    data.players.forEach(player => {
        const option = document.createElement('option');
        option.value = player;
        option.textContent = player;
        playerSelect.appendChild(option);
    });
}