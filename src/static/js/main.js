// Aguarda o documento HTML ser completamente carregado
document.addEventListener('DOMContentLoaded', function() {

    // Encontra os elementos do formulário do modal
    const pacienteSearchInput = document.getElementById('pacienteSearch');
    const searchResultsDiv = document.getElementById('searchResults');
    const pacienteIdInput = document.getElementById('pacienteId');
  
    // Função para buscar pacientes na API
    async function searchPacientes(query) {
      if (query.length < 2) {
        searchResultsDiv.innerHTML = ''; // Limpa os resultados se a busca for muito curta
        return;
      }
  
      try {
        const response = await fetch(`/pacientes/search?q=${query}`);
        const pacientes = await response.json();
  
        // Limpa os resultados anteriores
        searchResultsDiv.innerHTML = '';
  
        // Cria e adiciona os novos resultados na div
        pacientes.forEach(paciente => {
          const a = document.createElement('a');
          a.href = '#';
          a.classList.add('list-group-item', 'list-group-item-action');
          a.textContent = `${paciente.nome} (CPF: ${paciente.cpf || 'N/A'})`;
          
          // Evento de clique para selecionar o paciente
          a.addEventListener('click', function(e) {
            e.preventDefault();
            pacienteSearchInput.value = paciente.nome; // Preenche o input com o nome
            pacienteIdInput.value = paciente.id;      // Guarda o ID no input escondido
            searchResultsDiv.innerHTML = '';           // Esconde a lista de resultados
          });
  
          searchResultsDiv.appendChild(a);
        });
  
      } catch (error) {
        console.error('Erro ao buscar pacientes:', error);
      }
    }
  
    // Adiciona o "ouvinte" de eventos no campo de busca
    pacienteSearchInput.addEventListener('input', () => {
      searchPacientes(pacienteSearchInput.value);
    });
  
  });