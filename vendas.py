import customtkinter as ctk
import json
import os
from tkinter import messagebox
from datetime import datetime

# --- BLOCO DE SEGURANÇA: Tenta importar as bibliotecas externas ---
try:
    import matplotlib.pyplot as plt
    GRAFICOS_DISPONIVEIS = True
except ImportError:
    GRAFICOS_DISPONIVEIS = False

try:
    from fpdf import FPDF
    PDF_DISPONIVEL = True
except ImportError:
    PDF_DISPONIVEL = False
# ----------------------------------------------------------------

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class SistemaShekinah(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Shekinah Açaí - Gestão Pro")
        self.geometry("1000x850")
        
        # Arquivos de dados
        self.config_file = "estoque_shekinah.json"
        self.historico_file = "historico_mensal.json"
        self.ultimo_pdf_gerado = ""

        # Variáveis de controle
        self.produtos = []
        self.vendas_do_dia = []
        self.gastos_do_dia = []
        self.faturamento_dia = 0.0
        self.custo_reposicao_dia = 0.0
        self.lucro_liquido_dia = 0.0
        
        self.carregar_dados()

        # --- UI: Dashboard Superior ---
        self.label_titulo = ctk.CTkLabel(self, text="🌿 Shekinah Açaí - Controle de Fluxo", font=("Arial", 28, "bold"))
        self.label_titulo.pack(pady=15)

        self.frame_dash = ctk.CTkFrame(self, fg_color="#1e3d23")
        self.frame_dash.pack(pady=10, padx=20, fill="x")
        
        self.lbl_faturado = ctk.CTkLabel(self.frame_dash, text="Faturado: R$ 0.00", font=("Arial", 16))
        self.lbl_faturado.grid(row=0, column=0, padx=30, pady=20)
        
        self.lbl_lucro_liquido = ctk.CTkLabel(self.frame_dash, text="LUCRO LÍQUIDO: R$ 0.00", font=("Arial", 18, "bold"), text_color="#58d68d")
        self.lbl_lucro_liquido.grid(row=0, column=3, padx=30, pady=20)

        # --- Corpo Principal ---
        self.frame_corpo = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_corpo.pack(pady=10, padx=20, fill="both", expand=True)

        # Coluna Esquerda: Registros
        self.frame_esq = ctk.CTkFrame(self.frame_corpo)
        self.frame_esq.pack(side="left", fill="both", expand=True, padx=5)

        ctk.CTkLabel(self.frame_esq, text="Vender Item:", font=("Arial", 12, "bold")).pack(pady=5)
        self.combo_venda = ctk.CTkComboBox(self.frame_esq, values=[p['nome'] for p in self.produtos], width=250)
        self.combo_venda.pack(pady=5)
        self.btn_vender = ctk.CTkButton(self.frame_esq, text="Registrar Venda ✅", fg_color="green", command=self.registrar_venda)
        self.btn_vender.pack(pady=5)

        ctk.CTkLabel(self.frame_esq, text="\nRegistrar Gasto:", font=("Arial", 12, "bold")).pack(pady=5)
        self.entry_desc = ctk.CTkEntry(self.frame_esq, placeholder_text="Descrição (Ex: Gelo)")
        self.entry_desc.pack(pady=5)
        self.entry_val = ctk.CTkEntry(self.frame_esq, placeholder_text="Valor (Ex: 5,00)")
        self.entry_val.pack(pady=5)
        self.btn_gasto = ctk.CTkButton(self.frame_esq, text="Registrar Gasto 💸", fg_color="#e74c3c", command=self.registrar_gasto)
        self.btn_gasto.pack(pady=5)

        # Coluna Direita: Histórico do Dia
        self.lista_mov_txt = ctk.CTkTextbox(self.frame_corpo, width=400)
        self.lista_mov_txt.pack(side="right", fill="both", expand=True, padx=5)

        # --- Rodapé ---
        self.frame_footer = ctk.CTkFrame(self)
        self.frame_footer.pack(pady=20, padx=20, fill="x")

        self.btn_fechar_dia = ctk.CTkButton(self.frame_footer, text="FECHAR DIA", height=40, fg_color="#34495e", command=self.fechar_dia)
        self.btn_fechar_dia.grid(row=0, column=0, padx=10, pady=10)

        self.btn_gerar_pdf = ctk.CTkButton(self.frame_footer, text="GERAR RELATÓRIO MENSAL", height=40, fg_color="purple", command=self.fechar_mes)
        self.btn_gerar_pdf.grid(row=0, column=1, padx=10, pady=10)

        self.btn_abrir_pdf = ctk.CTkButton(self.frame_footer, text="ABRIR ÚLTIMO PDF", height=40, fg_color="#2e86c1", state="disabled", command=self.abrir_pdf_manual)
        self.btn_abrir_pdf.grid(row=0, column=2, padx=10, pady=10)
        
        self.btn_novo = ctk.CTkButton(self.frame_footer, text="+ Novo Produto", height=40, command=self.janela_cadastro_produto)
        self.btn_novo.grid(row=0, column=3, padx=10, pady=10)

        self.atualizar_dash()

    # --- LÓGICA DO SISTEMA ---
    
    def carregar_dados(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                d = json.load(f)
                self.produtos = d.get("produtos", [])
                self.vendas_do_dia = d.get("vendas_do_dia", [])
                self.gastos_do_dia = d.get("gastos_do_dia", [])
                self.faturamento_dia = d.get("faturamento_dia", 0.0)
                self.custo_reposicao_dia = d.get("custo_reposicao_dia", 0.0)
                self.lucro_liquido_dia = d.get("lucro_liquido_dia", 0.0)
        
        if not os.path.exists(self.historico_file):
            with open(self.historico_file, "w") as f:
                json.dump({"historico_diario": []}, f)

    def salvar_dados(self):
        with open(self.config_file, "w") as f:
            json.dump({
                "produtos": self.produtos,
                "vendas_do_dia": self.vendas_do_dia,
                "gastos_do_dia": self.gastos_do_dia,
                "faturamento_dia": self.faturamento_dia,
                "custo_reposicao_dia": self.custo_reposicao_dia,
                "lucro_liquido_dia": self.lucro_liquido_dia
            }, f, indent=4)

    def registrar_venda(self):
        nome = self.combo_venda.get()
        for p in self.produtos:
            if p['nome'] == nome:
                hora = datetime.now().strftime("%H:%M")
                self.vendas_do_dia.append({"tipo": "venda", "item": nome, "valor": p['venda'], "hora": hora})
                self.faturamento_dia += p['venda']
                self.custo_reposicao_dia += p['custo']
                self.recalcular_lucro()
                self.salvar_dados()
                self.atualizar_dash()
                break

    def registrar_gasto(self):
        desc = self.entry_desc.get()
        val_str = self.entry_val.get().replace(",", ".")
        if desc and val_str:
            try:
                valor = float(val_str)
                hora = datetime.now().strftime("%H:%M")
                self.gastos_do_dia.append({"tipo": "gasto", "item": desc, "valor": valor, "hora": hora})
                self.recalcular_lucro()
                self.salvar_dados()
                self.atualizar_dash()
                self.entry_desc.delete(0, 'end'); self.entry_val.delete(0, 'end')
            except: messagebox.showerror("Erro", "Valor inválido")

    def recalcular_lucro(self):
        total_gastos = sum(g['valor'] for g in self.gastos_do_dia)
        self.lucro_liquido_dia = self.faturamento_dia - self.custo_reposicao_dia - total_gastos

    def atualizar_dash(self):
        self.lbl_faturado.configure(text=f"Faturado: R$ {self.faturamento_dia:.2f}")
        self.lbl_lucro_liquido.configure(text=f"LUCRO LÍQUIDO: R$ {self.lucro_liquido_dia:.2f}")
        
        self.lista_mov_txt.configure(state="normal")
        self.lista_mov_txt.delete("1.0", "end")
        for m in self.vendas_do_dia + self.gastos_do_dia:
            cor = "🟢" if m['tipo'] == "venda" else "🔴"
            self.lista_mov_txt.insert("end", f"{cor} [{m['hora']}] {m['item']}: R$ {m['valor']:.2f}\n")
        self.lista_mov_txt.configure(state="disabled")
        self.combo_venda.configure(values=[p['nome'] for p in self.produtos])

    def fechar_dia(self):
        total_gastos = sum(g['valor'] for g in self.gastos_do_dia)
        msg = f"--- BALANÇO ---\nFaturamento: R$ {self.faturamento_dia:.2f}\nGastos: R$ {total_gastos:.2f}\nLucro: R$ {self.lucro_liquido_dia:.2f}\n\nFechar o dia?"
        
        if messagebox.askyesno("Confirmar", msg):
            resumo = {"data": datetime.now().strftime("%Y-%m-%d"), "faturamento": self.faturamento_dia, "lucro_liquido": self.lucro_liquido_dia}
            with open(self.historico_file, "r+") as f:
                h = json.load(f)
                h['historico_diario'].append(resumo)
                f.seek(0); json.dump(h, f, indent=4); f.truncate()
            
            self.vendas_do_dia, self.gastos_do_dia = [], []
            self.faturamento_dia, self.custo_reposicao_dia, self.lucro_liquido_dia = 0, 0, 0
            self.salvar_dados(); self.atualizar_dash()

    def fechar_mes(self):
        if not PDF_DISPONIVEL:
            messagebox.showerror("Erro", "Instale: pip install fpdf")
            return
        
        try:
            # Garante que lê o arquivo na mesma pasta do script
            caminho_hist = os.path.join(os.path.dirname(__file__), self.historico_file)
            
            if not os.path.exists(caminho_hist):
                messagebox.showwarning("Aviso", "Nenhum dado encontrado. Feche um dia primeiro!")
                return

            with open(caminho_hist, "r") as f:
                dados = json.load(f).get('historico_diario', [])

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, f"RELATORIO SHEKINAH - {datetime.now().strftime('%Y-%m')}", ln=True, align='C')
            pdf.ln(10)

            if not dados:
                pdf.set_font("Arial", size=12)
                pdf.cell(0, 10, "Historico vazio. Registre e feche um dia antes.", ln=True)
            else:
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(40, 10, "Data", 1)
                pdf.cell(40, 10, "Faturamento", 1)
                pdf.cell(40, 10, "Lucro Liq.", 1, ln=True)
                
                pdf.set_font("Arial", size=10)
                for d in dados:
                    pdf.cell(40, 10, str(d['data']), 1)
                    pdf.cell(40, 10, f"R$ {d['faturamento']:.2f}", 1)
                    pdf.cell(40, 10, f"R$ {d['lucro_liquido']:.2f}", 1, ln=True)

            nome_pdf = f"Relatorio_Shekinah_{datetime.now().strftime('%Y-%m')}.pdf"
            pdf.output(nome_pdf)
            self.ultimo_pdf_gerado = nome_pdf
            self.btn_abrir_pdf.configure(state="normal")
            messagebox.showinfo("Sucesso", "Relatório gerado com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar PDF: {e}")

    def abrir_pdf_manual(self):
        if self.ultimo_pdf_gerado: os.startfile(self.ultimo_pdf_gerado)

    def janela_cadastro_produto(self):
        # Orientação clara para o usuário
        dialog = ctk.CTkInputDialog(text="Formato: Nome, Custo, Venda\nExemplo: Açaí 500ml, 9.90, 25.00", title="Novo Produto")
        res = dialog.get_input()
        
        if res:
            try:
                # Divide pelos itens usando a vírgula como separador de colunas
                partes = res.split(",")
                if len(partes) != 3:
                    raise ValueError("Formato incorreto")
                
                nome = partes[0].strip()
                # Remove espaços e garante que o centavo seja ponto antes de converter para número
                custo = float(partes[1].strip().replace(",", "."))
                venda = float(partes[2].strip().replace(",", "."))
                
                self.produtos.append({"nome": nome, "custo": custo, "venda": venda})
                self.salvar_dados()
                self.atualizar_dash()
                messagebox.showinfo("Sucesso", f"Produto '{nome}' cadastrado corretamente!")
            except Exception as e:
                messagebox.showerror("Erro de Cadastro", "Use o formato: Nome, Custo, Venda\nExemplo: Açaí, 5.50, 15.00")

if __name__ == "__main__":
    app = SistemaShekinah()
    app.mainloop()