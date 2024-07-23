<!-- # DONE: #52 Hora inicio on load e hora fim os save - ok 

# DONE: #47 No final da OS adicionar o digito 01 para campanha de coleta e remover o codigo dew 4 caracteres - ok

# DONE: Passar o ponto para o final da string no model de coleta

# Done: #53 Mudar o status da campanha automaticamente, se tiver iniciada ja vai para os fomrs de coleta

# Programada, Reprogramada, Cancelada, iniciada, finalizada

# DONE: #49 tirar  a variavel de OS da tabela de lista de coletas e colocar no titulo da tabela

# Done: #50 Mudar o ponto no proprio formulario (no card colocar um filtro de navegacao para mudar o ponto) -->

# TODO: #48 Cancelamento  precisa de motivo e precisa guardar o usuario responsavel pelo cancelamento e a data

# Done: #46 Remover  o delete em cascata

# ------------------------


# TODO: Adicionar botóes para exportação dos dados em todas as telas com tabelas

# mudar as cores dos botoes da tabela campanhas

#colocar OS no lugar de local na tela inicial

#colocar link para o checklist na campanha atual

# TODO: #62 Falar com os pesquisadores para estabelecer a faixa de cada parametro das amostras

TODO #63:
- [x] **Corrigir Erro ao Atualizar Dados de Campanha**
  - Descrição: Ao tentar atualizar os dados de uma campanha e salvar, ocorre um erro. O problema persiste mesmo sem alterações nos dados. Necessário investigar e corrigir o erro no botão de salvar.

TODO:
- [x] **Adicionar Confirmação ao Remover Campanha**
  - Descrição: Atualmente, o botão de remover campanha não solicita confirmação do usuário. Implementar um diálogo de confirmação ("Tem certeza?") antes de prosseguir com a remoção. Além disso, é necessário adicionar um campo para que o usuário possa escrever o motivo da remoção.

TODO:
- [x] **Adicionar Confirmação ao Cancelar Campanha**
  - Descrição: Similar ao botão de remover, o botão de cancelar campanha também não solicita confirmação do usuário. Implementar um diálogo de confirmação ("Tem certeza?") antes de efetuar o cancelamento. Incluir um campo para escrita do motivo do cancelamento e adicionar a opção de descancelar a campanha.

TODO #64:
- [x] **Impedir Criação de Campanha com Dados de Uma Deletada**
  - Descrição: O sistema atualmente não permite a criação de uma nova campanha com os mesmos dados e nome de outra campanha que já foi deletada. Revisar e ajustar a lógica para permitir essa ação, garantindo que não haja conflitos ou inconsistências nos dados.