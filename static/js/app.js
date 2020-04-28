console.log(' app.js here ');

const deleteBtn = document.querySelectorAll('.delete-btn');
deleteBtn.forEach((btn) =>
  btn.addEventListener('click', (e) => {
    let venueID = e.target.dataset['id'];
    fetch(`/venues/${venueID}`, {
      method: 'DELETE',
    })
      .then((res) => {
        if (res.status === 200) {
          location.reload();
        }
      })
      .catch((err) => console.log(err));
  })
);
