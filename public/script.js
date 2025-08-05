document.addEventListener('DOMContentLoaded', () => {
  // --- HERO TYPING EFFECT (only on home page) ---
  const heroTitle = document.getElementById('hero-title');
  if (heroTitle) {
    const textToType = "Smart Data. Smarter World.";
    let i = 0;
    function typeWriter() {
      if (i < textToType.length) {
        heroTitle.innerHTML += textToType.charAt(i);
        i++;
        setTimeout(typeWriter, 80);
      }
    }
    typeWriter();
  }

  // --- MOBILE MENU ---
  const mobileMenuButton = document.getElementById('mobile-menu-button');
  const closeMenuButton = document.getElementById('close-menu-button');
  const mobileMenu = document.getElementById('mobile-menu');
  const mobileNavLinks = mobileMenu ? mobileMenu.querySelectorAll('.mobile-nav-link') : [];

  if (mobileMenuButton) {
    mobileMenuButton.addEventListener('click', () => {
      mobileMenu.classList.add('is-open');
      document.body.style.overflow = 'hidden';
    });
  }

  const closeMenu = () => {
    if (mobileMenu) {
        mobileMenu.classList.remove('is-open');
        document.body.style.overflow = '';
    }
  };

  if (closeMenuButton) closeMenuButton.addEventListener('click', closeMenu);
  if (mobileNavLinks) mobileNavLinks.forEach(link => link.addEventListener('click', closeMenu));

  // --- ACTIVE NAV LINK HIGHLIGHTING ---
  const desktopNavLinks = document.querySelectorAll('#desktop-nav .nav-link');
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';

  desktopNavLinks.forEach(link => {
    const linkPage = link.getAttribute('href');
    if (linkPage === currentPage) {
      link.classList.add('active');
    }
  });

  // --- FADE-IN ANIMATION ON SCROLL ---
  const fadeElements = document.querySelectorAll('.fade-in-section');
  const fadeObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  fadeElements.forEach(el => fadeObserver.observe(el));

  // --- AI PARTICLE NETWORK ANIMATION ---
  const canvas = document.getElementById('particle-canvas');
  if (canvas) {
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    let particlesArray;

    const mouse = {
      x: null,
      y: null,
      radius: (canvas.height / 110) * (canvas.width / 110)
    };

    window.addEventListener('mousemove', (event) => {
      mouse.x = event.x;
      mouse.y = event.y;
    });
    
    window.addEventListener('mouseout', () => {
        mouse.x = undefined;
        mouse.y = undefined;
    });

    class Particle {
      constructor(x, y, directionX, directionY, size, color) {
        this.x = x;
        this.y = y;
        this.directionX = directionX;
        this.directionY = directionY;
        this.size = size;
        this.color = color;
      }

      draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2, false);
        ctx.fillStyle = '#FFB347';
        ctx.fill();
      }

      update() {
        if (this.x > canvas.width || this.x < 0) this.directionX = -this.directionX;
        if (this.y > canvas.height || this.y < 0) this.directionY = -this.directionY;
        
        let dx = mouse.x - this.x;
        let dy = mouse.y - this.y;
        let distance = Math.sqrt(dx*dx + dy*dy);
        if (distance < mouse.radius + this.size){
            if(mouse.x < this.x && this.x < canvas.width - this.size * 10) this.x += 5;
            if(mouse.x > this.x && this.x > this.size * 10) this.x -= 5;
            if(mouse.y < this.y && this.y < canvas.height - this.size * 10) this.y += 5;
            if(mouse.y > this.y && this.y > this.size * 10) this.y -= 5;
        }

        this.x += this.directionX;
        this.y += this.directionY;
        this.draw();
      }
    }

    function init() {
      particlesArray = [];
      let numberOfParticles = (canvas.height * canvas.width) / 9000;
      for (let i = 0; i < numberOfParticles; i++) {
        let size = (Math.random() * 2) + 1;
        let x = (Math.random() * ((innerWidth - size * 2) - (size * 2)) + size * 2);
        let y = (Math.random() * ((innerHeight - size * 2) - (size * 2)) + size * 2);
        let directionX = (Math.random() * 0.4) - 0.2;
        let directionY = (Math.random() * 0.4) - 0.2;
        particlesArray.push(new Particle(x, y, directionX, directionY, size, '#FFB347'));
      }
    }

    function connect() {
      let opacityValue = 1;
      for (let a = 0; a < particlesArray.length; a++) {
        for (let b = a; b < particlesArray.length; b++) {
          let distance = ((particlesArray[a].x - particlesArray[b].x) * (particlesArray[a].x - particlesArray[b].x))
                       + ((particlesArray[a].y - particlesArray[b].y) * (particlesArray[a].y - particlesArray[b].y));
          if (distance < (canvas.width / 7) * (canvas.height / 7)) {
            opacityValue = 1 - (distance / 20000);
            ctx.strokeStyle = 'rgba(255, 179, 71,' + opacityValue + ')';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(particlesArray[a].x, particlesArray[a].y);
            ctx.lineTo(particlesArray[b].x, particlesArray[b].y);
            ctx.stroke();
          }
        }
      }
    }

    function animate() {
      requestAnimationFrame(animate);
      ctx.clearRect(0, 0, innerWidth, innerHeight);
      for (let i = 0; i < particlesArray.length; i++) {
        particlesArray[i].update();
      }
      connect();
    }
    
    window.addEventListener('resize', () => {
        canvas.width = innerWidth;
        canvas.height = innerHeight;
        mouse.radius = (canvas.height / 110) * (canvas.width / 110);
        init();
    });

    init();
    animate();
  }

  // --- APPLICATION MODAL (from services.html) ---
  const openModalBtn = document.getElementById('open-apply-modal-btn');
  const modal = document.getElementById('application-modal');
  const closeModalBtn = document.getElementById('close-modal-btn');
  const applicationForm = document.getElementById('application-form');
  
  if (openModalBtn && modal && closeModalBtn && applicationForm) {
    const fileUploadWrapper = document.getElementById('file-upload-wrapper');
    const fileInput = document.getElementById('resumeFile');
    const fileNameDisplay = document.getElementById('file-name-display');
    const removeFileBtn = document.getElementById('remove-file-btn');
    const submitBtn = document.getElementById('submit-application-btn');
    
    const openModal = () => {
      modal.classList.add('show');
      document.body.classList.add('modal-open');
    };

    const closeModal = () => {
      modal.classList.remove('show');
      document.body.classList.remove('modal-open');
    };

    openModalBtn.addEventListener('click', (e) => {
      e.preventDefault();
      openModal();
    });

    closeModalBtn.addEventListener('click', closeModal);

    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        closeModal();
      }
    });

    fileInput.addEventListener('change', () => {
      if (fileInput.files.length > 0) {
        fileNameDisplay.textContent = fileInput.files[0].name;
        fileUploadWrapper.classList.add('has-file');
      } else {
        fileNameDisplay.textContent = 'No file chosen';
        fileUploadWrapper.classList.remove('has-file');
      }
    });

    removeFileBtn.addEventListener('click', () => {
        fileInput.value = '';
        fileNameDisplay.textContent = 'No file chosen';
        fileUploadWrapper.classList.remove('has-file');
    });
    
    applicationForm.addEventListener('submit', (e) => {
      e.preventDefault();
      
      submitBtn.disabled = true;
      submitBtn.textContent = 'Submitting...';

      const formData = new FormData(applicationForm);
      
      // NOTE: This form's submission logic is now handled in services.html
      // This is just a placeholder for the visual feedback
      setTimeout(() => {
        alert('Thank you for your application! We will be in touch shortly.');
        
        applicationForm.reset();
        fileNameDisplay.textContent = 'No file chosen';
        fileUploadWrapper.classList.remove('has-file');
        closeModal();
        
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit Application';

      }, 1500);
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && modal.classList.contains('show')) {
        closeModal();
      }
    });
  }
});