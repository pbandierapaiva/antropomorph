document.addEventListener('DOMContentLoaded', function() {
    lucide.createIcons();

    let lastBatchResults = null;
    let peopleList = []; // Array para armazenar as pessoas adicionadas manualmente

    // Elementos da UI
    const navLinks = document.querySelectorAll('.sidebar-nav .nav-link, .sidebar-footer .nav-link');
    const pageSections = document.querySelectorAll('.page-section');
    const pageTitle = document.getElementById('page-title');
    const mobileMenuOverlay = document.getElementById('mobile-menu-overlay');
    const menuToggle = document.getElementById('menu-toggle');
    const closeMenu = document.getElementById('close-menu');

    // Elementos da nova interface unificada
    const addPersonForm = document.getElementById('addPersonForm');
    const peopleListContainer = document.getElementById('people-list-container');
    const peopleTableBody = document.getElementById('people-table-body');
    const peopleCount = document.getElementById('people-count');
    const processAllBtn = document.getElementById('process-all-btn');
    const clearAllBtn = document.getElementById('clear-all-btn');
    
    // Elementos de informações gerais
    const escolaNomeInput = document.getElementById('escola-nome');
    const turmaNomeInput = document.getElementById('turma-nome');
    
    // Elementos de arquivo
    const batchFileInput = document.getElementById('batchFile');
    const fileInfoDisplay = document.getElementById('file-info-display');

    // Elementos de loading e erro unificados
    const loadingProcess = document.getElementById('loading-process');
    const errorMessage = document.getElementById('error-message');

    // Elementos de resultado
    const resultsDisplay = document.getElementById('results-display');
    const resultsSummary = document.getElementById('results-summary');
    const resultsActions = document.getElementById('results-actions');
    const resultsTableBody = document.getElementById('results-table-body');
    const resultsErrorsDisplay = document.getElementById('results-errors-display');
    const resultsErrorList = document.getElementById('results-error-list');

    const recentActivityTableBody = document.querySelector('#recent-activity-table tbody');

    // Função para limpar todos os resultados
    function clearAllResults() {
        if (resultsDisplay) resultsDisplay.style.display = 'none';
        if (resultsSummary) resultsSummary.innerHTML = '';
        if (resultsTableBody) resultsTableBody.innerHTML = '';
        if (resultsErrorList) resultsErrorList.innerHTML = '';
        if (resultsErrorsDisplay) resultsErrorsDisplay.style.display = 'none';
        if (resultsActions) resultsActions.innerHTML = '';
        displayError('');
    }

    // Função para exibir loading
    function displayLoading(show) {
        if (loadingProcess) loadingProcess.style.display = show ? 'flex' : 'none';
    }

    // Função para exibir erros
    function displayError(message) {
        if (errorMessage) {
            errorMessage.textContent = message;
            errorMessage.style.display = message ? 'block' : 'none';
        }
    }

    // Função para adicionar pessoa à lista
    function addPersonToList(personData) {
        // Gera um ID único para a pessoa
        personData.id = Date.now() + Math.random();
        peopleList.push(personData);
        updatePeopleTable();
        updatePeopleCount();
        showPeopleListContainer();
    }

    // Função para remover pessoa da lista
    function removePersonFromList(personId) {
        peopleList = peopleList.filter(person => person.id !== personId);
        updatePeopleTable();
        updatePeopleCount();
        if (peopleList.length === 0) {
            hidePeopleListContainer();
        }
    }

    // Função para atualizar a tabela de pessoas
    function updatePeopleTable() {
        if (!peopleTableBody) return;
        
        peopleTableBody.innerHTML = '';
        peopleList.forEach(person => {
            const row = peopleTableBody.insertRow();
            row.insertCell().textContent = person.nome;
            row.insertCell().textContent = formatDateToBrazilian(person.data_nascimento);
            row.insertCell().textContent = formatDateToBrazilian(person.data_avaliacao);
            row.insertCell().textContent = person.sexo === 'M' ? 'Masculino' : 'Feminino';
            row.insertCell().textContent = `${person.peso_kg} kg`;
            row.insertCell().textContent = `${person.altura_cm} cm`;
            
            const actionsCell = row.insertCell();
            const removeBtn = document.createElement('button');
            removeBtn.className = 'btn btn-sm btn-secondary';
            removeBtn.innerHTML = '<i data-lucide="trash-2" style="width: 16px; height: 16px;"></i>';
            removeBtn.onclick = () => removePersonFromList(person.id);
            actionsCell.appendChild(removeBtn);
        });
        lucide.createIcons();
    }

    // Função para atualizar o contador de pessoas
    function updatePeopleCount() {
        if (peopleCount) {
            peopleCount.textContent = peopleList.length;
        }
    }

    // Função para mostrar/esconder o container da lista
    function showPeopleListContainer() {
        if (peopleListContainer) {
            peopleListContainer.style.display = 'block';
        }
    }

    function hidePeopleListContainer() {
        if (peopleListContainer) {
            peopleListContainer.style.display = 'none';
        }
    }

    // Função para limpar todas as pessoas da lista
    function clearAllPeople() {
        peopleList = [];
        updatePeopleTable();
        updatePeopleCount();
        hidePeopleListContainer();
    }

    // Função para mostrar página
    function showPage(pageId) {
        pageSections.forEach(section => section.classList.remove('active-section'));
        const activePage = document.getElementById(`${pageId}-section`);
        if (activePage) {
            activePage.classList.add('active-section');
            const correspondingLink = document.querySelector(`.nav-link[data-section="${pageId}"]`);
            if (correspondingLink && pageTitle) pageTitle.textContent = correspondingLink.textContent.trim();
        } else {
            document.getElementById('dashboard-section')?.classList.add('active-section');
            if (pageTitle) pageTitle.textContent = "Dashboard";
        }
        clearAllResults();
    }

    // Event listeners para navegação
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const pageId = this.getAttribute('data-section');
            navLinks.forEach(l => l.classList.remove('active'));
            document.querySelectorAll(`.nav-link[data-section="${pageId}"]`).forEach(activeLink => activeLink.classList.add('active'));
            showPage(pageId);
            if (mobileMenuOverlay && window.getComputedStyle(mobileMenuOverlay).display === 'block') {
                mobileMenuOverlay.style.display = 'none';
            }
        });
    });

    // Menu mobile
    if (menuToggle) menuToggle.addEventListener('click', () => mobileMenuOverlay.style.display = 'block');
    if (closeMenu) closeMenu.addEventListener('click', () => mobileMenuOverlay.style.display = 'none');
    if (mobileMenuOverlay) mobileMenuOverlay.addEventListener('click', (e) => {
        if (e.target === mobileMenuOverlay) mobileMenuOverlay.style.display = 'none';
    });

    // Event listener para adicionar pessoa
    if (addPersonForm) {
        addPersonForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(addPersonForm);
            const personData = {
                nome: formData.get('nome'),
                data_nascimento: formData.get('data_nascimento'),
                data_avaliacao: formData.get('data_avaliacao'),
                sexo: formData.get('sexo'),
                peso_kg: parseFloat(formData.get('peso_kg')),
                altura_cm: parseFloat(formData.get('altura_cm'))
            };
            
            addPersonToList(personData);
            addPersonForm.reset();
            // Redefine a data de avaliação para hoje
            const today = new Date().toISOString().split('T')[0];
            if (document.getElementById('data_avaliacao')) {
                document.getElementById('data_avaliacao').value = today;
            }
        });
    }

    // Event listener para limpar formulário
    document.getElementById('clearPersonForm')?.addEventListener('click', function() {
        addPersonForm.reset();
        const today = new Date().toISOString().split('T')[0];
        if (document.getElementById('data_avaliacao')) {
            document.getElementById('data_avaliacao').value = today;
        }
    });

    // Event listener para processar todas as pessoas
    if (processAllBtn) {
        processAllBtn.addEventListener('click', async function() {
            if (peopleList.length === 0) {
                alert('Nenhuma pessoa foi adicionada à lista.');
                return;
            }

            await processManualBatch();
        });
    }

    // Event listener para limpar todas as pessoas
    if (clearAllBtn) {
        clearAllBtn.addEventListener('click', function() {
            if (confirm('Tem certeza que deseja limpar todas as pessoas da lista?')) {
                clearAllPeople();
            }
        });
    }

    // Event listener para upload de arquivo
    if (batchFileInput) {
        batchFileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                displayFileInfo(file);
            } else {
                hideFileInfo();
            }
        });
    }

    // Função para processar lote manual
    async function processManualBatch() {
        displayLoading(true);
        displayError('');
        clearAllResults();

        try {
            // Adiciona informações opcionais da escola/turma
            const escola = escolaNomeInput?.value?.trim() || '';
            const turma = turmaNomeInput?.value?.trim() || '';
            
            const peopleWithBatchInfo = peopleList.map(person => ({
                ...person,
                escola: escola,
                turma: turma
            }));

            const response = await fetch('/api/processar/manual-batch', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ pessoas: peopleWithBatchInfo })
            });

            if (!response.ok) {
                throw new Error(`Erro do servidor: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.success) {
                lastBatchResults = result;
                displayResults(result);
                updateRecentActivity('batch', result);
            } else {
                displayError(result.error || 'Erro desconhecido');
            }
        } catch (error) {
            console.error('Erro no processamento do lote:', error);
            displayError('Erro ao processar lote: ' + error.message);
        } finally {
            displayLoading(false);
        }
    }

    // Função para processar arquivo CSV/TSV
    async function processBatchFile() {
        const fileInput = batchFileInput;
        if (!fileInput || !fileInput.files[0]) {
            displayError('Por favor, selecione um arquivo.');
            return;
        }

        const file = fileInput.files[0];
        displayLoading(true);
        displayError('');
        clearAllResults();

        try {
            const formData = new FormData();
            formData.append('file', file);

            // Adiciona informações opcionais da escola/turma
            const escola = escolaNomeInput?.value?.trim() || '';
            const turma = turmaNomeInput?.value?.trim() || '';
            
            if (escola) formData.append('escola', escola);
            if (turma) formData.append('turma', turma);

            const response = await fetch('/api/processar/lote', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Erro do servidor: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.success) {
                lastBatchResults = result;
                displayResults(result);
                updateRecentActivity('batch', result);
            } else {
                displayError(result.error || 'Erro desconhecido');
            }
        } catch (error) {
            console.error('Erro no processamento do lote:', error);
            displayError('Erro ao processar arquivo: ' + error.message);
        } finally {
            displayLoading(false);
        }
    }

    // Botão para processar arquivo
    document.getElementById('process-file-btn')?.addEventListener('click', processBatchFile);

    // Função para exibir informações do arquivo
    function displayFileInfo(file) {
        if (fileInfoDisplay) {
            fileInfoDisplay.innerHTML = `
                <div class="file-info">
                    <i data-lucide="file-text" style="width: 20px; height: 20px;"></i>
                    <div>
                        <div class="file-name">${file.name}</div>
                        <div class="file-details">${(file.size / 1024).toFixed(1)} KB</div>
                    </div>
                </div>
            `;
            fileInfoDisplay.style.display = 'block';
            lucide.createIcons();
        }
    }

    function hideFileInfo() {
        if (fileInfoDisplay) {
            fileInfoDisplay.style.display = 'none';
        }
    }

    // Função para exibir resultados
    function displayResults(result) {
        if (!resultsDisplay) return;

        resultsDisplay.style.display = 'block';

        // Exibir resumo
        if (resultsSummary) {
            resultsSummary.innerHTML = `
                <div class="summary-cards">
                    <div class="summary-card">
                        <span class="summary-label">Total de Pessoas:</span>
                        <span class="summary-value">${result.total_pessoas}</span>
                    </div>
                    <div class="summary-card">
                        <span class="summary-label">Processadas com Sucesso:</span>
                        <span class="summary-value text-success">${result.processadas_com_sucesso}</span>
                    </div>
                    <div class="summary-card">
                        <span class="summary-label">Erros:</span>
                        <span class="summary-value text-danger">${result.erros}</span>
                    </div>
                </div>
            `;
        }

        // Exibir tabela de resultados
        if (resultsTableBody && result.resultados && result.resultados.length > 0) {
            resultsTableBody.innerHTML = '';
            result.resultados.forEach(pessoa => {
                const row = resultsTableBody.insertRow();
                row.insertCell().textContent = pessoa.nome;
                row.insertCell().textContent = formatDateToBrazilian(pessoa.data_nascimento);
                row.insertCell().textContent = pessoa.sexo === 'M' ? 'Masculino' : 'Feminino';
                row.insertCell().textContent = `${pessoa.peso_kg} kg`;
                row.insertCell().textContent = `${pessoa.altura_cm} cm`;

                // Células de classificação
                const pesoIdadeCell = row.insertCell();
                pesoIdadeCell.innerHTML = `<span class="status-badge ${getNutritionalStatusClass(pessoa.classificacao_peso_idade)}">${pessoa.classificacao_peso_idade || 'N/A'}</span>`;

                const estaturaIdadeCell = row.insertCell();
                estaturaIdadeCell.innerHTML = `<span class="status-badge ${getNutritionalStatusClass(pessoa.classificacao_estatura_idade)}">${pessoa.classificacao_estatura_idade || 'N/A'}</span>`;

                const pesoEstaturaCell = row.insertCell();
                pesoEstaturaCell.innerHTML = `<span class="status-badge ${getNutritionalStatusClass(pessoa.classificacao_peso_estatura)}">${pessoa.classificacao_peso_estatura || 'N/A'}</span>`;

                const imcIdadeCell = row.insertCell();
                imcIdadeCell.innerHTML = `<span class="status-badge ${getNutritionalStatusClass(pessoa.classificacao_imc_idade)}">${pessoa.classificacao_imc_idade || 'N/A'}</span>`;
            });
        }

        // Exibir erros se houver
        if (result.detalhes_erros && result.detalhes_erros.length > 0) {
            if (resultsErrorsDisplay) resultsErrorsDisplay.style.display = 'block';
            if (resultsErrorList) {
                resultsErrorList.innerHTML = '';
                result.detalhes_erros.forEach(erro => {
                    const listItem = document.createElement('li');
                    listItem.innerHTML = `<strong>Linha ${erro.linha}:</strong> ${erro.erro}`;
                    resultsErrorList.appendChild(listItem);
                });
            }
        }

        // Botões de ação
        if (resultsActions) {
            resultsActions.innerHTML = `
                <button class="btn btn-primary" onclick="downloadExcel()">
                    <i data-lucide="download" style="width: 16px; height: 16px;"></i>
                    Baixar Excel
                </button>
                <button class="btn btn-primary" onclick="downloadPDF()">
                    <i data-lucide="file-text" style="width: 16px; height: 16px;"></i>
                    Baixar PDF
                </button>
                <button class="btn btn-secondary" onclick="clearAllResults()">
                    <i data-lucide="x" style="width: 16px; height: 16px;"></i>
                    Limpar Resultados
                </button>
            `;
            lucide.createIcons();
        }
    }

    // Função para baixar Excel
    window.downloadExcel = function() {
        if (lastBatchResults && lastBatchResults.batch_id) {
            window.open(`/api/download/excel/${lastBatchResults.batch_id}`, '_blank');
        }
    };

    // Função para baixar PDF
    window.downloadPDF = function() {
        if (lastBatchResults && lastBatchResults.batch_id) {
            window.open(`/api/download/pdf/${lastBatchResults.batch_id}`, '_blank');
        }
    };

    // Função para atualizar atividade recente
    function updateRecentActivity(type, result) {
        if (!recentActivityTableBody) return;

        const now = new Date();
        const timeString = now.toLocaleTimeString('pt-BR');
        const dateString = now.toLocaleDateString('pt-BR');
        
        const row = recentActivityTableBody.insertRow(0);
        row.insertCell().textContent = `${dateString} ${timeString}`;
        row.insertCell().textContent = type === 'batch' ? 'Lote' : 'Individual';
        row.insertCell().textContent = result.total_pessoas || 1;
        row.insertCell().textContent = result.processadas_com_sucesso || (result.success ? 1 : 0);
        
        const statusCell = row.insertCell();
        statusCell.innerHTML = result.success ? 
            '<span class="status-badge bg-emerald-100 text-emerald-700">Sucesso</span>' : 
            '<span class="status-badge bg-red-100 text-red-700">Erro</span>';

        // Manter apenas as últimas 10 entradas
        while (recentActivityTableBody.rows.length > 10) {
            recentActivityTableBody.deleteRow(-1);
        }
    }

    // Funções auxiliares
    function formatDateToBrazilian(dateString) {
        if (!dateString) return 'N/A';
        const [year, month, day] = dateString.split('-');
        if (!year || !month || !day) return dateString;
        return `${day}/${month}/${year}`;
    }

    function getNutritionalStatusClass(classificationText) {
        if (!classificationText) return 'bg-slate-100 text-slate-700';
        const lowerClass = classificationText.toLowerCase();
        if (lowerClass.includes('magreza acentuada') || lowerClass.includes('muito baixo peso')) return 'bg-red-100 text-red-700';
        if (lowerClass.includes('magreza') || lowerClass.includes('baixo peso') || lowerClass.includes('baixa estatura')) return 'bg-rose-100 text-rose-700';
        if (lowerClass.includes('eutrofia') || lowerClass.includes('peso adequado') || lowerClass.includes('estatura adequada')) return 'bg-emerald-100 text-emerald-700';
        if (lowerClass.includes('risco de sobrepeso')) return 'bg-amber-100 text-amber-700';
        if (lowerClass.includes('sobrepeso')) return 'bg-amber-100 text-amber-600';
        if (lowerClass.includes('obesidade grave')) return 'bg-red-100 text-red-700';
        if (lowerClass.includes('obesidade')) return 'bg-rose-100 text-rose-700';
        return 'bg-slate-100 text-slate-700';
    }

    // Inicializar data de avaliação como hoje
    const today = new Date().toISOString().split('T')[0];
    const dataAvaliacaoInput = document.getElementById('data_avaliacao');
    if (dataAvaliacaoInput && !dataAvaliacaoInput.value) {
        dataAvaliacaoInput.value = today;
    }

    // Mostrar a página inicial
    showPage('dashboard');
});
