document.addEventListener('DOMContentLoaded', function() {
    lucide.createIcons();

    let lastBatchResults = null;

    // Elementos da UI
    const navLinks = document.querySelectorAll('.sidebar-nav .nav-link, .sidebar-footer .nav-link');
    const pageSections = document.querySelectorAll('.page-section');
    const pageTitle = document.getElementById('page-title');    const mobileMenuOverlay = document.getElementById('mobile-menu-overlay');
    const menuToggle = document.getElementById('menu-toggle');
    const closeMenu = document.getElementById('close-menu');

    // Formulários e elementos de resultado
    const individualForm = document.getElementById('individualForm');
    const batchForm = document.getElementById('batchForm');
    const batchFileInput = document.getElementById('batchFile');
    const fileInfoDisplay = document.getElementById('file-info-display');
    const batchActionsDiv = document.getElementById('batch-actions');
    
    // Pegando os novos inputs do formulário de lote
    const reportIdentifierInput = document.getElementById('reportIdentifier');
    const reportSubIdentifierInput = document.getElementById('reportSubIdentifier');

    const loadingIndividual = document.getElementById('loading-individual');
    const errorMessageIndividual = document.getElementById('error-message-individual');
    const individualResultDisplay = document.getElementById('individual-result-display');
    const individualJsonResult = document.querySelector('#individual-result-display code');
    const individualTableBody = document.getElementById('individual-table-body');

    const loadingBatch = document.getElementById('loading-batch');
    const errorMessageBatch = document.getElementById('error-message-batch');
    const batchResultDisplay = document.getElementById('batch-result-display');
    const batchSummaryDiv = document.getElementById('batch-summary');
    const batchTableBody = document.getElementById('batch-table-body');
    const batchErrorsDisplay = document.getElementById('batch-errors-display');
    const batchErrorList = document.getElementById('batch-error-list');

    const recentActivityTableBody = document.querySelector('#recent-activity-table tbody');

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
        clearAllResultsAndErrors();
    }

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

    if (menuToggle) menuToggle.addEventListener('click', () => mobileMenuOverlay.style.display = 'block');
    if (closeMenu) closeMenu.addEventListener('click', () => mobileMenuOverlay.style.display = 'none');
    if (mobileMenuOverlay) mobileMenuOverlay.addEventListener('click', (e) => {
        if (e.target === mobileMenuOverlay) mobileMenuOverlay.style.display = 'none';
    });

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

    if (document.getElementById('currentYear')) document.getElementById('currentYear').textContent = new Date().getFullYear();
    const today = new Date().toISOString().split('T')[0];
    const dataAvaliacaoInput = document.getElementById('data_avaliacao');
    if (dataAvaliacaoInput) dataAvaliacaoInput.value = today;

    function displayLoading(section, show) {
        const loader = section === 'individual' ? loadingIndividual : loadingBatch;
        if (loader) loader.style.display = show ? 'flex' : 'none';
    }

    function displayError(section, message) {
        const errorDiv = section === 'individual' ? errorMessageIndividual : errorMessageBatch;
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.style.display = message ? 'block' : 'none';
        }
    }

    function clearIndividualResults() {
        if (individualResultDisplay) individualResultDisplay.style.display = 'none';
        if (individualJsonResult) individualJsonResult.textContent = '';
        if (individualTableBody) individualTableBody.innerHTML = '';
        displayError('individual', '');
    }

    function clearBatchResults() {
        if (batchResultDisplay) batchResultDisplay.style.display = 'none';
        if (batchSummaryDiv) batchSummaryDiv.innerHTML = '';
        if (batchTableBody) batchTableBody.innerHTML = '';
        if (batchErrorList) batchErrorList.innerHTML = '';
        if (batchErrorsDisplay) batchErrorsDisplay.style.display = 'none';
        if (batchActionsDiv) batchActionsDiv.innerHTML = '';
        displayError('batch', '');
    }

    function clearAllResultsAndErrors() {
        clearIndividualResults();
        clearBatchResults();
    }

    function getClassificationForIndicator(indicadores, tipoIndicador) {
        if (!indicadores || !Array.isArray(indicadores)) return 'N/A';
        const indicador = indicadores.find(ind => ind.tipo.startsWith(tipoIndicador));
        return indicador ? (indicador.classificacao || 'N/A') : 'N/A';
    }

    function createBadgeCell(classificationText) {
        const cell = document.createElement('td');
        const badge = document.createElement('span');
        badge.className = `table-status-badge ${getNutritionalStatusClass(classificationText)}`;
        badge.textContent = classificationText;
        cell.appendChild(badge);
        return cell;
    }    function populateSuccessRow(result, tableBodyElement) {
        const row = tableBodyElement.insertRow();
        row.insertCell().textContent = result.nome || 'N/A';
        row.insertCell().textContent = result.idade || 'N/A';
        row.insertCell().textContent = formatDateToBrazilian(result.data_nascimento);
        row.insertCell().textContent = formatDateToBrazilian(result.data_avaliacao);
        row.insertCell().textContent = parseFloat(result.peso_kg).toFixed(1);
        row.appendChild(createBadgeCell(getClassificationForIndicator(result.indicadores, 'Peso-para-Idade')));
        row.insertCell().textContent = parseFloat(result.altura_cm).toFixed(1);
        row.appendChild(createBadgeCell(getClassificationForIndicator(result.indicadores, 'Altura-para-Idade')));
        row.insertCell().textContent = result.imc?.toFixed(2) ?? 'N/A';
        const imcIClassification = getClassificationForIndicator(result.indicadores, 'IMC-para-Idade');
        row.appendChild(createBadgeCell(imcIClassification));

        updateDashboardAndRecentActivity(result, imcIClassification);
    }    function populateErrorRow(errorItem, tableBodyElement) {
        const row = tableBodyElement.insertRow();
        row.classList.add('row-error');
        const originalData = errorItem.dados_originais || {};
        row.insertCell().textContent = originalData.nome || 'N/A';
        row.insertCell().textContent = '---';
        row.insertCell().textContent = originalData.data_nascimento || 'N/A';
        row.insertCell().textContent = originalData.data_avaliacao || 'N/A';
        row.insertCell().textContent = originalData.peso_kg || 'N/A';
        
        const pesoStatusCell = row.insertCell();
        const pesoStatusBadge = document.createElement('span');
        pesoStatusBadge.className = 'table-status-badge bg-red-100 text-red-700';
        pesoStatusBadge.textContent = 'Erro';
        pesoStatusBadge.title = errorItem.erro;
        pesoStatusCell.appendChild(pesoStatusBadge);
        
        row.insertCell().textContent = originalData.altura_cm || 'N/A';
        
        const alturaStatusCell = row.insertCell();
        const alturaStatusBadge = document.createElement('span');
        alturaStatusBadge.className = 'table-status-badge bg-red-100 text-red-700';
        alturaStatusBadge.textContent = 'Erro';
        alturaStatusBadge.title = errorItem.erro;
        alturaStatusCell.appendChild(alturaStatusBadge);
        
        row.insertCell().textContent = '---';
        
        const imcStatusCell = row.insertCell();
        const imcStatusBadge = document.createElement('span');
        imcStatusBadge.className = 'table-status-badge bg-red-100 text-red-700';
        imcStatusBadge.textContent = 'Erro';
        imcStatusBadge.title = errorItem.erro;
        imcStatusCell.appendChild(imcStatusBadge);
    }

    function getNutritionalStatusPdfColor(classificationText) {
        if (!classificationText) return null;
        const lowerClass = classificationText.toLowerCase();

        if (lowerClass.includes('magreza acentuada') || lowerClass.includes('muito baixo peso') || lowerClass.includes('obesidade grave')) return [254, 226, 226]; // Vermelho
        if (lowerClass.includes('magreza') || lowerClass.includes('baixo peso') || lowerClass.includes('baixa estatura') || lowerClass.includes('obesidade')) return [254, 242, 242]; // Rosa
        if (lowerClass.includes('eutrofia') || lowerClass.includes('peso adequado') || lowerClass.includes('estatura adequada')) return [236, 253, 245]; // Verde
        if (lowerClass.includes('risco de sobrepeso') || lowerClass.includes('sobrepeso')) return [254, 252, 232]; // Amarelo
        if (lowerClass === 'erro') return [254, 226, 226]; // Vermelho

        return null;
    }
    
    function exportBatchResultsToPdf(identifier, subIdentifier) {
        if (!lastBatchResults) {
            console.error("Não há dados de lote para exportar.");
            return;
        }

        const { jsPDF } = window.jspdf;
        const doc = new jsPDF({ orientation: 'landscape' });
        
        doc.setFontSize(18);
        doc.text(identifier, 14, 20);
        
        let startY = 30;
        if (subIdentifier) {
            doc.setFontSize(12);
            doc.text(subIdentifier, 14, startY);
            startY += 8;
        }

        doc.setFontSize(10);
        doc.text(`Arquivo: ${lastBatchResults.nome_arquivo}`, 14, startY);
        doc.text(`Total de Registros: ${lastBatchResults.total_registros_no_arquivo}`, 14, startY + 5);
        doc.text(`Sucessos: ${lastBatchResults.total_processados_com_sucesso}`, 14, startY + 10);
        doc.text(`Erros: ${lastBatchResults.total_com_erros}`, 14, startY + 15);
          const head = [['Nome', 'Idade', 'Data Nasc.', 'Data Aval.', 'Peso(kg)', 'P/I', 'Altura(cm)', 'A/I', 'IMC', 'IMC/I']];
        const body = [];

        if (Array.isArray(lastBatchResults.resultados_individuais)) {            lastBatchResults.resultados_individuais.forEach(res => {
                body.push([
                    res.dados_entrada.nome || 'N/A',
                    res.idade_calculada_str || 'N/A',
                    formatDateToBrazilian(res.dados_entrada.data_nascimento),
                    formatDateToBrazilian(res.dados_entrada.data_avaliacao),
                    res.dados_entrada.peso_kg.toFixed(1),
                    getClassificationForIndicator(res.indicadores, 'Peso-para-Idade'),
                    res.dados_entrada.altura_cm.toFixed(1),
                    getClassificationForIndicator(res.indicadores, 'Altura-para-Idade'),
                    res.imc_calculado?.toFixed(2) ?? 'N/A',
                    getClassificationForIndicador(res.indicadores, 'IMC-para-Idade')
                ]);
            });
        }

        if (Array.isArray(lastBatchResults.erros_por_linha)) {            lastBatchResults.erros_por_linha.forEach(err => {
                const d = err.dados_originais || {};
                body.push([
                    d.nome || 'N/A',
                    '---',
                    d.data_nascimento || 'N/A',
                    d.data_avaliacao || 'N/A',
                    d.peso_kg || 'N/A',
                    'Erro',
                    d.altura_cm || 'N/A',
                    'Erro',
                    '---',
                    'Erro'
                ]);
            });
        }
        
        doc.autoTable({
            head: head, body: body, startY: startY + 22, theme: 'grid',
            headStyles: { fillColor: [22, 78, 99] }, // Azul escuro
            styles: { fontSize: 8, cellPadding: 2 },            didParseCell: function (data) {
                const imcStatus = data.row.raw[9]; // IMC/I está na coluna 9 agora
                let color = getNutritionalStatusPdfColor(imcStatus);

                if (color) {
                    data.cell.styles.fillColor = color;
                }
            }
        });
        
        const pageCount = doc.internal.getNumberOfPages();
        for (let i = 1; i <= pageCount; i++) {
            doc.setPage(i);
            doc.setFontSize(8);
            doc.text(`Página ${i} de ${pageCount}`, doc.internal.pageSize.width - 25, doc.internal.pageSize.height - 10);
            doc.text(`Gerado em: ${new Date().toLocaleDateString('pt-BR')} ${new Date().toLocaleTimeString('pt-BR')}`, 14, doc.internal.pageSize.height - 10);
        }

        doc.save(`Relatorio_${identifier.replace(/ /g, "_")}.pdf`);
    }

    if (individualForm) {
        individualForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            clearIndividualResults();
            displayLoading('individual', true);

            const formData = new FormData(individualForm);
            const data = {
                nome: formData.get('nome') || null,
                data_nascimento: formData.get('data_nascimento'),
                data_avaliacao: formData.get('data_avaliacao'),
                sexo: formData.get('sexo'),
                peso_kg: parseFloat(formData.get('peso_kg')),
                altura_cm: parseFloat(formData.get('altura_cm')),
            };

            try {
                const response = await fetch('/api/processar/individual', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data),
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || `Erro ${response.status}`);
                }

                const result = await response.json();
                if (individualJsonResult) individualJsonResult.textContent = JSON.stringify(result, null, 2);
                if (individualTableBody) {
                    individualTableBody.innerHTML = '';
                    populateSuccessRow(result, individualTableBody);
                }
                if (individualResultDisplay) individualResultDisplay.style.display = 'block';

            } catch (error) {
                displayError('individual', `Erro ao processar: ${error.message}`);
            } finally {
                displayLoading('individual', false);
            }
        });

        document.getElementById('clearIndividualForm')?.addEventListener('click', () => {
            individualForm.reset();
            if (dataAvaliacaoInput) dataAvaliacaoInput.value = today;
            clearIndividualResults();
        });
    }

    if (batchFileInput && fileInfoDisplay) {
        batchFileInput.addEventListener('change', () => {
            if (batchFileInput.files.length > 0) {
                const file = batchFileInput.files[0];
                const fileSize = (file.size / 1024).toFixed(2);
                fileInfoDisplay.innerHTML = `
                    <div class="flex items-center space-x-2 p-2 bg-slate-100 rounded-md border border-slate-200 text-sm text-slate-700">
                        <i data-lucide="file-text" class="h-5 w-5 text-slate-500"></i>
                        <span>Arquivo: <strong>${file.name}</strong> (${fileSize} KB)</span>
                    </div>`;
                lucide.createIcons();
            } else {
                fileInfoDisplay.innerHTML = '';
            }
        });
    }

    if (batchForm) {
        batchForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            clearBatchResults();
            lastBatchResults = null;

            if (!batchFileInput || !batchFileInput.files || !batchFileInput.files.length) {
                displayError('batch', 'Nenhum arquivo selecionado.');
                return;
            }

            displayLoading('batch', true);
            const formData = new FormData(batchForm);

            try {
                const response = await fetch('/api/processar/lote', { method: 'POST', body: formData });
                if (!response.ok) { throw new Error((await response.json()).detail || `Erro ${response.status}`); }

                const resultsData = await response.json();
                lastBatchResults = resultsData;

                if (batchTableBody) batchTableBody.innerHTML = '';
                if (batchErrorList) batchErrorList.innerHTML = '';
                
                if (Array.isArray(resultsData.resultados_individuais)) { resultsData.resultados_individuais.forEach(result => { populateSuccessRow(result, batchTableBody); }); }
                if (Array.isArray(resultsData.erros_por_linha)) { resultsData.erros_por_linha.forEach(errorItem => { populateErrorRow(errorItem, batchTableBody); const li = document.createElement('li'); li.textContent = `Linha ${errorItem.linha}: ${errorItem.erro}`; batchErrorList.appendChild(li); }); }

                if (batchSummaryDiv) {
                     batchSummaryDiv.innerHTML = `<p>Arquivo: <strong>${resultsData.nome_arquivo}</strong></p>
                                               <p>Registros no arquivo: <strong>${resultsData.total_registros_no_arquivo}</strong></p>
                                               <p class="text-emerald-700">Processados com sucesso: <strong>${resultsData.total_processados_com_sucesso}</strong></p>
                                               <p class="text-rose-700">Registros com erro: <strong>${resultsData.total_com_erros}</strong></p>`;
                }

                if (batchActionsDiv) {
                    batchActionsDiv.innerHTML = '';
                    const pdfButton = document.createElement('button');
                    pdfButton.className = 'btn btn-primary';
                    pdfButton.innerHTML = '<i data-lucide="download"></i> <span>Baixar Relatório em PDF</span>';
                    
                    pdfButton.onclick = () => {
                        const identifier = reportIdentifierInput.value;
                        const subIdentifier = reportSubIdentifierInput.value;
                        if (!identifier) {
                            alert('Por favor, preencha o nome da Escola / Comunidade para gerar o relatório.');
                            reportIdentifierInput.focus();
                            return;
                        }
                        exportBatchResultsToPdf(identifier, subIdentifier);
                    };

                    batchActionsDiv.appendChild(pdfButton);
                    lucide.createIcons();
                }

                if (resultsData.total_com_erros > 0 && batchErrorsDisplay) batchErrorsDisplay.style.display = 'block';
                if (batchResultDisplay) batchResultDisplay.style.display = 'block';

            } catch (error) {
                displayError('batch', `Erro ao processar lote: ${error.message}`);
            } finally {
                displayLoading('batch', false);
                if (batchFileInput) batchFileInput.value = '';
                if (fileInfoDisplay) fileInfoDisplay.innerHTML = '';
            }
        });
    }

    let totalAvaliacoes = 0, totalAlertas = 0, totalEutroficos = 0, totalDesvios = 0;
    const maxRecentActivities = 5;
    let recentActivities = [];

    function updateDashboardStats() {
        if(document.getElementById('stat-avaliacoes')) document.getElementById('stat-avaliacoes').textContent = totalAvaliacoes;
        if(document.getElementById('stat-alertas')) document.getElementById('stat-alertas').textContent = totalAlertas;
        if(document.getElementById('stat-eutroficos')) document.getElementById('stat-eutroficos').textContent = totalEutroficos;
        if(document.getElementById('stat-desvios')) document.getElementById('stat-desvios').textContent = totalDesvios;
    }    function updateRecentActivityTable() {
        if (!recentActivityTableBody) return;
        recentActivityTableBody.innerHTML = ''; 

        if (recentActivities.length === 0) {
            recentActivityTableBody.innerHTML = '<tr><td colspan="10" class="text-center">Nenhuma atividade recente.</td></tr>';
            return;
        }

        recentActivities.forEach(activity => {
            const row = recentActivityTableBody.insertRow();
            row.insertCell().textContent = activity.nome;
            row.insertCell().textContent = activity.idade;
            row.insertCell().textContent = activity.dataNascimento;
            row.insertCell().textContent = activity.dataAvaliacao;
            row.insertCell().textContent = activity.peso;
            row.appendChild(createBadgeCell(activity.statusPesoI));
            row.insertCell().textContent = activity.altura;
            row.appendChild(createBadgeCell(activity.statusAlturaI));
            row.insertCell().textContent = activity.imc;
            row.appendChild(createBadgeCell(activity.statusImcI));        });
    }

    function updateDashboardAndRecentActivity(result, imcIClassification) {
        totalAvaliacoes++;
        const lowerImcI = imcIClassification.toLowerCase();

        if (lowerImcI.includes('eutrofia') || lowerImcI.includes('adequado')) {
            totalEutroficos++;
        } else if (lowerImcI !== 'n/a') {
            totalAlertas++;
            totalDesvios++;
        }        recentActivities.unshift({
            nome: result.nome || 'N/A',
            idade: result.idade || 'N/A',
            dataNascimento: formatDateToBrazilian(result.data_nascimento),
            dataAvaliacao: formatDateToBrazilian(result.data_avaliacao),
            peso: `${parseFloat(result.peso_kg).toFixed(1)}`,
            altura: `${parseFloat(result.altura_cm).toFixed(1)}`,
            imc: result.imc?.toFixed(2) ?? 'N/A',
            statusPesoI: getClassificationForIndicator(result.indicadores, 'Peso-para-Idade'),
            statusAlturaI: getClassificationForIndicator(result.indicadores, 'Altura-para-Idade'),
            statusImcI: imcIClassification
        });
        if (recentActivities.length > maxRecentActivities) {
            recentActivities.pop();
        }

        updateDashboardStats();
        updateRecentActivityTable();
    }
    
    // Gráfico de Exemplo
    const ctx = document.getElementById('imcChart');
    if (ctx) {
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Eutrofia', 'Risco de Sobrepeso', 'Sobrepeso', 'Obesidade', 'Magreza', 'Magreza Acentuada'],
                datasets: [{
                    label: 'Distribuição do Estado Nutricional',
                    data: [12, 19, 3, 5, 2, 3],
                    backgroundColor: [
                        '#10B981', '#F59E0B', '#EF4444', '#DC2626', '#FBBF24', '#F87171'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: false
                    }
                }
            }
        });
    }


    const initialSection = 'dashboard';
    showPage(initialSection);
    const initialLink = document.querySelector(`.nav-link[data-section="${initialSection}"]`);
    if (initialLink) {
        navLinks.forEach(l => l.classList.remove('active'));
        document.querySelectorAll(`.nav-link[data-section="${initialSection}"]`).forEach(activeLink => activeLink.classList.add('active'));
        if(pageTitle) pageTitle.textContent = initialLink.textContent.trim();
    }
    updateDashboardStats();
    updateRecentActivityTable();
});