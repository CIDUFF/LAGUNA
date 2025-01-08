from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from decouple import config
import qrcode
import os
from simal.models import TabColeta, TabAmostra


from dotenv import load_dotenv

load_dotenv()


class etiquetas():
    def consulta(self, id):
        coleta = TabColeta.objects.get(id=id)
        os = coleta.ordem_servico
        responsavel = coleta.criado_por
        amostras = TabAmostra.objects.filter(id_coleta = coleta.id)
        setor  = coleta.id_setor
        campanha = coleta.id_campanha
        nome = coleta.nome
        data_coleta = coleta.data
    
        return os, responsavel, amostras, setor, campanha, nome, data_coleta
        

    def qr_code(self, id):
        try:
            site = config('SITE_URL')
            url = f"{site}/info_coleta/{id}"
            qr = qrcode.make(url)
            qr_path = f"media/qr_codes/{id}.png"
            qr.save(qr_path)
            return qr_path
        except Exception as e:
            print(f"Erro ao gerar QR Code: {e}")
            return None     
        
    def adicionar_etiqueta(c, qr_path, codigo, data, responsavel, x, y):
        try:
            c.drawImage(qr_path, x, y, width=20 * mm, height=20 * mm)
            c.drawString(x + 25 * mm, y + 15 * mm, f"Código: {codigo}")
            c.drawString(x + 25 * mm, y + 7 * mm, f"Data da coleta: {data}")
            c.drawString(x + 25 * mm, y + -1 * mm, f"Responsável: {responsavel}")
        except Exception as e:
            print(f"Erro ao adicionar etiqueta: {e}")

    def desenhar_linhas_tracejadas(
        c,
        largura_pagina,
        altura_pagina,
        largura_etiqueta,
        altura_etiqueta,
        espacamento_x,
        espacamento_y,
    ):
        try:
            c.setDash(1, 2)  # Define o estilo da linha tracejada

            # Linhas verticais
            x = 30 * mm + largura_etiqueta + espacamento_x / 2
            for _ in range(1):
                c.line(x, 0, x, altura_pagina)
                x += largura_etiqueta + espacamento_x

            # Linhas horizontais
            y = altura_pagina + 5 * mm - altura_etiqueta - espacamento_y / 2
            for _ in range(8):
                c.line(0, y, largura_pagina, y)
                y -= altura_etiqueta + espacamento_y

            c.setDash()  # Reseta o estilo da linha para o padrão
        except Exception as e:
            print(f"Erro ao desenhar linhas tracejadas: {e}")
            
    def gerar_etiquetas(self, codigos, data, responsavel, codigo_servico):
        try:
            largura_pagina, altura_pagina = A4
            pdf_path = os.path.join(
                "/home/marcus/projects/LAGUNA/media/pdf/",
                f"etiquetas_da_OS_{codigo_servico}.pdf",
            )
            try:
                c = canvas.Canvas(pdf_path, pagesize=A4)
            except Exception as e:
                print(f"Erro ao criar canvas do PDF: {e}")
                return None

            x_inicial = 10 * mm
            y_inicial = altura_pagina - 20 * mm
            largura_etiqueta = 50 * mm
            altura_etiqueta = 30 * mm
            espacamento_x = 50 * mm
            espacamento_y = 3 * mm
            x = x_inicial
            y = y_inicial
            etiquetas_por_pagina = 18
            contador_etiquetas = 0
            qr_paths = []

            try:
                self.desenhar_linhas_tracejadas(
                    c,
                    largura_pagina,
                    altura_pagina,
                    largura_etiqueta,
                    altura_etiqueta,
                    espacamento_x,
                    espacamento_y,
                )
            except Exception as e:
                print(f"Erro ao desenhar linhas tracejadas: {e}")

            for codigo in codigos:
                for i in range(1, 4):
                    codigo_modificado = f"{codigo}{i}"
                    try:
                        qr_path = self.gerar_qr_code(
                            codigo_modificado, data, responsavel, codigo_servico
                        )
                        if qr_path:
                            qr_paths.append(qr_path)
                            try:
                                self.adicionar_etiqueta(
                                    c, qr_path, codigo_modificado, data, responsavel, x, y
                                )
                            except Exception as e:
                                print(f"Erro ao adicionar etiqueta: {e}")
                            y -= altura_etiqueta + espacamento_y
                            contador_etiquetas += 1

                            if contador_etiquetas == 9:
                                x += largura_etiqueta + espacamento_x
                                y = y_inicial

                            if contador_etiquetas >= etiquetas_por_pagina:
                                c.showPage()
                                try:
                                    self.desenhar_linhas_tracejadas(
                                        c,
                                        largura_pagina,
                                        altura_pagina,
                                        largura_etiqueta,
                                        altura_etiqueta,
                                        espacamento_x,
                                        espacamento_y,
                                    )
                                except Exception as e:
                                    print(
                                        f"Erro ao desenhar linhas tracejadas em nova página: {e}"
                                    )
                                x = x_inicial
                                y = y_inicial
                                contador_etiquetas = 0
                    except Exception as e:
                        print(f"Erro ao gerar QR Code ou adicionar etiqueta: {e}")

            try:
                c.save()
            except Exception as e:
                print(f"Erro ao salvar o PDF: {e}")

            for path in qr_paths:
                try:
                    os.remove(path)
                except OSError as e:
                    print(f"Erro ao remover o arquivo {path}: {e}")
            return pdf_path
        except Exception as e:
            print(f"Erro ao gerar etiquetas: {e}")
            return None

        
        