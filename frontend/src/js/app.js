// ===================================================
// CONFIGURAÇÃO DA API
// Detecta automaticamente se estamos rodando local (localhost) ou na internet
// ===================================================
const API_BASE_URL = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1" 
    ? "http://localhost:8000" 
    : window.location.origin;

// ===================================================
// Armazena as figurinhas e a coleção do usuário para acesso global na lógica de clique
let todasFigurinhas = new Map();
let figurinhasColadas = [];
let figurinhasReveladas = new Set(JSON.parse(sessionStorage.getItem("figurinhas_reveladas") || "[]"));

// FUNÇÃO: Preenche os slots do álbum com imagens da API
// Esta função é chamada após o álbum ser inicializado.
// ===================================================
async function preencherFigurinhas(pageFlip = null) {
    try {
        const token = sessionStorage.getItem("access_token");
        
        // 1. Busca todas as figurinhas disponíveis
        const responseAll = await fetch(`${API_BASE_URL}/figurinhas`);
        if (!responseAll.ok) {
            throw new Error(`Erro na API: ${responseAll.status}`);
        }
        const figurinhas = await responseAll.json();
        todasFigurinhas = new Map(figurinhas.map(f => [f.id, f]));

        // 2. Se logado, busca a lista de IDs coladas
        figurinhasColadas = [];
        if (token) {
            try {
                const responseMe = await fetch(`${API_BASE_URL}/figurinhas/user/me`, {
                    headers: { "Authorization": `Bearer ${token}` }
                });
                if (responseMe.ok) {
                    figurinhasColadas = await responseMe.json();
                }
            } catch (err) {
                console.warn("⚠️ Não foi possível carregar a coleção do usuário:", err.message);
            }
        }

        // 3. Limpa e atualiza cada slot
        const slots = document.querySelectorAll(".sticker-slot");
        for (const slot of slots) {
            const slotNumeroEl = slot.querySelector(".slot-number");
            if (!slotNumeroEl) continue;

            const id = parseInt(slotNumeroEl.textContent.replace("#", ""), 10);
            
            // Remove qualquer imagem ou overlay de revelação adicionados anteriormente
            const imgExistente = slot.querySelector(".sticker-img");
            if (imgExistente) {
                imgExistente.remove();
            }
            const overlayExistente = slot.querySelector(".sticker-reveal-overlay");
            if (overlayExistente) {
                overlayExistente.remove();
            }
            slot.classList.remove("slot-preenchido");
            slot.classList.remove("slot-revelavel");

            if (!todasFigurinhas.has(id)) continue;
            const figurinha = todasFigurinhas.get(id);

            // Só exibe a imagem se estiver logado AND a figurinha estiver na lista de coladas
            if (token && figurinhasColadas.includes(id)) {
                if (figurinhasReveladas.has(id)) {
                    // Já revelada: exibe a imagem
                    const img = document.createElement("img");
                    img.src = `${API_BASE_URL}${figurinha.imagem_url}`;
                    img.alt = figurinha.nome;
                    img.className = "sticker-img";

                    img.onload = () => {
                        slot.classList.add("slot-preenchido");
                        if (pageFlip) {
                            pageFlip.update();
                        }
                    };
                    img.onerror = () => console.warn(`Imagem não encontrada: ${figurinha.nome}`);

                    slot.insertBefore(img, slot.firstChild);
                } else {
                    // Coletada mas não revelada: exibe overlay "revelável"
                    slot.classList.add("slot-revelavel");

                    const overlay = document.createElement("div");
                    overlay.className = "sticker-reveal-overlay";
                    overlay.innerHTML = `
                        <div class="reveal-glow"></div>
                        <span class="reveal-text">Revelar!</span>
                    `;
                    slot.insertBefore(overlay, slot.firstChild);
                }
            }
        }

        console.log(`✅ Figurinhas atualizadas! Coladas: [${figurinhasColadas.join(", ")}]`);

        // Notifica o PageFlip após a inserção síncrona
        if (pageFlip) {
            pageFlip.update();
        }

    } catch (erro) {
        console.warn("⚠️  Erro ao carregar figurinhas:", erro.message);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const bookElement = document.getElementById("book");
    const btnPrev = document.getElementById("btn-prev");
    const btnNext = document.getElementById("btn-next");
    const soundToggle = document.getElementById("sound-toggle");
    const iconOn = soundToggle.querySelector(".sound-icon-on");
    const iconOff = soundToggle.querySelector(".sound-icon-off");
    const themeToggle = document.getElementById("theme-toggle");

    let isMuted = false;
    let pageFlip = null;

    // 1. Inicializa o St.PageFlip
    try {
        pageFlip = new St.PageFlip(bookElement, {
            width: 550, // Largura base da página
            height: 800, // Altura base da página
            size: "stretch",
            minWidth: 315,
            maxWidth: 1000,
            minHeight: 420,
            maxHeight: 1350,
            drawShadow: true,
            maxShadowOpacity: 0.4, // Aumenta levemente o contraste da sombra
            showCover: true,
            mobileScrollSupport: true,
            useMouseEvents: false, // Desativa gestos padrão do StPageFlip para evitar cliques indesejados nas bordas/páginas
            showPageCorners: false, // Remove dobras dos cantos no hover
            disableFlipByClick: true, // Garante que a virada por cliques simples esteja desativada
            flippingTime: 800 // Transição mais ágil (800ms em vez de 1000ms)
        });

        // Carrega as páginas a partir do HTML
        pageFlip.loadFromHTML(document.querySelectorAll(".page"));

        // Estado de arraste personalizado
        let activeDragPage = null;
        let isClicking = false;
        let startX = 0;
        let startY = 0;
        let dragStarted = false;

        // Monitora o mousedown/touchstart em cada página para iniciar a intenção de arraste
        document.querySelectorAll(".page").forEach((page, index) => {
            page.addEventListener("mousedown", (e) => {
                if (e.target.closest("button") || e.target.closest("a")) return;
                e.preventDefault(); // Evita seleção de texto e comportamento de arraste nativo do navegador
                isClicking = true;
                startX = e.clientX;
                startY = e.clientY;
                dragStarted = false;
                activeDragPage = { page, index };
            });

            page.addEventListener("touchstart", (e) => {
                if (e.target.closest("button") || e.target.closest("a")) return;
                // Não cancelamos o touchstart padrão aqui para permitir cliques normais
                const touch = e.touches[0];
                isClicking = true;
                startX = touch.clientX;
                startY = touch.clientY;
                dragStarted = false;
                activeDragPage = { page, index };
            });
        });

        // Executa o movimento de dobra apenas se o mouse/dedo se mover além de um limiar (threshold)
        const handleMove = (clientX, clientY, isTouch = false) => {
            if (!isClicking || !activeDragPage) return;
            
            const deltaX = clientX - startX;
            const deltaY = clientY - startY;
            const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
            
            const bookRect = bookElement.getBoundingClientRect();

            // Só ativa o flip se mover mais de 10px (evita disparar ao clicar e soltar estático)
            if (distance > 10 && !dragStarted) {
                dragStarted = true;
                let cornerX, cornerY;
                
                // Determina canto vertical (topo vs base) em coordenadas relativas ao livro
                const centerY = bookRect.top + bookRect.height / 2;
                if (startY < centerY) {
                    cornerY = 0; // Canto superior
                } else {
                    cornerY = bookRect.height; // Canto inferior
                }

                // Determina canto horizontal (direita vs esquerda) em coordenadas relativas ao livro
                const isPortrait = pageFlip.getOrientation() === "portrait" || window.innerWidth <= 768;
                if (isPortrait) {
                    // No modo retrato (uma página por vez), o canto depende da direção do arraste (deltaX)
                    if (deltaX < 0) {
                        cornerX = bookRect.width; // Arrasta da direita para a esquerda (avançar)
                    } else {
                        cornerX = 0; // Arrasta da esquerda para a direita (voltar)
                    }
                } else {
                    // No modo paisagem (duas páginas), depende do índice da página ativa
                    if (activeDragPage.index % 2 === 0) {
                        cornerX = bookRect.width; // Canto direito
                    } else {
                        cornerX = 0; // Canto esquerdo
                    }
                }
                
                document.body.classList.add("dragging");
                pageFlip.startUserTouch({ x: cornerX, y: cornerY });
            }
            
            if (dragStarted) {
                const relX = clientX - bookRect.left;
                const relY = clientY - bookRect.top;
                pageFlip.userMove({ x: relX, y: relY }, isTouch);
            }
        };
 
        const handleRelease = (clientX, clientY, isTouch = false) => {
            if (dragStarted) {
                const bookRect = bookElement.getBoundingClientRect();
                const relX = clientX - bookRect.left;
                const relY = clientY - bookRect.top;
                pageFlip.userStop({ x: relX, y: relY }, isTouch);
            }
            isClicking = false;
            dragStarted = false;
            activeDragPage = null;
            document.body.classList.remove("dragging");
        };

        window.addEventListener("mousemove", (e) => {
            handleMove(e.clientX, e.clientY, false);
        });

        window.addEventListener("touchmove", (e) => {
            if (dragStarted && e.cancelable) {
                e.preventDefault(); // Evita rolar a página verticalmente durante o swipe do álbum
            }
            if (e.touches.length > 0) {
                const touch = e.touches[0];
                handleMove(touch.clientX, touch.clientY, true);
            }
        }, { passive: false });

        window.addEventListener("mouseup", (e) => {
            handleRelease(e.clientX, e.clientY, false);
        });

        window.addEventListener("touchend", (e) => {
            const touch = e.changedTouches[0] || e.touches[0];
            if (touch) {
                handleRelease(touch.clientX, touch.clientY, true);
            } else {
                handleRelease(startX, startY, true);
            }
        });

        window.addEventListener("touchcancel", () => {
            isClicking = false;
            dragStarted = false;
            activeDragPage = null;
            document.body.classList.remove("dragging");
        });

        // Mostra o livro após a inicialização bem-sucedida
        bookElement.style.display = "block";

        // Dia 3: Busca as figurinhas da API e preenche o álbum
        // A função é async, chamamos sem await para não bloquear a inicialização do álbum
        preencherFigurinhas(pageFlip);

        // Garante que o PageFlip recalcule o tamanho e renderize as páginas corretamente ao redimensionar a janela
        window.addEventListener("resize", () => {
            if (pageFlip) {
                pageFlip.update();
            }
        });

    } catch (error) {
        console.error("Erro ao inicializar a biblioteca PageFlip:", error);
    }

    // 2. Gerador de Efeitos Sonoros (Web Audio API)
    function playPaperTurnSound() {
        if (isMuted) return;

        try {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (!AudioContext) return;

            const audioCtx = new AudioContext();
            const duration = 0.45; // segundos
            const sampleRate = audioCtx.sampleRate;
            const bufferSize = sampleRate * duration;
            const buffer = audioCtx.createBuffer(1, bufferSize, sampleRate);
            const data = buffer.getChannelData(0);

            // Sintetiza ruído branco com um envelope de volume personalizado para virada de página
            for (let i = 0; i < bufferSize; i++) {
                const progress = i / bufferSize;
                // Valor do ruído entre -1 e 1
                const noise = Math.random() * 2 - 1;

                // Envelope de volume: curva suave com pico em cerca de 30% da duração
                let envelope = 0;
                if (progress < 0.3) {
                    envelope = progress / 0.3; // Subida rápida
                } else {
                    envelope = (1 - progress) / 0.7; // Decaimento suave
                }

                // Adiciona pequenos picos irregulares para simular a fricção/estalo do papel
                const paperCrackle = Math.random() > 0.985 ? (Math.random() * 2 - 1) * 0.35 : 0;

                data[i] = (noise * 0.65 + paperCrackle) * envelope * 0.12;
            }

            // Cria os nós de áudio
            const noiseNode = audioCtx.createBufferSource();
            noiseNode.buffer = buffer;

            // Filtro passa-faixa para extrair o som de "sopro" do embaralhar de papéis
            const bandpassFilter = audioCtx.createBiquadFilter();
            bandpassFilter.type = "bandpass";
            bandpassFilter.Q.value = 2.0;

            // Varredura dinâmica de frequência: começa em 1500Hz e desce para 350Hz (som da página se afastando)
            bandpassFilter.frequency.setValueAtTime(1500, audioCtx.currentTime);
            bandpassFilter.frequency.exponentialRampToValueAtTime(350, audioCtx.currentTime + duration);

            // Filtro passa-baixa para remover artefatos digitais ásperos de alta frequência
            const lowpassFilter = audioCtx.createBiquadFilter();
            lowpassFilter.type = "lowpass";
            lowpassFilter.frequency.setValueAtTime(3800, audioCtx.currentTime);

            // Conecta o grafo de áudio: Fonte -> Passa-faixa -> Passa-baixa -> Destino
            noiseNode.connect(bandpassFilter);
            bandpassFilter.connect(lowpassFilter);
            lowpassFilter.connect(audioCtx.destination);

            noiseNode.start();
        } catch (e) {
            console.warn("Falha ao tocar som de virada de página:", e);
        }
    }

    // 3. Controles do Estado do Áudio
    soundToggle.addEventListener("click", () => {
        isMuted = !isMuted;
        if (isMuted) {
            iconOn.classList.add("hidden");
            iconOff.classList.remove("hidden");
        } else {
            iconOn.classList.remove("hidden");
            iconOff.classList.add("hidden");
        }
    });

    // 3.1. Theme Toggle Controls (Claro / Escuro)
    if (themeToggle) {
        const sunIcon = themeToggle.querySelector(".theme-icon-sun");
        const moonIcon = themeToggle.querySelector(".theme-icon-moon");

        themeToggle.addEventListener("click", () => {
            document.body.classList.toggle("light-mode");
            const isLightMode = document.body.classList.contains("light-mode");

            if (isLightMode) {
                sunIcon.classList.add("hidden");
                moonIcon.classList.remove("hidden");
            } else {
                sunIcon.classList.remove("hidden");
                moonIcon.classList.add("hidden");
            }
        });
    }

    // 4. Controles e Eventos de Navegação
    if (pageFlip) {
        // Toca o som de virada quando a página começa a virar
        pageFlip.on("changeState", (e) => {
            if (e.data === "flipping") {
                playPaperTurnSound();
            }
        });

        // Alterna a visibilidade das setas dependendo da página atual
        pageFlip.on("flip", (e) => {
            const currentPage = e.data;
            const totalPages = pageFlip.getPageCount();

            // Esconde o botão esquerdo na página de capa
            if (currentPage === 0) {
                btnPrev.classList.add("hidden");
            } else {
                btnPrev.classList.remove("hidden");
            }

            // Esconde o botão direito na contracapa
            if (currentPage === totalPages - 1) {
                btnNext.classList.add("hidden");
            } else {
                btnNext.classList.remove("hidden");
            }
        });

        // Eventos de clique para as setas de navegação
        btnPrev.addEventListener("click", () => {
            pageFlip.flipPrev();
        });

        btnNext.addEventListener("click", () => {
            pageFlip.flipNext();
        });

        // Eventos de teclado para as setas de navegação
        document.addEventListener("keydown", (e) => {
            if (e.key === "ArrowLeft") {
                pageFlip.flipPrev();
            } else if (e.key === "ArrowRight") {
                pageFlip.flipNext();
            }
        });

        // Esconde o botão esquerdo inicialmente, já que a página inicial é 0
        btnPrev.classList.add("hidden");
    }

    // ===================================================
    // LÓGICA DE AUTENTICAÇÃO E USER MODAL
    // ===================================================
    const userToggle = document.getElementById("user-toggle");
    const userBadge = document.getElementById("user-badge");
    const authModal = document.getElementById("auth-modal");
    const authModalClose = document.getElementById("auth-modal-close");
    const authTabsContainer = document.getElementById("auth-tabs-container");
    const tabLogin = document.getElementById("tab-login");
    const tabRegister = document.getElementById("tab-register");
    const formLogin = document.getElementById("form-login");
    const formRegister = document.getElementById("form-register");
    const authProfile = document.getElementById("auth-profile");
    const profileUsername = document.getElementById("profile-username");
    const btnLogout = document.getElementById("btn-logout");
    const loginError = document.getElementById("login-error");
    const registerError = document.getElementById("register-error");
    const registerSuccess = document.getElementById("register-success");

    let currentUser = null;

    // Helper: Atualiza os elementos da interface baseando-se no estado logado/deslogado
    function updateAuthUI() {
        if (currentUser) {
            userBadge.classList.remove("hidden");
            profileUsername.textContent = currentUser.username;
        } else {
            userBadge.classList.add("hidden");
            profileUsername.textContent = "";
        }
    }

    // Helper: Verifica se o token JWT está salvo e é válido
    async function checkLoginStatus() {
        const token = sessionStorage.getItem("access_token");
        if (!token) {
            currentUser = null;
            updateAuthUI();
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/auth/me`, {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            });

            if (response.ok) {
                currentUser = await response.json();
            } else {
                // Token inválido ou expirado
                sessionStorage.removeItem("access_token");
                currentUser = null;
            }
        } catch (error) {
            console.warn("⚠️ Não foi possível verificar o status de login:", error.message);
            // Em caso de erro de rede, mantemos o token local mas não assumimos nada
        }
        updateAuthUI();
    }

    // Executa verificação inicial de login
    checkLoginStatus();

    // Abre e fecha Modal
    userToggle.addEventListener("click", () => {
        // Limpa mensagens anteriores
        loginError.classList.add("hidden");
        registerError.classList.add("hidden");
        registerSuccess.classList.add("hidden");
        formLogin.reset();
        formRegister.reset();

        authModal.classList.remove("hidden");

        if (currentUser) {
            // Mostra perfil
            authTabsContainer.classList.add("hidden");
            formLogin.classList.add("hidden");
            formRegister.classList.add("hidden");
            authProfile.classList.remove("hidden");
        } else {
            // Mostra aba de login
            authTabsContainer.classList.remove("hidden");
            switchTab("login");
        }
    });

    const closeModal = () => {
        authModal.classList.add("hidden");
    };

    authModalClose.addEventListener("click", closeModal);
    
    // Clicar fora do modal fecha o modal
    authModal.querySelector(".auth-modal-overlay").addEventListener("click", closeModal);

    // Alternar entre abas do modal (Login / Cadastro)
    function switchTab(tab) {
        if (tab === "login") {
            tabLogin.classList.add("active");
            tabRegister.classList.remove("active");
            formLogin.classList.remove("hidden");
            formRegister.classList.add("hidden");
            loginError.classList.add("hidden");
        } else {
            tabLogin.classList.remove("active");
            tabRegister.classList.add("active");
            formLogin.classList.add("hidden");
            formRegister.classList.remove("hidden");
            registerError.classList.add("hidden");
            registerSuccess.classList.add("hidden");
        }
    }

    tabLogin.addEventListener("click", () => switchTab("login"));
    tabRegister.addEventListener("click", () => switchTab("register"));

    // Submissão do Formulário de Login
    formLogin.addEventListener("submit", async (e) => {
        e.preventDefault();
        loginError.classList.add("hidden");

        const username = document.getElementById("login-username").value.trim();
        const password = document.getElementById("login-password").value;

        try {
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || "Erro ao fazer login.");
            }

            sessionStorage.setItem("access_token", data.access_token);
            await checkLoginStatus();
            closeModal();
            
            // Recarrega figurinhas se necessário
            if (typeof preencherFigurinhas === "function") {
                preencherFigurinhas(pageFlip);
            }

        } catch (error) {
            loginError.textContent = error.message;
            loginError.classList.remove("hidden");
        }
    });

    // Submissão do Formulário de Cadastro
    formRegister.addEventListener("submit", async (e) => {
        e.preventDefault();
        registerError.classList.add("hidden");
        registerSuccess.classList.add("hidden");

        const username = document.getElementById("register-username").value.trim();
        const password = document.getElementById("register-password").value;
        const confirmPassword = document.getElementById("register-confirm-password").value;

        if (password !== confirmPassword) {
            registerError.textContent = "As senhas não coincidem.";
            registerError.classList.remove("hidden");
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/auth/register`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || "Erro ao cadastrar usuário.");
            }

            registerSuccess.textContent = "Conta criada com sucesso! Entrando...";
            registerSuccess.classList.remove("hidden");

            // Auto-login após cadastro bem-sucedido
            setTimeout(async () => {
                try {
                    const loginResponse = await fetch(`${API_BASE_URL}/auth/login`, {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({ username, password })
                    });
                    if (loginResponse.ok) {
                        const loginData = await loginResponse.json();
                        sessionStorage.setItem("access_token", loginData.access_token);
                        await checkLoginStatus();
                        closeModal();
                        if (typeof preencherFigurinhas === "function") {
                            preencherFigurinhas(pageFlip);
                        }
                    } else {
                        switchTab("login");
                    }
                } catch (err) {
                    switchTab("login");
                }
            }, 1200);

        } catch (error) {
            registerError.textContent = error.message;
            registerError.classList.remove("hidden");
        }
    });

    // Evento de Logout
    btnLogout.addEventListener("click", () => {
        sessionStorage.removeItem("access_token");
        sessionStorage.removeItem("figurinhas_reveladas");
        currentUser = null;
        figurinhasReveladas.clear();
        updateAuthUI();
        closeModal();
        
        // Recarrega figurinhas se necessário
        if (typeof preencherFigurinhas === "function") {
            preencherFigurinhas(pageFlip);
        }
    });

    // Clique nos Slots de Figurinhas para Colar/Descolar
    const slots = document.querySelectorAll(".sticker-slot");
    slots.forEach(slot => {
        slot.addEventListener("click", async (e) => {
            // Evita disparar cliques se estivermos arrastando a página do livro
            if (document.body.classList.contains("dragging")) return;

            const slotNumeroEl = slot.querySelector(".slot-number");
            if (!slotNumeroEl) return;

            const id = parseInt(slotNumeroEl.textContent.replace("#", ""), 10);
            const token = sessionStorage.getItem("access_token");

            // Se não estiver logado, abre o modal de login
            if (!token) {
                loginError.classList.add("hidden");
                formLogin.reset();
                authTabsContainer.classList.remove("hidden");
                switchTab("login");
                authModal.classList.remove("hidden");
                return;
            }

            if (!todasFigurinhas.has(id)) return;
            const figurinha = todasFigurinhas.get(id);

            // Caso 1: Figurinha colada mas ainda não revelada (revela ao clicar)
            if (figurinhasColadas.includes(id) && !figurinhasReveladas.has(id)) {
                figurinhasReveladas.add(id);
                sessionStorage.setItem("figurinhas_reveladas", JSON.stringify(Array.from(figurinhasReveladas)));

                const overlay = slot.querySelector(".sticker-reveal-overlay");
                if (overlay) overlay.remove();
                slot.classList.remove("slot-revelavel");

                const img = document.createElement("img");
                img.src = `${API_BASE_URL}${figurinha.imagem_url}`;
                img.alt = figurinha.nome;
                img.className = "sticker-img reveal-animation";
                img.onload = () => {
                    slot.classList.add("slot-preenchido");
                    if (pageFlip) {
                        pageFlip.update();
                    }
                };
                slot.insertBefore(img, slot.firstChild);
                console.log(`✨ Figurinha ${id} revelada!`);
                return;
            }

            // Caso 2: Figurinha colada e já revelada (confirma descolamento se clicar novamente)
            if (figurinhasColadas.includes(id) && figurinhasReveladas.has(id)) {
                const confirmar = confirm(`Deseja descolar a figurinha de ${figurinha.nome}?`);
                if (confirmar) {
                    try {
                        const response = await fetch(`${API_BASE_URL}/figurinhas/user/me/collect/${id}`, {
                            method: "DELETE",
                            headers: { "Authorization": `Bearer ${token}` }
                        });
                        if (response.ok) {
                            // Atualiza a coleção local
                            figurinhasColadas = figurinhasColadas.filter(item => item !== id);
                            figurinhasReveladas.delete(id);
                            sessionStorage.setItem("figurinhas_reveladas", JSON.stringify(Array.from(figurinhasReveladas)));

                            // Remove imagem e classe
                            const img = slot.querySelector(".sticker-img");
                            if (img) img.remove();
                            slot.classList.remove("slot-preenchido");
                            console.log(`❌ Figurinha ${id} descolada.`);
                            
                            // Atualiza a visualização do PageFlip
                            if (pageFlip) {
                                pageFlip.update();
                            }
                        } else {
                            const errData = await response.json();
                            alert(errData.detail || "Erro ao descolar figurinha.");
                        }
                    } catch (err) {
                        console.error("Erro ao descolar:", err);
                    }
                }
            } else {
                // Caso 3: Não colada (cola e revela imediatamente)
                try {
                    const response = await fetch(`${API_BASE_URL}/figurinhas/user/me/collect/${id}`, {
                        method: "POST",
                        headers: { "Authorization": `Bearer ${token}` }
                    });
                    if (response.ok) {
                        // Atualiza a coleção local
                        figurinhasColadas.push(id);
                        figurinhasReveladas.add(id);
                        sessionStorage.setItem("figurinhas_reveladas", JSON.stringify(Array.from(figurinhasReveladas)));

                        // Cria e insere a imagem
                        const img = document.createElement("img");
                        img.src = `${API_BASE_URL}${figurinha.imagem_url}`;
                        img.alt = figurinha.nome;
                        img.className = "sticker-img reveal-animation";
                        img.onload = () => {
                            slot.classList.add("slot-preenchido");
                            if (pageFlip) {
                                pageFlip.update();
                            }
                        };
                        slot.insertBefore(img, slot.firstChild);
                        console.log(`✅ Figurinha ${id} colada.`);
                    } else {
                        const errData = await response.json();
                        alert(errData.detail || "Erro ao colar figurinha.");
                    }
                } catch (err) {
                    console.error("Erro ao colar:", err);
                }
            }
        });
    });
});

