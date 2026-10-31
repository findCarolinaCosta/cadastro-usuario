(() => {
    'use strict';
    const form = document.querySelector('#cadastro-form');
    const cep = document.querySelector('#cep');
    const button = document.querySelector('#buscar-cep');
    const status = document.querySelector('#cep-status');
    const resultado = document.querySelector('#resultado');
    const campos = ['rua', 'bairro', 'cidade', 'estado'];
    let consulta;
    let versao = 0;
    const limparEndereco = () => campos.forEach(id => { document.getElementById(id).value = ''; });
    const cancelar = () => { versao++; consulta?.abort(); button.disabled = false; };

    async function buscar() {
        cancelar();
        const atual = versao;
        const codigo = cep.value.replace(/\D/g, '');
        limparEndereco();
        if (!/^\d{8}$/.test(codigo)) {
            status.textContent = 'Informe um CEP com 8 dígitos.';
            cep.setAttribute('aria-invalid', 'true');
            return;
        }
        cep.removeAttribute('aria-invalid');
        const controller = new AbortController();
        consulta = controller;
        const timeout = setTimeout(() => controller.abort(), 10000);
        button.disabled = true;
        status.textContent = 'Consultando endereço…';
        try {
            const response = await fetch(`https://viacep.com.br/ws/${codigo}/json/`, { signal: controller.signal });
            if (!response.ok) throw new Error('Falha na consulta');
            const dados = await response.json();
            if (atual !== versao) return;
            if (dados.erro) {
                status.textContent = 'CEP não encontrado. Confira o número informado.';
                return;
            }
            const endereco = { rua: dados.logradouro, bairro: dados.bairro, cidade: dados.localidade, estado: dados.uf };
            campos.forEach(id => {
                const campo = document.getElementById(id);
                campo.value = endereco[id] || '';
                campo.dispatchEvent(new Event('input', { bubbles: true }));
            });
            status.textContent = 'Endereço encontrado. Complete número e complemento; preencha manualmente qualquer informação ausente.';
        } catch (error) {
            if (atual === versao) status.textContent = 'Não foi possível consultar o CEP. Tente novamente ou preencha o endereço manualmente.';
        } finally {
            clearTimeout(timeout);
            if (atual === versao) button.disabled = false;
        }
    }

    button.addEventListener('click', buscar);
    cep.addEventListener('blur', () => { if (cep.value.trim()) buscar(); });
    cep.addEventListener('input', () => {
        cancelar();
        limparEndereco();
        const digits = cep.value.replace(/\D/g, '').slice(0, 8);
        cep.value = digits.length > 5 ? `${digits.slice(0, 5)}-${digits.slice(5)}` : digits;
        status.textContent = 'Informe o CEP e clique em Buscar ou saia do campo.';
    });
    form.addEventListener('reset', () => {
        cancelar();
        status.textContent = 'Informe o CEP e clique em Buscar ou saia do campo.';
        resultado.hidden = true;
        form.querySelectorAll('[aria-invalid]').forEach(campo => campo.removeAttribute('aria-invalid'));
        form.querySelectorAll('.erro').forEach(erro => { erro.textContent = ''; });
    });
    form.addEventListener('submit', event => {
        event.preventDefault();
        if (form.dataset.validar === 'true') return;
        if (!form.reportValidity()) return;
        resultado.textContent = 'Formulário preenchido. Demonstração concluída; nenhum dado foi armazenado ou enviado.';
        resultado.hidden = false;
    });
})();
