document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();
  
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const errorMessage = document.getElementById('error-message');
  
    if (username === "" || password === "") {
      errorMessage.textContent = "Veuillez remplir tous les champs.";
      errorMessage.style.display = "block";
    } else {
      errorMessage.style.display = "none";
  
      
      const formData = new FormData();
      formData.append('name', username);
      formData.append('password', password);
  
      
      fetch('/', {
        method: 'POST',
        body: formData
      })
      .then(response => response.text())
      .then(data => {
        if (data.includes('error')) {
          errorMessage.textContent = "Nom d’utilisateur ou mot de passe incorrect.";
          errorMessage.style.display = "block";
        } else {
          window.location.href = '/dashboard'; 
        }
      })
      .catch(error => {
        console.error('Error:', error);
        errorMessage.textContent = "Une erreur est survenue.";
        errorMessage.style.display = "block";
      });
    }
  });
  
  function togglePassword() {
    const passwordInput = document.getElementById('password');
    const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
    passwordInput.setAttribute('type', type);
  }
  