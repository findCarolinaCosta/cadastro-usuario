/* Validação da atividade 4: jQuery, independente da consulta ao ViaCEP. */
$(function () {
    'use strict';
    const form = $('#cadastro-form');
    const email = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    function validar(campo) {
        const valor = campo.value.trim();
        let mensagem = '';
        if (campo.required && !valor) mensagem = 'Preencha este campo.';
        else if (campo.id === 'email' && !email.test(valor)) mensagem = 'Informe um e-mail válido, como nome@dominio.com.';
        else if (campo.id === 'cep' && !/^\d{5}-?\d{3}$/.test(valor)) mensagem = 'O CEP deve conter 8 dígitos.';
        else if (campo.id === 'senha' && campo.value.length < 8) mensagem = 'Use pelo menos 8 caracteres.';
        else if (campo.id === 'confirmacao' && campo.value !== $('#senha').val()) mensagem = 'As senhas devem ser iguais.';
        $(campo).attr('aria-invalid', mensagem ? 'true' : 'false');
        $('#' + campo.id + '-erro').text(mensagem);
        return !mensagem;
    }

    form.on('submit', function (event) {
        event.preventDefault();
        let primeiroErro;
        form.find('input, select').each(function () {
            if (!validar(this) && !primeiroErro) primeiroErro = this;
        });
        $('#resultado').prop('hidden', false).text(primeiroErro
            ? 'Revise os campos destacados antes de continuar.'
            : 'Cadastro validado com sucesso! Esta demonstração não armazena nem envia seus dados.');
        primeiroErro?.focus();
    });
    form.on('input change', 'input, select', function () {
        $('#resultado').prop('hidden', true);
        if ($(this).attr('aria-invalid') !== undefined) validar(this);
        if (this.id === 'senha' && $('#confirmacao').attr('aria-invalid') !== undefined) validar($('#confirmacao')[0]);
    });
});
