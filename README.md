# antropomorph
Após clonar o repositório, mude para a pasta onde ele está:

$ cd antropomorph

Para rodar localmente você deve criar o ambiente virtual - na pasta ambiente:

$ python -m venv ambiente

Tendo instalado o ambiente, ative-o com:

[paiva@pnote2 antropomorph]$ source ambiente/bin/activate
(ambiente) [paiva@pnote2 antropomorph]$ 

No ambiente, instale os pacotes requeridos:

(ambiente) [paiva@pnote2 antropomorph]$ pip install -r requirements.txt
...

Execute a aplicação:
(ambiente) [paiva@pnote2 antropomorph]$ uvicorn main:app --reload
 

