document.addEventListener('DOMContentLoaded', function () {
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
    const processFileBtn = document.getElementById('process-file-btn');


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
        
        // Limpar dados do lote em memória
        lastBatchResults = null;
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

    // Função para exibir mensagem de sucesso temporária
    function displaySuccess(message) {
        if (errorMessage) {
            errorMessage.textContent = message;
            errorMessage.style.display = 'block';
            errorMessage.className = 'success';
            
            // Voltar ao estilo de erro após 3 segundos
            setTimeout(() => {
                errorMessage.className = 'error';
                errorMessage.style.display = 'none';
            }, 3000);
        }
    }

    // Função para adicionar pessoa à lista (não usada no processamento automático)
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
            row.insertCell().textContent = person.nome || 'Não informado';
            row.insertCell().textContent = formatDateObjectToBrazilian(person.data_nascimento);
            row.insertCell().textContent = formatDateObjectToBrazilian(person.data_avaliacao);
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
            
            // Definir títulos específicos para cada página
            const pageTitles = {
                'dashboard': 'Boas-vindas',
                'avaliacao': 'Avaliação Antropométrica',
                'relatorios': 'Relatórios',
                'configuracoes': 'Configurações'
            };
            
            if (pageTitle) {
                pageTitle.textContent = pageTitles[pageId] || pageId;
            }
        } else {
            document.getElementById('dashboard-section')?.classList.add('active-section');
            if (pageTitle) pageTitle.textContent = "Boas-vindas";
        }
        clearAllResults();
    }

    // Event listeners para navegação
    navLinks.forEach(link => {
        link.addEventListener('click', function (e) {
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

    // Event listener para botão "Iniciar Avaliação" na página de boas-vindas
    const startEvaluationBtn = document.getElementById('start-evaluation-btn');
    if (startEvaluationBtn) {
        startEvaluationBtn.addEventListener('click', function () {
            // Navegar para a página de avaliação
            navLinks.forEach(l => l.classList.remove('active'));
            document.querySelectorAll(`.nav-link[data-section="avaliacao"]`).forEach(activeLink => activeLink.classList.add('active'));
            showPage('avaliacao');
        });
    }

    // Menu mobile
    if (menuToggle) menuToggle.addEventListener('click', () => mobileMenuOverlay.style.display = 'block');
    if (closeMenu) closeMenu.addEventListener('click', () => mobileMenuOverlay.style.display = 'none');
    if (mobileMenuOverlay) mobileMenuOverlay.addEventListener('click', (e) => {
        if (e.target === mobileMenuOverlay) mobileMenuOverlay.style.display = 'none';
    });

    // Event listener para adicionar pessoa
    if (addPersonForm) {
        addPersonForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            const formData = new FormData(addPersonForm);
            const personData = {
                id_paciente: formData.get('id_paciente'),
                nome: formData.get('nome'),
                data_nascimento: formData.get('data_nascimento'),
                data_avaliacao: formData.get('data_avaliacao'),
                sexo: formData.get('sexo'),
                peso_kg: parseFloat(formData.get('peso_kg')),
                altura_cm: parseFloat(formData.get('altura_cm'))
            };

            // Processar automaticamente a pessoa adicionada
            await processAndAddPerson(personData);
            
            addPersonForm.reset();
            // Redefine a data de avaliação para hoje
            const today = new Date().toISOString().split('T')[0];
            if (document.getElementById('data_avaliacao')) {
                document.getElementById('data_avaliacao').value = today;
            }
        });
    }

    // Event listener para limpar formulário
    document.getElementById('clearPersonForm')?.addEventListener('click', function () {
        addPersonForm.reset();
        const today = new Date().toISOString().split('T')[0];
        if (document.getElementById('data_avaliacao')) {
            document.getElementById('data_avaliacao').value = today;
        }
    });

    // Event listener para processar todas as pessoas
    if (processAllBtn) {
        processAllBtn.addEventListener('click', async function () {
            if (peopleList.length === 0) {
                alert('Nenhuma pessoa foi adicionada à lista.');
                return;
            }
            await processManualBatch();
        });
    }

    // Event listener para limpar todas as pessoas
    if (clearAllBtn) {
        clearAllBtn.addEventListener('click', function () {
            if (confirm('Tem certeza que deseja limpar todas as pessoas da lista?')) {
                clearAllPeople();
            }
        });
    }

    // Event listener para upload de arquivo
    if (batchFileInput) {
        batchFileInput.addEventListener('change', function (e) {
            const file = e.target.files[0];
            if (file) {
                displayFileInfo(file);
            } else {
                hideFileInfo();
            }
        });
    }

    // Event listener para o botão de processar arquivo
    if (processFileBtn) {
        processFileBtn.addEventListener('click', async function () {
            await processBatchFile();
        });
    }

    // Função para formatar data para o padrão brasileiro (DD/MM/AAAA)
    function formatDateToBrazilian(dateString) {
        if (!dateString) return 'N/A';
        
        // Se já está no formato brasileiro, retorna como está
        if (dateString.includes('/')) {
            return dateString;
        }
        
        // Se está no formato YYYY-MM-DD, converte
        const [year, month, day] = dateString.split('-');
        return `${day}/${month}/${year}`;
    }

    // Função para formatar data de objeto Date para string brasileira
    function formatDateObjectToBrazilian(dateObj) {
        if (!dateObj) return 'N/A';
        
        // Se é uma string, usar a função anterior
        if (typeof dateObj === 'string') {
            return formatDateToBrazilian(dateObj);
        }
        
        // Se é um objeto Date
        if (dateObj instanceof Date) {
            const day = dateObj.getDate().toString().padStart(2, '0');
            const month = (dateObj.getMonth() + 1).toString().padStart(2, '0');
            const year = dateObj.getFullYear();
            return `${day}/${month}/${year}`;
        }
        
        return 'N/A';
    }

    // Função para mostrar informações do arquivo selecionado
    function displayFileInfo(file) {
        const infoContainer = document.querySelector('#file-info-display .file-info');
        if (fileInfoDisplay && infoContainer) {
            infoContainer.innerHTML = `
                <p><strong>Arquivo:</strong> ${file.name}</p>
                <p><strong>Tamanho:</strong> ${(file.size / 1024).toFixed(2)} KB</p>
                <p><strong>Tipo:</strong> ${file.type || 'Não reconhecido'}</p>
            `;
            fileInfoDisplay.style.display = 'block';
        }
        if (processFileBtn) {
            processFileBtn.disabled = false;
        }
    }

    // Função para esconder informações do arquivo
    function hideFileInfo() {
        const infoContainer = document.querySelector('#file-info-display .file-info');
        if (fileInfoDisplay && infoContainer) {
            fileInfoDisplay.style.display = 'none';
            infoContainer.innerHTML = '';
        }
        if (processFileBtn) {
            processFileBtn.disabled = true;
        }
    }

    // Função para processar e adicionar uma pessoa individualmente
    async function processAndAddPerson(personData) {
        try {
            displayLoading(true);
            displayError('');
            
            // Processar a pessoa individualmente
            const response = await fetch('/api/processar/individual', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(personData)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Erro desconhecido' }));
                throw new Error(errorData.detail || `Erro do servidor: ${response.status}`);
            }

            const resultado = await response.json();
            
            // Se já existem resultados de lote, adicionar à lista existente
            if (lastBatchResults && lastBatchResults.results) {
                lastBatchResults.results.push(resultado);
                lastBatchResults.summary.total_processed += 1;
                lastBatchResults.summary.success_count += 1;
            } else {
                // Criar nova estrutura de resultados
                lastBatchResults = {
                    success: true,
                    summary: {
                        total_processed: 1,
                        success_count: 1,
                        error_count: 0
                    },
                    results: [resultado],
                    errors: []
                };
            }

            // Atualizar a exibição com os resultados atualizados
            displayResults(lastBatchResults);
            updateRecentActivity('individual', lastBatchResults);
            
            // Exibir mensagem de sucesso
            displaySuccess(`${personData.nome} foi processado(a) e adicionado(a) aos resultados com sucesso!`);
            
        } catch (error) {
            console.error('Erro no processamento individual:', error);
            displayError('Erro ao processar pessoa: ' + error.message);
            
            // Adicionar erro à lista de erros se já existem resultados
            if (lastBatchResults && lastBatchResults.errors) {
                const erroLinha = {
                    linha: lastBatchResults.results.length + lastBatchResults.errors.length + 1,
                    erro: error.message,
                    dados_originais: personData
                };
                lastBatchResults.errors.push(erroLinha);
                lastBatchResults.summary.total_processed += 1;
                lastBatchResults.summary.error_count += 1;
                
                // Atualizar exibição com os erros
                displayResults(lastBatchResults);
            }
        } finally {
            displayLoading(false);
        }
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
                body: JSON.stringify({
                    pessoas: peopleWithBatchInfo
                })
            });
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Erro desconhecido' }));
                throw new Error(errorData.detail || `Erro do servidor: ${response.status}`);
            }
            const result = await response.json();

            if (result.success) {
                lastBatchResults = result;
                displayResults(result);
                updateRecentActivity('batch', result);
                clearAllPeople(); 
            } else {
                displayError(result.error || 'Erro desconhecido no processamento do lote.');
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
        const formData = new FormData();
        formData.append('batchFile', file);

        // Adiciona informações opcionais da escola/turma (comentado até ser implementado no backend)
        // const escola = escolaNomeInput?.value?.trim() || '';
        // const turma = turmaNomeInput?.value?.trim() || '';
        // formData.append('escola', escola);
        // formData.append('turma', turma);


        displayLoading(true);
        displayError('');
        clearAllResults();

        try {
            const response = await fetch('/api/processar/lote', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Erro desconhecido ao processar o arquivo.' }));
                console.error('Erro detalhado:', errorData);
                throw new Error(errorData.detail || `Erro do servidor: ${response.status}`);
            }

            const result = await response.json();

            if (result.success) {
                lastBatchResults = result;
                displayResults(result);
                updateRecentActivity('file', result);
                // Limpa o input do arquivo após o sucesso
                if (batchFileInput) batchFileInput.value = '';
                hideFileInfo();
            } else {
                displayError(result.error || 'Erro desconhecido no processamento do arquivo.');
                if (result.errors && result.errors.length > 0) {
                    displayProcessingErrors(result.errors);
                }
            }
        } catch (error) {
            console.error('Erro no processamento do arquivo:', error);
            displayError('Erro ao processar arquivo: ' + error.message);
        } finally {
            displayLoading(false);
        }
    }

    // Função para buscar diagnósticos específicos
    function getDiagnostico(indicadores, tipo) {
        const indicador = indicadores.find(ind => ind.tipo.includes(tipo));
        return indicador ? indicador.classificacao : 'N/A';
    }

    // Função para exibir os resultados do processamento
    function displayResults(resultData) {
        if (!resultsDisplay) return;

        resultsDisplay.style.display = 'block';

        // 1. Preencher o resumo
        if (resultsSummary) {
            resultsSummary.innerHTML = `
                <div class="summary-card">
                    <h4>Total Processado</h4>
                    <p>${resultData.summary.total_processed}</p>
                </div>
                <div class="summary-card">
                    <h4>Sucessos</h4>
                    <p>${resultData.summary.success_count}</p>
                </div>
                <div class="summary-card">
                    <h4>Erros</h4>
                    <p>${resultData.summary.error_count}</p>
                </div>
            `;
        }

        // 2. Preencher a tabela de resultados
        if (resultsTableBody) {
            resultsTableBody.innerHTML = ''; // Limpa a tabela
            resultData.results.forEach(item => {
                const row = resultsTableBody.insertRow();
                row.insertCell().textContent = item.id_paciente || 'N/A';
                row.insertCell().textContent = item.nome || 'N/A';
                row.insertCell().textContent = item.idade || 'N/A';
                row.insertCell().textContent = formatDateObjectToBrazilian(item.data_nascimento);
                row.insertCell().textContent = formatDateObjectToBrazilian(item.data_avaliacao);
                row.insertCell().textContent = `${item.peso_kg} kg`;
                row.insertCell().textContent = getDiagnostico(item.indicadores, 'Peso-para-Idade');
                row.insertCell().textContent = `${item.altura_cm} cm`;
                row.insertCell().textContent = getDiagnostico(item.indicadores, 'Altura-para-Idade');
                row.insertCell().textContent = item.imc || 'N/A';
                row.insertCell().textContent = getDiagnostico(item.indicadores, 'IMC-para-Idade');
            });
        }

        // 3. Exibir erros de processamento, se houver
        if (resultData.errors && resultData.errors.length > 0) {
            displayProcessingErrors(resultData.errors);
        } else {
            if (resultsErrorsDisplay) resultsErrorsDisplay.style.display = 'none';
            if (resultsErrorList) resultsErrorList.innerHTML = '';
        }

        // 4. Adicionar botões de ação (download)
        if (resultsActions) {
            resultsActions.innerHTML = ''; // Limpa ações anteriores
            const downloadCsvBtn = document.createElement('button');
            downloadCsvBtn.className = 'btn btn-secondary';
            downloadCsvBtn.innerHTML = '<i data-lucide="download"></i> Baixar CSV';
            downloadCsvBtn.onclick = () => downloadResults('csv');

            const downloadXlsxBtn = document.createElement('button');
            downloadXlsxBtn.className = 'btn btn-secondary';
            downloadXlsxBtn.innerHTML = '<i data-lucide="download"></i> Baixar Excel';
            downloadXlsxBtn.onclick = () => downloadResults('xlsx');

            const downloadPdfBtn = document.createElement('button');
            downloadPdfBtn.className = 'btn btn-primary';
            downloadPdfBtn.innerHTML = '<i data-lucide="file-text"></i> Baixar PDF';
            downloadPdfBtn.onclick = () => downloadResults('pdf');

            resultsActions.appendChild(downloadCsvBtn);
            resultsActions.appendChild(downloadXlsxBtn);
            resultsActions.appendChild(downloadPdfBtn);
            lucide.createIcons();
        }

        // Rola a página para a seção de resultados
        resultsDisplay.scrollIntoView({ behavior: 'smooth' });
    }

    // Função para exibir erros de processamento específicos
    function displayProcessingErrors(errors) {
        if (!resultsErrorsDisplay || !resultsErrorList) return;

        resultsErrorList.innerHTML = '';
        errors.forEach(error => {
            const li = document.createElement('li');
            li.textContent = `Linha ${error.linha}: ${error.erro} - Dados: ${JSON.stringify(error.dados_originais)}`;
            resultsErrorList.appendChild(li);
        });
        resultsErrorsDisplay.style.display = 'block';
    }


    // Função para baixar os resultados
    function downloadResults(format) {
        if (!lastBatchResults) {
            alert('Não há resultados para baixar.');
            return;
        }
        const { results, summary } = lastBatchResults;
        if (!results || results.length === 0) {
            alert('Não há dados de sucesso para baixar.');
            return;
        }

        // Adiciona informações de escola e turma se existirem nos primeiros resultados
        const escola = escolaNomeInput?.value?.trim() || '';
        const turma = turmaNomeInput?.value?.trim() || '';

        if (format === 'pdf') {
            // Para PDF, usar o endpoint específico
            downloadPdfReport(results, summary, escola, turma);
        } else {
            // Para CSV e Excel, usar o endpoint genérico
            fetch(`/api/export/${format}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    results: results,
                    summary: summary,
                    escola: escola,
                    turma: turma
                }),
            })
            .then(async resp => {
                if (resp.ok) {
                    const blob = await resp.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.style.display = 'none';
                    a.href = url;
                    const timestamp = new Date().toISOString().slice(0, 19).replace(/[-:T]/g, '');
                    a.download = `resultados_antropometria_${timestamp}.${format}`;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                } else {
                    const error = await resp.json().catch(() => ({ detail: 'Erro desconhecido' }));
                    throw new Error(error.detail || 'Erro ao baixar o arquivo.');
                }
            })
            .catch(error => {
                console.error(`Erro ao baixar ${format}:`, error);
                displayError(`Não foi possível baixar o arquivo: ${error.message}`);
            });
        }
    }

    // Função para baixar relatório PDF
    function downloadPdfReport(results, summary, escola, turma) {
        const reportData = {
            identifier: escola || 'Relatório Antropométrico',
            sub_identifier: turma || '',
            batch_results: {
                success: true,
                summary: summary,
                results: results,
                errors: lastBatchResults.errors || []
            }
        };

        fetch('/api/export/pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(reportData),
        })
        .then(async resp => {
            if (resp.ok) {
                const blob = await resp.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                const timestamp = new Date().toISOString().slice(0, 19).replace(/[-:T]/g, '');
                const filename = escola ? 
                    `Relatorio_${escola.replace(/\s+/g, '_')}_${timestamp}.pdf` :
                    `Relatorio_Antropometrico_${timestamp}.pdf`;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            } else {
                const error = await resp.json().catch(() => ({ detail: 'Erro desconhecido' }));
                throw new Error(error.detail || 'Erro ao gerar relatório PDF.');
            }
        })
        .catch(error => {
            console.error('Erro ao baixar PDF:', error);
            displayError(`Não foi possível gerar o relatório PDF: ${error.message}`);
        });
    }

    // Função para atualizar a tabela de atividades recentes
    function updateRecentActivity(type, resultData) {
        if (!recentActivityTableBody) return;

        const row = recentActivityTableBody.insertRow(0); // Insere no topo
        const iconCell = row.insertCell();
        const descriptionCell = row.insertCell();
        const detailsCell = row.insertCell();
        const dateCell = row.insertCell();

        const now = new Date();
        const formattedDate = `${now.toLocaleDateString('pt-BR')} ${now.toLocaleTimeString('pt-BR')}`;

        if (type === 'batch' || type === 'file') {
            const isFile = type === 'file';
            iconCell.innerHTML = `<i data-lucide="${isFile ? 'file-up' : 'users'}"></i>`;
            descriptionCell.textContent = `Processamento em Lote ${isFile ? '(Arquivo)' : '(Manual)'}`;
            detailsCell.textContent = `${resultData.summary.total_processed} registros processados (${resultData.summary.success_count} sucesso, ${resultData.summary.error_count} erros).`;
        }

        dateCell.textContent = formattedDate;
        lucide.createIcons();

        // Limita a 5 atividades
        while (recentActivityTableBody.rows.length > 5) {
            recentActivityTableBody.deleteRow(recentActivityTableBody.rows.length - 1);
        }
    }


    // Inicialização da página
    function initializeApp() {
        // Define a data de avaliação padrão para hoje
        const today = new Date().toISOString().split('T')[0];
        if (document.getElementById('data_avaliacao')) {
            document.getElementById('data_avaliacao').value = today;
        }

        // Mostra o dashboard por padrão
        showPage('dashboard');
        document.querySelector('.nav-link[data-section="dashboard"]')?.classList.add('active');

        // Esconde elementos que só devem aparecer após uma ação
        if (peopleListContainer) peopleListContainer.style.display = 'none';
        if (resultsDisplay) resultsDisplay.style.display = 'none';
        if (loadingProcess) loadingProcess.style.display = 'none';
        if (errorMessage) errorMessage.style.display = 'none';
        hideFileInfo();
    }

    initializeApp();
});
