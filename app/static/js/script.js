document.addEventListener('DOMContentLoaded', () => {
    const individualForm = document.getElementById('individualForm');
    const batchForm = document.getElementById('batchForm');
    const loadingDiv = document.getElementById('loading');
    const errorMessageDiv = document.getElementById('error-message');
    const individualResultDisplay = document.getElementById('individual-result-display');
    const individualJsonResult = document.getElementById('individual-json-result');
    const individualReportDiv = document.getElementById('individual-report');
    const batchResultDisplay = document.getElementById('batch-result-display');
    const batchSummaryDiv = document.getElementById('batch-summary');
    const batchDetailsDiv = document.getElementById('batch-details');

    document.getElementById('currentYear').textContent = new Date().getFullYear();

    // Seta a data de avaliação para hoje por padrão
    const today = new Date().toISOString().split('T')[0];
    const dataAvaliacaoInput = document.getElementById('data_avaliacao');
    if (dataAvaliacaoInput) {
        dataAvaliacaoInput.value = today;
    }


    function displayLoading(show) {
        loadingDiv.style.display = show ? 'block' : 'none';
    }

    function displayError(message) {
        errorMessageDiv.textContent = message;
        errorMessageDiv.style.display = message ? 'block' : 'none';
    }

    function clearResults() {
        individualResultDisplay.style.display = 'none';
        individualJsonResult.textContent = '';
        individualReportDiv.innerHTML = '';
        batchResultDisplay.style.display = 'none';
        batchSummaryDiv.innerHTML = '';
        batchDetailsDiv.innerHTML = '';
        displayError('');
    }

    function formatResultAsHtml(result) {
        let html = `<div class="result-card">`;
        if (result.dados_entrada.nome) {
            html += `<h4>${result.dados_entrada.nome}</h4>`;
        }
        html += `<p><strong>Data Nasc.:</strong> ${result.dados_entrada.data_nascimento}</p>`;
        html += `<p><strong>Data Aval.:</strong> ${result.dados_entrada.data_avaliacao}</p>`;
        html += `<p><strong>Sexo:</strong> ${result.dados_entrada.sexo === 'M' ? 'Masculino' : 'Feminino'}</p>`;
        html += `<p><strong>Peso:</strong> ${result.dados_entrada.peso_kg} kg</p>`;
        html += `<p><strong>Altura:</strong> ${result.dados_entrada.altura_cm} cm</p>`;
        html += `<p><strong>Idade Calculada:</strong> ${result.idade_calculada_str}</p>`;
        if (result.imc_calculado !== null && result.imc_calculado !== undefined) {
            html += `<p><strong>IMC:</strong> ${result.imc_calculado.toFixed(2)}</p>`;
        }

        if (result.indicadores && result.indicadores.length > 0) {
            html += `<h5>Indicadores:</h5>`;
            result.indicadores.forEach(ind => {
                html += `<div class="indicador ${ind.destaque ? 'destaque' : ''}">`;
                html += `<p><strong>${ind.tipo}:</strong> `;
                if (ind.valor_medido !== null && ind.valor_medido !== undefined) {
                     html += `Valor: ${typeof ind.valor_medido === 'number' ? ind.valor_medido.toFixed(2) : ind.valor_medido}, `;
                }
                if (ind.escore_z !== null && ind.escore_z !== undefined) {
                    html += `Escore-Z: ${ind.escore_z.toFixed(2)}, `;
                }
                html += `<span class="classificacao">Classificação: ${ind.classificacao || 'N/A'}</span></p>`;
                html += `</div>`;
            });
        }
        html += `</div>`;
        return html;
    }


    if (individualForm) {
        individualForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            clearResults();
            displayLoading(true);

            const formData = new FormData(individualForm);
            const data = {
                nome: formData.get('nome') || null, // Enviar null se vazio
                data_nascimento: formData.get('data_nascimento'),
                data_avaliacao: formData.get('data_avaliacao'),
                sexo: formData.get('sexo'),
                peso_kg: parseFloat(formData.get('peso_kg')),
                altura_cm: parseFloat(formData.get('altura_cm')),
            };

            try {
                const response = await fetch('/api/processar/individual', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data),
                });

                displayLoading(false);

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || `Erro ${response.status}`);
                }

                const result = await response.json();
                individualJsonResult.textContent = JSON.stringify(result, null, 2);
                individualReportDiv.innerHTML = formatResultAsHtml(result);
                individualResultDisplay.style.display = 'block';

            } catch (error) {
                displayLoading(false);
                displayError(`Erro ao processar: ${error.message}`);
                console.error('Erro:', error);
            }
        });
    }

    if (batchForm) {
        batchForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            clearResults();
            displayLoading(true);

            const formData = new FormData(batchForm);
            const fileInput = document.getElementById('batchFile');

            if (!fileInput.files.length) {
                displayLoading(false);
                displayError('Nenhum arquivo selecionado.');
                return;
            }

            try {
                const response = await fetch('/api/processar/lote', {
                    method: 'POST',
                    body: formData, // Enviar FormData diretamente para upload de arquivo
                });

                displayLoading(false);

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || `Erro ${response.status}`);
                }

                const results = await response.json(); // Espera-se uma lista de resultados
                
                batchSummaryDiv.innerHTML = `<p>Total de registros processados: ${results.length}</p>`;
                // Adicionar mais estatísticas se o backend retornar um objeto ResultadoProcessamentoLote
                // if (results.nome_arquivo) {
                //    batchSummaryDiv.innerHTML = `<p>Arquivo: ${results.nome_arquivo}</p>
                //                                 <p>Total processados: ${results.total_processados}</p>
                //                                 <p>Total com erros: ${results.total_com_erros}</p>`;
                //    results.resultados_individuais.forEach(result => {
                //        batchDetailsDiv.innerHTML += formatResultAsHtml(result);
                //    });
                // } else { // Se for uma lista direta
                    results.forEach(result => {
                        batchDetailsDiv.innerHTML += formatResultAsHtml(result);
                    });
                // }


                batchResultDisplay.style.display = 'block';

            } catch (error) {
                displayLoading(false);
                displayError(`Erro ao processar lote: ${error.message}`);
                console.error('Erro:', error);
            }
        });
    }
});