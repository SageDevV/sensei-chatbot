let chat = document.querySelector('#chat');
let input = document.querySelector('#input');
let botaoEnviar = document.querySelector('#botao-enviar');
let imagemSelecionada;
let botaoAnexo = document.querySelector('#mais_arquivo');
let miniaturaImagem;

async function pegarImagem() {
    let fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = 'image/*, text/plain';

    fileInput.onchange = async e => {
        if (miniaturaImagem) {
            miniaturaImagem.remove(); 
        }

        arquivoSelecionado = e.target.files[0];

        let extensaoArquivo = arquivoSelecionado.name.split('.').pop().toLowerCase();

        if(extensaoArquivo !== 'txt'){
            miniaturaImagem = document.createElement('img');
            miniaturaImagem.src = URL.createObjectURL(arquivoSelecionado);
            miniaturaImagem.style.maxWidth = '3rem'; 
            miniaturaImagem.style.maxHeight = '3rem';
            miniaturaImagem.style.margin = '0.5rem'; 

            document.querySelector('.entrada__container').insertBefore(miniaturaImagem, input);

            let formData = new FormData();
            formData.append('imagem', arquivoSelecionado);

            const response = await fetch('http://127.0.0.1:5000/upload_arquivo', {
                method: 'POST',
                body: formData
            });

            const resposta = await response.text();
            console.log(resposta);
            console.log(imagemSelecionada);
        }
        else{
            miniaturaImagem = document.createElement('img');
            miniaturaImagem.src = "../static/img/txt.png";
            miniaturaImagem.style.maxWidth = '3rem'; 
            miniaturaImagem.style.maxHeight = '3rem';
            miniaturaImagem.style.margin = '0.5rem'; 

            document.querySelector('.entrada__container').insertBefore(miniaturaImagem, input);

            let formData = new FormData();
            formData.append('arquivo', arquivoSelecionado);

            const response = await fetch('http://127.0.0.1:5000/upload_arquivo', {
                method: 'POST',
                body: formData
            });

            const resposta = await response.text();
            console.log(resposta);
            console.log(arquivoSelecionado);
        }
    }
    fileInput.click();
}

async function enviarMensagem() {
    if(input.value == "" || input.value == null) return;
    let mensagem = input.value;
    input.value = "";

    if (miniaturaImagem) {
        miniaturaImagem.remove(); 
    }

    let novaBolha = criaBolhaUsuario();
    novaBolha.innerHTML = mensagem;
    chat.appendChild(novaBolha);

    let novaBolhaBot = criaBolhaBot();
    chat.appendChild(novaBolhaBot);
    vaiParaFinalDoChat();
    novaBolhaBot.innerHTML = "Analisando ..."
    
    const resposta = await fetch("http://127.0.0.1:5000/chat", {
        method: "POST",
        headers: {
        "Content-Type": "application/json",
        },
        body: JSON.stringify({'msg':mensagem}),
    });
    const textoDaResposta = await resposta.text();
    console.log(textoDaResposta);
    novaBolhaBot.innerHTML = textoDaResposta.replace(/\n/g, '<br>');
    vaiParaFinalDoChat();
}

function criaBolhaUsuario() {
    let bolha = document.createElement('p');
    bolha.classList = 'chat__bolha chat__bolha--usuario';
    return bolha;
}

function criaBolhaBot() {
    let bolha = document.createElement('p');
    bolha.classList = 'chat__bolha chat__bolha--bot';
    return bolha;
}

function vaiParaFinalDoChat() {
    chat.scrollTop = chat.scrollHeight;
}

botaoEnviar.addEventListener('click', enviarMensagem);
input.addEventListener("keyup", function(event) {
    event.preventDefault();
    if (event.keyCode === 13) {
        botaoEnviar.click();
    }
});

botaoAnexo.addEventListener('click', pegarImagem);