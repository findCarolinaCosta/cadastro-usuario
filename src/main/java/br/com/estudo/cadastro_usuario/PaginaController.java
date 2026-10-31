package br.com.estudo.cadastro_usuario;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class PaginaController {
    @GetMapping("/")
    public String inicio() {
        return "inicio";
    }

    @GetMapping({"/endereco", "/cadastro", "/cadastro-validado"})
    public String formulario(jakarta.servlet.http.HttpServletRequest request, Model model) {
        String pagina = request.getServletPath();
        model.addAttribute("somenteEndereco", pagina.equals("/endereco"));
        model.addAttribute("validar", pagina.equals("/cadastro-validado"));
        model.addAttribute("titulo", pagina.equals("/endereco") ? "Consulta de endereço" : "Formulário de Cadastro");
        return "formulario";
    }
}
