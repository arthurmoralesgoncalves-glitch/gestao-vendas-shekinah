# 🥤 Sistema de Gestão Financeira - Shekinah Açaí

Este projeto foi desenvolvido para resolver um problema real de gestão de vendas e controle de capital de giro. O software permite que microempreendedores organizem suas vendas diárias, separem os custos de reposição e identifiquem o lucro líquido real para reinvestimento.

## 🚀 Funcionalidades Principais
- **Fluxo de Caixa Diário:** Registro de vendas e gastos extras em tempo real.
- **Cálculo de Reinvestimento:** Separação automática entre valor de reposição (custo) e lucro líquido.
- **Histórico Mensal:** Persistência de dados em JSON para acompanhamento de longo prazo.
- **Relatórios em PDF:** Geração de balanços mensais detalhados com apenas um comando.
- **Interface Intuitiva:** Desenvolvida com `CustomTkinter` para uma experiência de uso moderna.

## 🛠️ Tecnologias Utilizadas
- **Python 3.x**
- **CustomTkinter:** Interface Gráfica (GUI).
- **FPDF:** Motor para geração de documentos PDF.
- **Matplotlib:** (Em implementação) Visualização de dados e gráficos de desempenho.
- **JSON:** Banco de dados leve para armazenamento local.

## 📊 Regra de Negócio Aplicada
O diferencial deste software é a aplicação de conceitos de administração financeira, onde cada venda é decomposta em:
1. **Faturamento Bruto**
2. **Custo de Mercadoria Vendida (CMV)** -> Retorna para o estoque.
3. **Margem de Contribuição** -> Lucro destinado a novos investimentos ou retirada.

## 📸 Como Executar
1. Instale as dependências: `pip install customtkinter fpdf matplotlib`
2. Execute o arquivo principal: `python vendas.py`
