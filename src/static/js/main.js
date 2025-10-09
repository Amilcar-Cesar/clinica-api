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
  
    // LÓGICA PARA O MODAL DE EDIÇÃO DE PACIENTES
    const editPacienteModal = document.getElementById('editPacienteModal');
    if (editPacienteModal) {
      editPacienteModal.addEventListener('show.bs.modal', function (event) {
          const button = event.relatedTarget; // O botão que acionou o modal

          // Extrai os dados dos atributos data-* do botão
          const id = button.getAttribute('data-id');
          const nome = button.getAttribute('data-nome');
          const nascimento = button.getAttribute('data-nascimento');
          const cpf = button.getAttribute('data-cpf');
          const sus = button.getAttribute('data-sus');
          const endereco = button.getAttribute('data-endereco');

          // Encontra o formulário e os inputs do modal
          const form = document.getElementById('editPacienteForm');
          const idInput = document.getElementById('editPacienteId');
          const nomeInput = document.getElementById('editNome');
          const nascimentoInput = document.getElementById('editDataNascimento');
          const cpfInput = document.getElementById('editCpf');
          const susInput = document.getElementById('editCartaoSus');
          const enderecoInput = document.getElementById('editEndereco');

          // Atualiza a action do formulário para o URL de update correto
          form.action = `/pacientes/${id}/update`;

          // Preenche os campos do formulário com os dados do paciente
          idInput.value = id;
          nomeInput.value = nome;
          nascimentoInput.value = nascimento;
          cpfInput.value = cpf;
          susInput.value = sus;
          enderecoInput.value = endereco;
      });
    }

});